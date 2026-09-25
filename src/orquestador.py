"""reparto del trabajo entre workers y medicion de cada configuracion.

esto es lo que produce la curva de escalabilidad  de
1, 2, 4, 8 y 16 workers manteniendo fijo el total de eventos. tambien
sale de aqui el punto 4, eventos por segundo y bytes escritos por corrida.

correr_config es una corrida suelta. medir_configuracion la repite, descarta
el warm-up y devuelve la mediana con el throughput y los MB/s efectivos.

uso ProcessPoolExecutor y no hilos a proposito. el trabajo del
generador es aritmetica, formateo y serializacion, o sea bytecode puro y
cpu-bound, y contra el GIL ocho hilos se turnan el mismo nucleo. cada proceso
hijo en cambio es un interprete independiente con su propio GIL, ahi el
paralelismo es real. la medicion de hilos contra procesos vive en bench/.

el generador no sabe nada de esto, el solo llena su shard.
"""

import json
import time
import statistics
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from generador import worker_shard


def repartir(total, n_workers):
    """reparte total entre n_workers sin perder ni inventar eventos.

    el resto se lo llevan los primeros workers, de a uno. asi la suma de la
    lista siempre da exactamente total, aunque no sea divisible. esto es lo
    que sostiene el requisito duro de lab1 4.6, un dataset con menos de 10
    millones de registros deja la calidad del dataset en cero.
    ej: repartir(10, 4) -> [3, 3, 2, 2]
    """
    base, resto = divmod(total, n_workers)
    return [base + (1 if wid < resto else 0) for wid in range(n_workers)]


def _tarea(args):
    """envoltorio para poder mandar worker_shard al pool de procesos."""
    wid, n_eventos, carpeta, semilla, n_workers = args
    return worker_shard(wid, n_eventos, Path(carpeta), semilla, n_workers)


def _armar_tareas(n_workers, total_eventos, carpeta, semilla):
    """los argumentos de cada worker.

    cada worker recibe el TOTAL del dataset y n_workers, no un cupo: el reparto
    es por activos (ver generador.iter_eventos), asi que cuantos eventos le
    tocan a cada uno sale de cuantos puntos de medicion simula. repartir() ya
    no se usa aqui porque partir el total en partes iguales hacia que todos
    los workers simularan el mismo periodo con los mismos sensores.

    la carpeta la mando como str y no como Path porque esto viaja pickleado
    al proceso hijo, lab1 1.3 avisa que todo dato que cruce entre procesos se
    serializa, asi que prefiero que cruce lo mas simple posible. igual aqui el
    peaje es minimo, van cuatro valores por worker y no diez millones de
    eventos, que es justamente la ventaja de la opcion b.
    """
    return [
        (wid, total_eventos, str(carpeta), semilla, n_workers)
        for wid in range(n_workers)
    ]


def _ejecutar(tareas, n_workers, paralelo):
    """corre las tareas y me devuelve los stats junto con lo que tardaron.

    con un solo worker no levanto el pool, el costo de crear el proceso me
    ensuciaria justo la corrida que uso de T(1) para el speedup de lab1 4.4
    punto 3. ese costo de arranque con spawn es ademas uno de los candidatos
    que el documento pide nombrar cuando la curva se aplana.
    """
    inicio = time.perf_counter()
    if paralelo and n_workers > 1:
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            stats = list(pool.map(_tarea, tareas))
    else:
        stats = [_tarea(t) for t in tareas]
    return stats, time.perf_counter() - inicio


def _primera_y_ultima_linea(ruta):
    """la primera y la ultima linea de un .jsonl sin leer el archivo entero.

    la ultima se saca leyendo solo el final del archivo, con 1,5 GB en disco
    recorrerlo completo para mirar un timestamp seria absurdo.
    """
    with open(ruta, "rb") as f:
        primera = f.readline()
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 4096))
        ultima = f.read().splitlines()[-1]
    return primera, ultima


def _dias_simulados(carpeta):
    """dias que cubre el dataset, sacados de los timestamps reales escritos.

    toma el timestamp mas temprano y el mas tardio entre todos los shards de
    la carpeta. no asume nada de como se repartio el tiempo entre workers: si
    todos simularon el mismo periodo, esto lo va a mostrar tal cual.
    """
    tiempos = []
    for ruta in Path(carpeta).glob("*.jsonl"):
        if ruta.stat().st_size == 0:
            continue
        for linea in _primera_y_ultima_linea(ruta):
            ts = json.loads(linea)["timestamp"]
            tiempos.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
    if not tiempos:
        return 0.0
    return (max(tiempos) - min(tiempos)).total_seconds() / 86400


def correr_config(n_workers, total_eventos, raiz, semilla, paralelo):
    """corre una configuracion completa y devuelve sus metricas.

    cada configuracion escribe en su propia subcarpeta w<n>, si no las cinco
    corridas se pisarian el mismo part-000.jsonl y no podria comparar tamanos.
    """
    carpeta = Path(raiz) / f"w{n_workers:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)

    tareas = _armar_tareas(n_workers, total_eventos, carpeta, semilla)
    stats, transcurrido = _ejecutar(tareas, n_workers, paralelo)
    eventos = sum(s["eventos"] for s in stats)

    # los dias salen de los timestamps reales y solo se usan para el promedio,
    # se leen despues de cronometrar asi no ensucian el tiempo de la corrida
    dias = _dias_simulados(carpeta)
    eventos_dia = eventos / dias if dias > 0 else 0.0
    return {
        "workers": n_workers,
        # el reparto por activos no queda parejo, se reporta el worker mas
        # cargado, que es el que marca el tiempo total de la corrida
        "eventos_por_worker": max(s["eventos"] for s in stats),
        "eventos": eventos,
        "bytes": sum(s["bytes"] for s in stats),
        "segundos": round(transcurrido, 2),
        "eventos_s": round(eventos / transcurrido),
        "eventos_dia": eventos_dia,
    }


def medir_configuracion(
    n_workers, total_eventos, raiz, semilla, paralelo, repeticiones=4
):
    """repite una configuracion varias veces y se queda con la MEDIANA.

    lab1 4.4 pide descartar la primera corrida, la de warm-up, donde el disco
    todavia no tiene la carpeta en cache y el pool paga el arranque en frio con
    spawn. de las corridas restantes se toma la mediana y no el promedio, que
    aguanta mejor un outlier puntual del planificador del sistema operativo.

    sobre ese tiempo mediano recien se calculan el throughput en eventos/s y la
    transferencia efectiva en MB/s del punto 4. correr_config ya hace todo el
    trabajo pesado, aqui solo se agrega la capa de repeticion y estadistico.
    """
    tiempos = []
    ultimo = None
    for intento in range(repeticiones):
        r = correr_config(n_workers, total_eventos, raiz, semilla, paralelo)
        tiempos.append(r["segundos"])
        ultimo = r
        print(
            f"  worker {n_workers:>2} | corrida {intento + 1}/{repeticiones} | "
            f"{r['segundos']:.4f} s"
        )

    # la primera corrida se descarta siempre, es el warm-up
    tiempo_mediano = statistics.median(tiempos[1:])

    eventos = ultimo["eventos"]
    return {
        "workers": n_workers,
        "eventos_totales": eventos,
        "eventos_por_worker": ultimo["eventos_por_worker"],
        "eventos_dia": ultimo["eventos_dia"],
        "tiempo": tiempo_mediano,
        "throughput": eventos / tiempo_mediano,
        "transferencia_MB_s": (ultimo["bytes"] / (1024 * 1024)) / tiempo_mediano,
    }
