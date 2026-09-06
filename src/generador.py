"""generacion de un shard, aqui esta el bucle que llena part-<wid>.jsonl.

aqui solo manejo el reloj, el buffer y el archivo.
"""

from datetime import datetime, timezone
from pathlib import Path

from esquema import formatear_evento, serializar_evento
from simulador import crear_activos

# los ~180 puntos de medicion del sitio reportan cada 15 segundos
DT_MS = 15_000
DT_S = DT_MS / 1000.0

# vacia el bufer cada 10.000 eventos, junto
# las lineas en ram y bajo de a lotes grandes para no pagar un write por evento
LOTE_BUFFER = 10_000


def _marcas_de_tiempo():
    """me va entregando las marcas de tiempo del reloj simulado, de a 15 segundos.

    el formato es el iso 8601 en utc con milisegundos y sufijo Z,
    nada de horas locales ni de datetime sin zona horaria.
    """
    t_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    seg_cache = -1
    prefijo = ""

    while True:
        seg, ms = divmod(t_ms, 1000)
        if seg != seg_cache:
            seg_cache = seg
            prefijo = datetime.fromtimestamp(seg, timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S."
            )
        yield f"{prefijo}{ms:03d}Z"
        t_ms += DT_MS


def worker_shard(wid, n_eventos, carpeta, semilla):
    """genera n_eventos y me los deja escritos en carpeta/part-<wid>.jsonl.

    1. le pido al reloj que hora es en el tick
    2. le pregunto a los 9 equipos que marcan
    3. guardo cada respuesta serializada en una lista
    4. cuando junto LOTE_BUFFER lineas, las escribo al archivo
    5. el reloj avanza solo 15 segundos
    6. repito hasta llegar a n_eventos lecturas

    cada logger.info toma un candado, arma un LogRecord y recorre los handlers, o
    sea entre tres y cinco veces mas lento, y encima los handlers no se
    comparten entre procesos
    """
    # el rng se instancia dentro del proceso hijo, uno por worker
    activos = crear_activos(semilla, wid)
    reloj = _marcas_de_tiempo()

    # el nombre part-{wid:03d}.jsonl es el del documento, un archivo
    # por worker es lo que hace que no haya colisiones de e/s a nivel de
    # software y el sistema operativo pueda planificar los descriptores como
    # le convenga, aprovechando el ancho de banda completo del disco
    ruta = Path(carpeta) / f"part-{wid:03d}.jsonl"
    buf = []
    escritos = 0

    # newline="\n" me deja el jsonl con saltos limpios 
    with open(ruta, "w", encoding="utf-8", newline="\n", buffering=4 * 1024 * 1024) as f:
        while escritos < n_eventos:
            timestamp_str = next(reloj)

            for activo in activos:
                for metadatos in activo.tick(DT_S):
                    if escritos >= n_eventos:      # corto aqui aunque el tick no termine
                        break
                    evento = formatear_evento(timestamp_str, metadatos, wid)
                    buf.append(serializar_evento(evento))
                    escritos += 1

                    # cuando junto el lote lo mando de una y vacio la lista
                    if len(buf) >= LOTE_BUFFER:
                        f.writelines(buf)
                        buf = []
                if escritos >= n_eventos:
                    break

        # lo que quedo sin alcanzar el lote completo
        if buf:
            f.writelines(buf)

    # lo unico que vuelve al proceso padre son estadisticas y no
    # datos, por eso el costo de pickle de esta arquitectura es practicamente
    # nulo. el stat va aqui afuera, con el archivo ya cerrado, si no me da
    # menos bytes de los que realmente escribi
    return {
        "worker_id": wid,
        "archivo": ruta.name,
        "eventos": escritos,
        "bytes": ruta.stat().st_size,
    }
