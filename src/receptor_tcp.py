"""receptor tcp del laboratorio de docker, el servicio que recibe y escribe.

el emisor genera los eventos y los manda por tcp, este los recibe y los deja
en disco. es la misma idea de la arquitectura b de lab1 2.3, un archivo por
conexion y ningun descriptor compartido, asi que no hay nada que sincronizar
entre conexiones:

    DATA_DIR/ingesta-<n>.jsonl      un archivo por cada conexion aceptada

los bytes se escriben tal como llegan, sin volver a parsear el json. el
emisor ya manda lineas jsonl completas y terminadas en \\n, aqui solo se cuentan
los \\n para saber cuantos eventos entraron.

no se acumula nada en memoria: cada read trae como maximo TAM_LECTURA bytes,
se escribe al archivo y se suelta. el streamreader de asyncio deja de leer del
socket cuando su buffer se llena, asi que si el disco va lento el emisor se
frena solo por tcp. es la misma contrapresion de lab1 2.2, pero la pone el
kernel. con eso el proceso cabe en el mem_limit de 1 GB aunque pasen 1,5 GB.

configuracion por variables de entorno:

    BIND_HOST   0.0.0.0     no 127.0.0.1, desde otro contenedor seria inalcanzable
    TCP_PORT    9009
    DATA_DIR    /app/data   en compose es un bind mount a ./data/raw del host
    N_PROCESOS  4           conexiones que se atienden a la vez

para correrlo: python -u src/receptor_tcp.py
"""

import asyncio
import os
import signal
import sys
import time
from pathlib import Path

# cada read del socket trae como maximo esto
TAM_LECTURA = 1024 * 1024

# el buffer del archivo, grande para no pagar un write por cada read
TAM_BUFFER_ARCHIVO = 4 * 1024 * 1024

# cada cuantos eventos totales se imprime el avance
CADA_AVANCE = 1_000_000

# 128 + 15, lo que docker muestra como apagado limpio tras un SIGTERM
SALIDA_SIGTERM = 143


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


def _preparar_data_dir(ruta):
    """crea DATA_DIR si no existe y comprueba que se pueda escribir en el.

    el contenedor corre como UID 10001. si el bind mount del host pertenece a
    otro usuario el problema aparece aqui, al arrancar, con un mensaje que dice
    que hacer, y no en la primera conexion con un traceback.
    """
    uid = os.getuid() if hasattr(os, "getuid") else "?"
    try:
        ruta.mkdir(parents=True, exist_ok=True)
        prueba = ruta / f".prueba-escritura-{os.getpid()}"
        prueba.write_bytes(b"")
        prueba.unlink()
    except PermissionError:
        sys.exit(
            f"error: sin permiso de escritura en DATA_DIR={ruta} (proceso con UID {uid}). "
            f"en el host dale la carpeta a ese usuario, por ejemplo: "
            f"sudo chown -R {uid} ./data/raw"
        )
    except OSError as e:
        sys.exit(f"error: no se pudo preparar DATA_DIR={ruta}: {e}")


