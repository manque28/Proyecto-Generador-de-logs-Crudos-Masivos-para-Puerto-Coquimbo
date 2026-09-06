from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def repartir(total, n_workers):
    """Reparte todos los eventos entre los workers sin perder ninguno."""
    base, resto = divmod(total, n_workers)
    return [base + (1 if wid < resto else 0) for wid in range(n_workers)]

def _tarea(args):
    """Ejecuta un shard en un proceso independiente."""
    from src.main import worker_shard

    wid, n_eventos, carpeta, semilla = args
    return worker_shard(
        wid=wid,
        n_eventos=n_eventos,
        carpeta=Path(carpeta),
        semilla=semilla,
    )


def ejecutar_procesos(n_workers, total_eventos, carpeta, semilla):
    """
    Ejecuta la generación mediante ProcessPoolExecutor.
    
    Cada worker recibe su propio cupo de eventos y escribe
    exclusivamente en su propio archivo part-XXX.jsonl.
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    cupos = repartir(total_eventos, n_workers)

    tareas = [
        (wid, cupos[wid], str(carpeta), semilla)
        for wid in range(n_workers)
    ]

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        resultados = list(executor.map(_tarea, tareas))

    return resultados
