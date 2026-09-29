"""presentacion y persistencia de la campana de mediciones.

el analisis de lab1 4.4 se apoya en estas dos salidas: la tabla que se imprime
al final de la corrida y el bench/mediciones.csv que despues consume
bench/graficos.py para dibujar la curva de speedup.

ni el orquestador ni el generador saben nada de esto, aqui solo se formatea y
se guarda lo que ya viene calculado.
"""

import csv
from pathlib import Path

# el orden y los nombres de las columnas del historico, fijos para que
# bench/graficos.py pueda leer el csv sin adivinar
CAMPOS_CSV = [
    "workers",
    "eventos_totales",
    "tiempo",
    "throughput",
    "transferencia_MB_s",
]


def guardar_medicion_csv(resultado, archivo_csv):
    """agrega una fila a bench/mediciones.csv en modo append.

    el encabezado se escribe solo cuando el archivo no existe o esta vacio, asi
    el benchmark se puede correr en varias tandas sin perder lo anterior ni
    repetir la cabecera en medio del csv.
    """
    archivo_csv = Path(archivo_csv)
    archivo_csv.parent.mkdir(parents=True, exist_ok=True)
    escribir_encabezado = not (
        archivo_csv.exists() and archivo_csv.stat().st_size > 0
    )

    with open(archivo_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        if escribir_encabezado:
            writer.writeheader()
        writer.writerow({
            "workers": resultado["workers"],
            "eventos_totales": resultado["eventos_totales"],
            "tiempo": f'{resultado["tiempo"]:.4f}',
            "throughput": f'{resultado["throughput"]:.2f}',
            "transferencia_MB_s": f'{resultado["transferencia_MB_s"]:.2f}',
        })


def imprimir_tabla(resultados):
    """la curva de escalabilidad del punto 3, ya con speedup y eficiencia.

    S(n) = T(1) / T(n) se saca siempre contra la corrida de 1 worker, que es la
    linea base. E(n) = S(n) / n mide cuanto de ese speedup es real: en el ideal
    lineal E(n) = 1, y lo que se aleja de 1 es lo que se pierde en el arranque
    de procesos, la contencion de disco y el reparto desparejo del resto.
    """
    base = resultados[0]["tiempo"]
    print(
        "\nworkers | eventos/worker |  mediana s |    eventos/s |   MB/s | "
        "speedup | eficiencia |   eventos/dia"
    )
    for r in resultados:
        speedup = base / r["tiempo"]
        print(
            f"{r['workers']:>7} | {r['eventos_por_worker']:>14,} | "
            f"{r['tiempo']:>9.4f} | {r['throughput']:>12,.0f} | "
            f"{r['transferencia_MB_s']:>6.2f} | {speedup:>6.2f}x | "
            f"{speedup / r['workers']:>10.2f} | {r['eventos_dia']:>13,.0f}"
        )
