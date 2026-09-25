"""generacion de eventos: el nucleo iter_eventos y el worker que llena el shard.

    iter_eventos     el bucle puro, reloj + activos + serializacion, sin disco
    generar_eventos  lo consume en memoria, carga cpu-bound para los experimentos
    worker_shard     le agrega encima el buffer y el archivo part-<wid>.jsonl
"""

from datetime import datetime, timezone
from pathlib import Path

from esquema import linea_evento
from simulador import crear_activos, primeros_puntos, puntos_por_tick

# los ~180 puntos de medicion del sitio reportan cada 15 segundos
DT_MS = 15_000
DT_S = DT_MS / 1000.0

# el origen del reloj simulado, 2026-01-01T00:00:00.000Z en milisegundos.
#
# esto era datetime.now() y ahi estaba el problema. main.py promete que con la
# misma semilla dos ejecuciones producen datasets identicos, y no se cumplia:
# el rng si era reproducible, los value salian iguales, pero el reloj arrancaba
# en la hora de pared y esa parte no la fija ninguna semilla. como el timestamp
# es el primer campo de cada linea, las 10 millones de lineas salian distintas
# en cada corrida. el hallazgo completo esta en docs/hallazgos_reloj.md.
#
# con un origen constante el dataset vuelve a ser reproducible, y de paso la
# epoca cae en un segundo entero, asi los milisegundos quedan en .000 y el
# reloj es honestamente discreto en vez de arrastrar un offset arbitrario
# heredado del instante en que se lanzo el proceso.
EPOCA_SIMULACION_MS = 1_767_225_600_000

# vacia el bufer cada 10.000 eventos, junto
# las lineas en ram y bajo de a lotes grandes para no pagar un write por evento
LOTE_BUFFER = 10_000

# el formato de la fecha, sin la hora. la hora se arma con aritmetica, ver
# _marcas_de_tiempo
_FORMATO_FECHA = "%Y-%m-%dT"
_SEGUNDOS_POR_DIA = 86_400


def _marcas_de_tiempo(inicio_ms=None):
    """me va entregando las marcas de tiempo del reloj simulado, de a 15 segundos.

    el formato es el iso 8601 en utc con milisegundos y sufijo Z,
    nada de horas locales ni de datetime sin zona horaria.

    la version anterior llamaba a datetime.fromtimestamp().strftime() en CADA
    tick. tenia una cache para evitarlo, la rama seg != seg_cache, pero
    bench/verificacion_reloj.py probo que esa cache acertaba el 0% de las
    veces: el paso son 15 segundos enteros, asi que el segundo cambia siempre y
    la rama de reutilizacion era inalcanzable.

    aca la cache se conserva pero ahora acierta, y se le suma una segunda por
    encima:

      - la de segundo sigue existiendo y sirve si algun dia DT_MS baja de 1000,
        que es el unico caso en que varios ticks caen dentro del mismo segundo
      - la de dia es la que rinde hoy: el strftime pasa de una vez por tick a
        una vez por dia simulado, o sea una cada 5.760 ticks a 15 segundos. la
        hora, el minuto y el segundo salen de dos divmod, aritmetica entera que
        no construye ningun datetime

    inicio_ms queda como parametro para poder anclar el reloj en otro instante
    desde un test o un experimento, pero el valor por defecto es constante a
    proposito, es lo que sostiene la reproducibilidad del dataset.
    """
    if inicio_ms is None:
        inicio_ms = EPOCA_SIMULACION_MS

    t_ms = int(inicio_ms)
    seg_cache = -1
    dia_cache = -1
    fecha = ""
    prefijo = ""

    while True:
        seg, ms = divmod(t_ms, 1000)

        if seg != seg_cache:
            seg_cache = seg
            dia, resto = divmod(seg, _SEGUNDOS_POR_DIA)

            if dia != dia_cache:
                dia_cache = dia
                fecha = datetime.fromtimestamp(
                    dia * _SEGUNDOS_POR_DIA, timezone.utc
                ).strftime(_FORMATO_FECHA)

            horas, sobra = divmod(resto, 3_600)
            minutos, segundos = divmod(sobra, 60)
            prefijo = f"{fecha}{horas:02d}:{minutos:02d}:{segundos:02d}."

        yield f"{prefijo}{ms:03d}Z"
        t_ms += DT_MS


