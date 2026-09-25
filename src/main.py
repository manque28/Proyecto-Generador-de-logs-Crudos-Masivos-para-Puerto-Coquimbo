"""fase 1 del proyecto, terminal puerto coquimbo sitio 3.

cada worker escribe su propio archivo .jsonl porque elegimos la opcion B

    esquema.py      el contrato del evento y la linea jsonl
    simulador.py    modelos de los activos y su fisica
    generador.py    el bucle de un worker, el reloj, el buffer y el archivo
    orquestador.py  el reparto entre workers y la medicion por configuracion
    reporte.py      la tabla final y el historico bench/mediciones.csv

pendiente de lab1 4.2: el simulador todavia no es parametrizable por linea de
comandos. el documento es explicito, si hay que abrir y editar un archivo
para cambiar la cantidad de procesos el requisito no esta cumplido, asi que
estas constantes tienen que pasar a argparse con --workers, --total-events,
--output-dir, --arch, --batch-size, --seed y --sim-days.

el generador quedo x2,5 mas rapido que la primera version, y las mediciones
viejas de bench/mediciones.csv son de antes de eso. la campana hay que
correrla de nuevo entera antes de sacar conclusiones de la curva, mezclar las
dos tandas en el mismo grafico no significa nada. el detalle de que se cambio
y cuanto rindio cada cosa esta en bench/microbench_resultados.md, y el perfil
que las origino en bench/perfil_cpu_resultados.md.

para correrlo: python src/main.py"""

from pathlib import Path

from orquestador import medir_configuracion
from reporte import guardar_medicion_csv, imprimir_tabla

# la raiz del proyecto es la carpeta que contiene src/ y bench/. todas las
# salidas cuelgan de aqui y no del directorio desde donde se lance el script,
# asi "python src/main.py" desde la raiz y "cd src && python main.py" dejan los
# archivos en el mismo sitio y no aparece un bench/ ni un data/ dentro de src/
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent

# la meta de volumen son 10 millones de eventos como minimo, que a
# ~150 bytes cada uno son del orden de 1,4 a 1,7 GB en disco
TOTAL_EVENTOS = 10_000_000

# la curva de escalabilidad se mide con estas cinco
# configuraciones y el total de eventos fijo, no repartido
CONFIGS = (1, 2, 4, 8, 16)

# la salida va a data/raw/ y esa carpeta esta en el .gitignore desde
# el primer commit, el dataset no se sube a git
RAIZ = RAIZ_PROYECTO / "data" / "raw"

# con la misma semilla y el mismo numero de workers dos ejecuciones
# tienen que producir datasets identicos.
#
# esto era una promesa incumplida hasta hace poco: el rng si era reproducible,
# pero el reloj arrancaba en datetime.now() y eso no lo fija ninguna semilla,
# asi que dos corridas daban timestamps distintos y el dataset entero cambiaba.
# se arreglo anclando el reloj en generador.EPOCA_SIMULACION_MS, y ahora
# bench/verificacion_reloj.py lo comprueba comparando el sha256 de dos corridas
SEMILLA = 42

PARALELO = True

# cada configuracion se corre 4 veces, se descarta la primera (warm-up) y se
# reporta la mediana de las 3 restantes
REPETICIONES = 4

# el historico de corridas que alimenta los graficos de bench/
ARCHIVO_CSV = RAIZ_PROYECTO / "bench" / "mediciones.csv"


def main():
    """la campana de mediciones completa, una configuracion a la vez.
    """
    print("=== BENCHMARK ===")
    print(f"eventos totales: {TOTAL_EVENTOS:,}")
    print(f"configuraciones: {', '.join(str(n) for n in CONFIGS)} workers")
    print(
        f"repeticiones: {REPETICIONES} "
        f"(se descarta la primera, estadistico: mediana)"
    )

    resultados = []
    for n_workers in CONFIGS:
        r = medir_configuracion(
            n_workers, TOTAL_EVENTOS, RAIZ, SEMILLA, PARALELO, REPETICIONES
        )
        # lab1 4.6, el volumen minimo es el requisito duro de la fase, si me
        # falta un solo evento prefiero enterarme aqui y no en la correccion
        assert r["eventos_totales"] == TOTAL_EVENTOS, r
        guardar_medicion_csv(r, ARCHIVO_CSV)
        resultados.append(r)

    imprimir_tabla(resultados)
    print(f"\ncsv actualizado: {ARCHIVO_CSV}")


if __name__ == "__main__":
    main()