class Receptor:
    """el estado del servidor: contadores, conexiones abiertas y archivos."""

    def __init__(self, data_dir, max_conexiones):
        self.data_dir = data_dir
        self.cupos = asyncio.Semaphore(max_conexiones)
        self.total = 0
        self.proximo_avance = CADA_AVANCE
        self.tareas = set()
        # los numeros de archivo siguen despues de los que ya existan, asi un
        # reinicio del receptor nunca pisa lo que se escribio antes
        existentes = [
            int(p.stem.split("-")[1])
            for p in data_dir.glob("ingesta-*.jsonl")
            if p.stem.split("-")[1].isdigit()
        ]
        self.siguiente = max(existentes) + 1 if existentes else 0
        if existentes:
            print(
                f"aviso: DATA_DIR ya tiene {len(existentes)} archivos ingesta-*.jsonl, "
                f"los nuevos parten en ingesta-{self.siguiente:03d}.jsonl",
                flush=True,
            )

    async def atender(self, reader, writer):
        """una conexion: lee lo que llegue y lo escribe en su propio archivo."""
        tarea = asyncio.current_task()
        self.tareas.add(tarea)
        peer = writer.get_extra_info("peername")
        try:
            # sin aviso de "en espera": aqui todavia no se sabe si la conexion
            # trae datos, y los healthchecks de compose lo llenarian el log
            async with self.cupos:
                await self._recibir(reader, writer, peer)
        finally:
            self.tareas.discard(tarea)
            writer.close()

    async def _recibir(self, reader, writer, peer):
        """recibe una conexion y la escribe en su ingesta-<n>.jsonl.

        el archivo se abre recien con el primer bloque de datos. el
        healthcheck de compose abre y cierra una conexion cada 5 s sin mandar
        nada, y si el archivo se abriera al aceptar, cada chequeo dejaria un
        ingesta-NNN.jsonl vacio y dos lineas de log. asi una conexion sin datos
        no crea archivo, no gasta numero y no escribe nada en el log, y los
        ingesta-NNN.jsonl de las conexiones reales quedan correlativos.
        """
        f = None
        n = None
        ruta = None
        lineas = 0
        bytes_rx = 0
        cola = 0          # bytes despues del ultimo \n, una linea aun incompleta
        inicio = time.perf_counter()
        motivo = "el emisor cerro la conexion"

        try:
            while True:
                datos = await reader.read(TAM_LECTURA)
                if not datos:                            # eof, shutdown(SHUT_WR)
                    break
                if f is None:
                    # primer bloque con datos: recien aqui la conexion es real
                    n = self.siguiente
                    self.siguiente += 1
                    ruta = self.data_dir / f"ingesta-{n:03d}.jsonl"
                    f = open(ruta, "wb", buffering=TAM_BUFFER_ARCHIVO)
                    print(f"conexion {n} desde {peer} -> {ruta.name}", flush=True)
                f.write(datos)
                bytes_rx += len(datos)
                nuevas = datos.count(b"\n")
                if nuevas:
                    lineas += nuevas
                    cola = len(datos) - 1 - datos.rindex(b"\n")
                    self._sumar(nuevas)
                else:
                    cola += len(datos)
        except asyncio.CancelledError:
            motivo = "cierre por senal"
            raise
        except (ConnectionError, OSError) as e:
            motivo = f"error de conexion: {e}"
        finally:
            # conexion sin datos, como el healthcheck: no hay archivo ni log
            if f is not None:
                self._cerrar_archivo(f, cola)
                segundos = time.perf_counter() - inicio
                print(
                    f"conexion {n} cerrada ({motivo}): {lineas:,} eventos, "
                    f"{bytes_rx / 1e6:,.1f} MB en {segundos:.2f} s -> {ruta.name}",
                    flush=True,
                )
                if cola:
                    print(
                        f"  aviso: la conexion {n} termino a mitad de una linea, "
                        f"se descartaron {cola} bytes incompletos para que el archivo "
                        f"quede con lineas json validas",
                        flush=True,
                    )

    def _sumar(self, nuevas):
        self.total += nuevas
        if self.total >= self.proximo_avance:
            print(f"avance: {self.total:,} eventos recibidos", flush=True)
            while self.proximo_avance <= self.total:
                self.proximo_avance += CADA_AVANCE

    @staticmethod
    def _cerrar_archivo(f, cola):
        """flush + fsync y cierre. si quedo una linea a medias se corta."""
        f.flush()
        if cola:
            f.truncate(f.tell() - cola)
        os.fsync(f.fileno())
        f.close()


async def _principal():
    host = os.environ.get("BIND_HOST", "0.0.0.0")
    puerto = _entero("TCP_PORT", 9009)
    max_conexiones = _entero("N_PROCESOS", 4)
    data_dir = Path(os.environ.get("DATA_DIR", "/app/data"))
    _preparar_data_dir(data_dir)

    receptor = Receptor(data_dir, max_conexiones)
    parar = asyncio.Event()
    loop = asyncio.get_running_loop()
    senal_recibida = []

    def al_recibir(sig):
        if not senal_recibida:
            senal_recibida.append(sig)
            loop.call_soon_threadsafe(parar.set)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, al_recibir, sig)
        except NotImplementedError:
            # windows no tiene add_signal_handler. en docker (linux) no se usa
            # esta rama, es solo para poder probar con ctrl+c en local
            signal.signal(sig, lambda s, _f: al_recibir(signal.Signals(s)))

    try:
        servidor = await asyncio.start_server(
            receptor.atender, host, puerto, limit=TAM_LECTURA
        )
    except OSError as e:
        sys.exit(f"error: no se pudo escuchar en {host}:{puerto}: {e}")

    print(
        f"receptor escuchando en {host}:{puerto}, DATA_DIR={data_dir}, "
        f"hasta {max_conexiones} conexiones a la vez",
        flush=True,
    )

    # se queda aqui indefinidamente, aunque nadie se conecte
    await parar.wait()

    nombre = senal_recibida[0].name
    print(f"{nombre} recibido: cerrando sockets y haciendo flush del .jsonl", flush=True)

    # 1. deja de aceptar conexiones nuevas
    servidor.close()
    # 2. corta las conexiones abiertas. lo que ya se leyo esta en el archivo;
    #    el finally de cada una hace flush + fsync y cierra
    for tarea in list(receptor.tareas):
        tarea.cancel()
    await asyncio.gather(*receptor.tareas, return_exceptions=True)
    await servidor.wait_closed()

    print(f"receptor detenido: {receptor.total:,} eventos recibidos en total", flush=True)
    return SALIDA_SIGTERM


if __name__ == "__main__":
    sys.exit(asyncio.run(_principal()))