def iter_eventos(n_eventos, semilla, worker_id, n_workers=1):
    """el nucleo de un worker, va largando lineas jsonl ya serializadas.

    n_eventos es el total del DATASET, no el cupo de este worker.

    1. le pido al reloj que hora es en el tick
    2. le pregunto a mis activos que marcan
    3. serializo cada respuesta y la entrego
    4. el reloj avanza solo 15 segundos
    5. repito hasta llegar al final del dataset

    reparto por activos (punto 3): todos los workers recorren el mismo reloj
    desde EPOCA_SIMULACION_MS, pero cada uno solo con sus activos, asi que
    ningun sensor_id aparece en dos workers y cada serie es continua.

    el corte: cada lectura tiene un indice global, tick * puntos_por_tick() +
    su posicion en el tick. se emite solo si ese indice es < n_eventos. es la
    misma regla que antes con un solo worker (cortar a mitad del ultimo tick),
    pero ahora vale igual para cualquier n_workers, y la suma de todos los
    shards da exactamente n_eventos, el volumen minimo de lab1 4.6.

    no toca disco ni sabe de archivos. worker_shard le pone encima el buffer y
    el archivo, y bench/experimento_gil.py lo consume en memoria para medir
    cpu puro.
    """
    # el rng se instancia dentro del proceso hijo, uno por worker
    activos = crear_activos(semilla, worker_id, n_workers)
    posiciones = primeros_puntos(worker_id, n_workers)
    por_tick = puntos_por_tick()
    reloj = _marcas_de_tiempo()

    # el nombre queda en una local antes del bucle. son 10 millones de
    # iteraciones y cada una se ahorra la busqueda del global del modulo
    armar_linea = linea_evento
    pares = list(zip(activos, posiciones))

    base = 0                                   # indice global del tick actual
    while base < n_eventos:
        timestamp_str = next(reloj)
        # en todos los ticks menos el ultimo, cada lectura entra entera
        if base + por_tick <= n_eventos:
            for activo, _ in pares:
                for metadatos in activo.tick(DT_S):
                    yield armar_linea(timestamp_str, metadatos, worker_id)
        else:
            # ultimo tick: solo lo que cae antes del corte global
            limite = n_eventos - base
            for activo, pos in pares:
                if pos >= limite:
                    break                      # posiciones van en orden
                for j, metadatos in enumerate(activo.tick(DT_S)):
                    if pos + j >= limite:
                        break
                    yield armar_linea(timestamp_str, metadatos, worker_id)
        base += por_tick


def generar_eventos(n_eventos, semilla=42, worker_id=0, n_workers=1):
    """genera en memoria la parte de este worker y devuelve cuantos produjo,
    sin escribir nada. con n_workers=1 son n_eventos.

    es la carga cpu-bound de bench/experimento_gil.py: sin e/s de disco que lo
    tape, el efecto del GIL sobre los hilos queda a la vista.
    """
    return sum(1 for _ in iter_eventos(n_eventos, semilla, worker_id, n_workers))


def worker_shard(wid, n_eventos, carpeta, semilla, n_workers=1):
    """genera su parte del dataset y la deja escrita en carpeta/part-<wid>.jsonl.

    n_eventos es el total del dataset; cuantos le tocan a este worker lo decide
    el reparto por activos de iter_eventos, y vuelve en "eventos".

    aqui solo vive el archivo y el buffer: junto LOTE_BUFFER lineas en ram y las
    bajo de una con writelines para no pagar un write por evento. la generacion
    en si la hace iter_eventos.

    el nombre part-{wid:03d}.jsonl es el del documento, un archivo por worker es
    lo que evita las colisiones de e/s a nivel de software y deja que el sistema
    operativo planifique los descriptores aprovechando el ancho de banda
    completo del disco.
    """
    # newline="\n" me deja el jsonl con saltos limpios
    ruta = Path(carpeta) / f"part-{wid:03d}.jsonl"
    buf = []
    escritos = 0

    with open(ruta, "w", encoding="utf-8", newline="\n", buffering=4 * 1024 * 1024) as f:
        for linea in iter_eventos(n_eventos, semilla, wid, n_workers):
            buf.append(linea)
            escritos += 1

            # cuando junto el lote lo mando de una y vacio la lista
            if len(buf) >= LOTE_BUFFER:
                f.writelines(buf)
                buf = []

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
