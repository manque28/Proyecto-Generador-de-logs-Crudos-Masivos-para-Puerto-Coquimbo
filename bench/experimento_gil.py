import multiprocessing
import threading
import time

from src.generador_francisco import generar_eventos

TOTAL_EVENTOS = 100_000
EVENTOS_POR_WORKER = TOTAL_EVENTOS // 4
NUM_HILOS = 4
NUM_PROCESOS = 4

def ejecutar_monohilo():
    """Genera los 100.000 eventos utilizando un solo hilo."""
    inicio = time.perf_counter()
    
    generar_eventos(TOTAL_EVENTOS)
    
    fin = time.perf_counter()
    return fin - inicio

def ejecutar_multihilo():
    """Genera los eventos utilizando 4 hilos."""
    hilos = []
    
    inicio = time.perf_counter()
    
    for _ in range(NUM_HILOS):
        hilo = threading.Thread(
            target=generar_eventos,
            args=(EVENTOS_POR_WORKER,),
        )
        hilos.append(hilo)
        hilo.start()
    
    for hilo in hilos:
        hilo.join()
    
    fin = time.perf_counter()
    return fin - inicio


def ejecutar_multiproceso():
    """Genera los eventos utilizando 4 procesos independientes."""
    procesos = []
    
    inicio = time.perf_counter()
    
    for _ in range(NUM_PROCESOS):
        proceso = multiprocessing.Process(
            target=generar_eventos,
            args=(EVENTOS_POR_WORKER,),
        )
        procesos.append(proceso)
        proceso.start()
    
    for proceso in procesos:
        proceso.join()
    
    fin = time.perf_counter()
    return fin - inicio


if __name__ == "__main__":
    tiempo_monohilo = ejecutar_monohilo()
    tiempo_multihilo = ejecutar_multihilo()
    tiempo_multiproceso = ejecutar_multiproceso()
    
    print("=== EXPERIMENTO GIL ===")
    print(f"Eventos totales: {TOTAL_EVENTOS:,}")
    print(f"Workers concurrentes: 4")
    print()
    print(
        f"Tiempo con 1 hilo:   "
        f"{tiempo_monohilo:.6f} segundos"
    )
    print(
        f"Tiempo con 4 hilos:  "
        f"{tiempo_multihilo:.6f} segundos"
    )
    print(
        f"Tiempo con 4 procesos:"
        f" {tiempo_multiproceso:.6f} segundos"
    )

    print()
    print("=== COMPARACIÓN ===")

    if tiempo_multihilo > tiempo_monohilo:
        print(
            "Los 4 hilos no mejoraron el tiempo del proceso "
            "monohilo, comportamiento compatible con el GIL "
            "en una carga limitada por CPU."
        )
    else:
        print(
            "Los 4 hilos fueron más rápidos en este entorno; "
            "el resultado puede estar influido por la naturaleza "
            "de la carga y por operaciones de E/S."
        )
    
    if tiempo_multiproceso < tiempo_multihilo:
        print(
            f"Los procesos fueron "
            f"{tiempo_multihilo / tiempo_multiproceso:.2f}x "
            f"más rápidos que los hilos."
        )
    else:
        print(
            "Los procesos no fueron más rápidos que los hilos "
            "en esta ejecución."
        )
