"""emisor tcp del laboratorio de docker, el servicio que genera y envia.

hace lo mismo que generador.worker_shard, pero en vez de escribir el shard en
disco lo manda por socket al receptor. cada worker es un proceso con su propio
socket y reutiliza generador.iter_eventos tal cual, con el mismo reparto por
activos, asi que la suma de todos los workers da exactamente TOTAL_EVENTOS.

junto BATCH_SIZE lineas y las mando con un solo sendall, por la misma razon
que worker_shard junta LOTE_BUFFER antes de writelines: no pagar una llamada
al sistema por evento.

configuracion por variables de entorno:

    TCP_HOST       ingestor-tcp   nombre dns del receptor en la red de compose
    TCP_PORT       9009
    TOTAL_EVENTOS  10000000       total del dataset
    N_PROCESOS     4              procesos emisores
    BATCH_SIZE     50000          lineas por envio
    SEMILLA        42             reproducibilidad

sale con 0 si la suma de eventos enviados es exactamente TOTAL_EVENTOS y el
receptor confirmo cada conexion, y con 1 si no.

para correrlo: python -u src/emisor_tcp.py
"""

import os
import socket
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from generador import iter_eventos

INTENTOS_CONEXION = 10
ESPERA_INICIAL_S = 0.5
ESPERA_MAXIMA_S = 8.0

# cuanto espero a que el receptor cierre su lado despues del shutdown. ese
# cierre es la confirmacion de que ya hizo flush + fsync del archivo
ESPERA_CONFIRMACION_S = 60.0

# cada cuantos eventos por worker se imprime el avance
CADA_AVANCE = 1_000_000


def _entero(nombre, defecto, minimo=1):
    """lee una variable de entorno entera y falla temprano si no sirve."""
    crudo = os.environ.get(nombre, str(defecto))
    try:
        valor = int(crudo)
    except ValueError:
        sys.exit(f"error: {nombre}={crudo!r} no es un entero")
    if valor < minimo:
        sys.exit(f"error: {nombre}={valor} tiene que ser >= {minimo}")
    return valor


def _conectar(host, puerto, wid):
    """abre el socket, reintentando con espera creciente.

    en compose el emisor puede arrancar antes que el receptor este escuchando,
    por eso no me rindo al primer ConnectionRefused.
    """
    espera = ESPERA_INICIAL_S
    for intento in range(1, INTENTOS_CONEXION + 1):
        try:
            sock = socket.create_connection((host, puerto), timeout=10)
            sock.settimeout(None)    # sendall bloquea si el receptor se frena
            return sock
        except OSError as e:
            if intento == INTENTOS_CONEXION:
                raise ConnectionError(
                    f"worker {wid}: no se pudo conectar a {host}:{puerto} "
                    f"tras {INTENTOS_CONEXION} intentos ({e})"
                ) from e
            print(
                f"worker {wid}: intento {intento}/{INTENTOS_CONEXION} fallo ({e}), "
                f"reintento en {espera:.1f} s",
                flush=True,
            )
            time.sleep(espera)
            espera = min(espera * 2, ESPERA_MAXIMA_S)


def _esperar_confirmacion(sock):
    """despues del SHUT_WR espero el eof del receptor.

    el receptor cierra su lado solo cuando ya hizo flush + fsync del archivo,
    asi que el eof confirma que lo enviado quedo en disco.
    """
    sock.settimeout(ESPERA_CONFIRMACION_S)
    try:
        while sock.recv(4096):
            pass
        return True
    except (socket.timeout, OSError):
        return False


def trabajador(wid, host, puerto, total, n_procesos, lote, semilla):
    """un proceso emisor: genera su parte y la manda por su propio socket.

    lo unico que vuelve al padre son estadisticas, igual que en worker_shard.
    """
    sock = _conectar(host, puerto, wid)
    enviados = 0
    bytes_tx = 0
    proximo_avance = CADA_AVANCE
    buf = []
    inicio = time.perf_counter()
    try:
        for linea in iter_eventos(total, semilla, wid, n_procesos):
            buf.append(linea)
            if len(buf) >= lote:
                datos = "".join(buf).encode("utf-8")
                sock.sendall(datos)
                enviados += len(buf)
                bytes_tx += len(datos)
                buf = []
                if enviados >= proximo_avance:
                    print(f"worker {wid}: {enviados:,} eventos enviados", flush=True)
                    proximo_avance += CADA_AVANCE
        if buf:
            datos = "".join(buf).encode("utf-8")
            sock.sendall(datos)
            enviados += len(buf)
            bytes_tx += len(datos)

        # aviso de termino, el receptor ve eof y cierra su archivo
        sock.shutdown(socket.SHUT_WR)
        confirmado = _esperar_confirmacion(sock)
    finally:
        sock.close()

    return {
        "worker_id": wid,
        "eventos": enviados,
        "bytes": bytes_tx,
        "segundos": time.perf_counter() - inicio,
        "confirmado": confirmado,
    }


def main():
    host = os.environ.get("TCP_HOST", "ingestor-tcp")
    puerto = _entero("TCP_PORT", 9009)
    total = _entero("TOTAL_EVENTOS", 10_000_000)
    n_procesos = _entero("N_PROCESOS", 4)
    lote = _entero("BATCH_SIZE", 50_000)
    semilla = _entero("SEMILLA", 42, minimo=0)

    nucleos = os.cpu_count() or 1
    if n_procesos > nucleos:
        print(
            f"aviso: N_PROCESOS={n_procesos} es mas que los {nucleos} nucleos del "
            f"equipo, los procesos de sobra se van a turnar la cpu",
            flush=True,
        )

    print(
        f"emisor -> {host}:{puerto} | {total:,} eventos | {n_procesos} procesos | "
        f"lotes de {lote:,} lineas | semilla {semilla}",
        flush=True,
    )

    inicio = time.perf_counter()
    resultados = []
    fallos = 0
    with ProcessPoolExecutor(max_workers=n_procesos) as pool:
        futuros = [
            pool.submit(trabajador, wid, host, puerto, total, n_procesos, lote, semilla)
            for wid in range(n_procesos)
        ]
        for futuro in as_completed(futuros):
            try:
                r = futuro.result()
            except Exception as e:
                fallos += 1
                print(f"error en un worker: {e}", flush=True)
                continue
            resultados.append(r)
            estado = "confirmado" if r["confirmado"] else "SIN confirmacion del receptor"
            print(
                f"worker {r['worker_id']} termino: {r['eventos']:,} eventos en "
                f"{r['segundos']:.2f} s ({estado})",
                flush=True,
            )
    segundos = time.perf_counter() - inicio

    enviados = sum(r["eventos"] for r in resultados)
    sin_confirmar = sum(1 for r in resultados if not r["confirmado"])
    print(
        f"\nresumen: {enviados:,} eventos en {segundos:.2f} s "
        f"({enviados / segundos:,.0f} eventos/s, "
        f"{sum(r['bytes'] for r in resultados) / 1e6:,.1f} MB)",
        flush=True,
    )

    if fallos or enviados != total or sin_confirmar:
        print(
            f"ERROR: se esperaban {total:,} eventos y se enviaron {enviados:,} "
            f"({fallos} workers fallaron, {sin_confirmar} sin confirmacion)",
            flush=True,
        )
        return 1
    print(f"OK: se enviaron exactamente {total:,} eventos", flush=True)
    return 0


if __name__ == "__main__":
    # obligatorio con ProcessPoolExecutor, con spawn cada hijo vuelve a
    # importar este modulo y sin esto lanzaria su propio pool
    sys.exit(main())
