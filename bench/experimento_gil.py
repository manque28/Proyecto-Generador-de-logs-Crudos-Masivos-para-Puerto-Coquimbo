import threading
import time

# Sustituir por el import real del generador de Francisco.
from src.generador_francisco import generar_eventos


TOTAL_EVENTOS = 100_000
EVENTOS_POR_HILO = 25_000
NUM_HILOS = 4


def ejecutar_monohilo():
    inicio = time.perf_counter()

    generar_eventos(TOTAL_EVENTOS)

    fin = time.perf_counter()
    return fin - inicio


def ejecutar_multihilo():
    hilos = []

    inicio = time.perf_counter()

    for _ in range(NUM_HILOS):
        hilo = threading.Thread(
            target=generar_eventos,
            args=(EVENTOS_POR_HILO,),
        )
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()

    fin = time.perf_counter()
    return fin - inicio


if __name__ == "__main__":
    tiempo_monohilo = ejecutar_monohilo()
    tiempo_multihilo = ejecutar_multihilo()

    print(f"Eventos: {TOTAL_EVENTOS}")
    print(f"Tiempo con 1 hilo: {tiempo_monohilo:.6f} segundos")
    print(f"Tiempo con 4 hilos: {tiempo_multihilo:.6f} segundos")