"""arquitectura B concretada: un proceso por worker y un archivo por worker.

es la opcion en la que se enfoca el proyecto. cada worker escribe su propio
part-<wid>.jsonl y nunca comparte descriptor con otro, asi no hay contencion de
e/s a nivel de software y el paralelismo entre procesos es real, cada uno con su
GIL.

la logica ya vive en orquestador.py (reparto y pool) y en generador.py (el
bucle del worker). este modulo solo expone el punto de entrada ejecutar_procesos
que pide el enunciado, sin repetir el reparto ni el ProcessPoolExecutor.
"""

from pathlib import Path

# _armar_tareas y _ejecutar son internos de orquestador, pero arquitectura_b es
# un modulo hermano del mismo proyecto y los reutiliza a proposito para no
# duplicar el reparto ni el corto de un solo worker
from orquestador import repartir, _armar_tareas, _ejecutar

__all__ = ["repartir", "ejecutar_procesos"]


def ejecutar_procesos(n_workers, total_eventos, carpeta, semilla):
    """corre la generacion con ProcessPoolExecutor y devuelve un stat por worker.

    reparte total_eventos entre n_workers sin perder ninguno, lanza el pool y
    junta la lista de {worker_id, archivo, eventos, bytes}. el timing y la
    agregacion por configuracion los hace orquestador.correr_config; aqui la
    salida es cruda a proposito, para que la consuma un experimento.
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    _, tareas = _armar_tareas(n_workers, total_eventos, carpeta, semilla)
    stats, _ = _ejecutar(tareas, n_workers, paralelo=True)
    return stats
