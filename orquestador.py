"""reparto del trabajo entre workers y medicion de cada configuracion.

esto es lo que produce la curva de escalabilidad  de
1, 2, 4, 8 y 16 workers manteniendo fijo el total de eventos. tambien
sale de aqui el punto 4, eventos por segundo y bytes escritos por corrida.

uso ProcessPoolExecutor y no hilos a proposito. el trabajo del
generador es aritmetica, formateo y serializacion, o sea bytecode puro y
cpu-bound, y contra el GIL ocho hilos se turnan el mismo nucleo. cada proceso
hijo en cambio es un interprete independiente con su propio GIL, ahi el
paralelismo es real. la medicion de hilos contra procesos vive en bench/.

el generador no sabe nada de esto, el solo llena su shard.
"""

import time
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
    wid, n_eventos, carpeta, semilla = args
    return worker_shard(wid, n_eventos, Path(carpeta), semilla)


def _armar_tareas(n_workers, total_eventos, carpeta, semilla):
    """los argumentos de cada worker, ya con su cupo asignado.

    la carpeta la mando como str y no como Path porque esto viaja pickleado
    al proceso hijo, lab1 1.3 avisa que todo dato que cruce entre procesos se
    serializa, asi que prefiero que cruce lo mas simple posible. igual aqui el
    peaje es minimo, van cuatro valores por worker y no diez millones de
    eventos, que es justamente la ventaja de la opcion b.
    """
    cupos = repartir(total_eventos, n_workers)
    return cupos, [(wid, cupos[wid], str(carpeta), semilla) for wid in range(n_workers)]


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


def correr_config(n_workers, total_eventos, raiz, semilla, paralelo):
    """corre una configuracion completa y devuelve sus metricas.

    cada configuracion escribe en su propia subcarpeta w<n>, si no las cinco
    corridas se pisarian el mismo part-000.jsonl y no podria comparar tamanos.
    """
    carpeta = Path(raiz) / f"w{n_workers:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)

    cupos, tareas = _armar_tareas(n_workers, total_eventos, carpeta, semilla)
    stats, transcurrido = _ejecutar(tareas, n_workers, paralelo)

    eventos = sum(s["eventos"] for s in stats)
    return {
        "workers": n_workers,
        "eventos_por_worker": cupos[0],
        "eventos": eventos,
        "bytes": sum(s["bytes"] for s in stats),
        "segundos": round(transcurrido, 2),
        "eventos_s": round(eventos / transcurrido),
    }
