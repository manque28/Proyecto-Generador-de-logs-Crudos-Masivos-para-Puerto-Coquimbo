"""fase 1 del proyecto, terminal puerto coquimbo sitio 3.

cada worker escribe su propio archivo .jsonl porque elegimos la opcion B


    esquema.py      construccion y validacion del evento
    simulador.py    modelos de los activos y su fisica
    generador.py    el bucle de un worker, el reloj, el buffer y el archivo
    orquestador.py  el reparto entre workers y la medicion

pendiente de lab1 4.2: el simulador todavia no es parametrizable por linea de
comandos. el documento es explicito, si hay que abrir y editar un archivo
para cambiar la cantidad de procesos el requisito no esta cumplido, asi que
estas constantes tienen que pasar a argparse con --workers, --total-events,
--output-dir, --arch, --batch-size, --seed y --sim-days.

para correrlo: python src/main.py"""

from pathlib import Path

from orquestador import correr_config

# la meta de volumen son 10 millones de eventos como minimo, que a
# ~150 bytes cada uno son del orden de 1,4 a 1,7 GB en disco
TOTAL_EVENTOS = 10_000_000

# la curva de escalabilidad se mide con estas cinco
# configuraciones y el total de eventos fijo, no repartido
CONFIGS = (1, 2, 4, 8, 16)

# la salida va a data/raw/ y esa carpeta esta en el .gitignore desde
# el primer commit, el dataset no se sube a git
RAIZ = Path("data/raw")

# con la misma semilla y el mismo numero de workers dos ejecuciones
# tienen que producir datasets identicos
SEMILLA = 42

PARALELO = True


def imprimir_tabla(resultados):
    """
    el speedup es el S(n) = T(1) / T(n) del punto 3, lo saco siempre contra la
    primera corrida, la de 1 worker, que es la linea base.

    pendiente del mismo punto 3: falta la eficiencia E(n) = S(n) / n y el
    grafico contra la recta del speedup ideal, que es donde el documento dice
    que se juega el analisis. tambien falta el MB/s efectivo del punto 4.
    """
    print("\nworkers | eventos/worker |  segundos |    eventos/s | speedup")
    base = resultados[0]["segundos"]
    for r in resultados:
        print(
            f"{r['workers']:>7} | {r['eventos_por_worker']:>14,} | "
            f"{r['segundos']:>9,.2f} | {r['eventos_s']:>12,} | "
            f"{base / r['segundos']:>6.2f}x"
        )


def main():
    """la campana de mediciones completa, una corrida por configuracion.
    """
    resultados = []
    for n_workers in CONFIGS:
        r = correr_config(n_workers, TOTAL_EVENTOS, RAIZ, SEMILLA, PARALELO)
        # lab1 4.6, el volumen minimo es el requisito duro de la fase, si me
        # falta un solo evento prefiero enterarme aqui y no en la correccion
        assert r["eventos"] == TOTAL_EVENTOS, r
        resultados.append(r)
        print(r)

    imprimir_tabla(resultados)


if __name__ == "__main__":
    main()
