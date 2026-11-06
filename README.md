# Proyecto-Generador-de-logs-Crudos-Masivos-para-Puerto-Coquimbo
Proyecto universitario de **Programación Avanzada**. Simula el comportamiento físico de un frente de atraque portuario, genera 10 millones de lecturas de sensores en paralelo y las procesa en un clúster de Apache Spark.

El sitio modelado tiene fajas transportadoras, dos grúas móviles, una báscula de acceso vehicular y un patio de contenedores reefer conectados a la red eléctrica del terminal.

## Contenido

- [Qué hace el proyecto](#qué-hace-el-proyecto)
- [El sitio simulado](#el-sitio-simulado)
- [Formato de los datos](#formato-de-los-datos)
- [Requisitos](#requisitos)
- [Fase 1: generar los datos](#fase-1-generar-los-datos)
- [Fase 2: procesar con PySpark](#fase-2-procesar-con-pyspark)
- [Fase 3: preparar los datos para MLlib](#fase-3-preparar-los-datos-para-mllib)
- [Resultados](#resultados)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Equipo](#equipo)

## Qué hace el proyecto

El trabajo tiene tres fases que se encadenan: la salida de cada una es la entrada de la siguiente.

```mermaid
flowchart LR
    A[Simulador físico<br>69 equipos] --> B[Generador paralelo<br>1 a 16 procesos]
    B --> C[(data/raw/<br>JSONL · 1,68 GiB<br>+ verdad de terreno)]
    C --> D[Clúster Spark<br>1 master · N workers]
    D --> E[(salida_fase2/<br>telemetria_limpia<br>Parquet por día)]
    E --> F[Fase 3<br>feature engineering<br>MLlib]
```

| Fase | Qué hace | Tecnología |
|:---|:---|:---|
| **1 · Generación** | Simula los equipos y escribe 10.000.000 de eventos, midiendo cómo escala el generador con 1, 2, 4, 8 y 16 procesos | Python, solo biblioteca estándar |
| **2 · Procesamiento** | Ingesta, perfila, limpia y analiza los eventos, los etiqueta contra la verdad de terreno y los guarda en Parquet particionado | PySpark 4.0.1 sobre Docker |
| **3 · Machine Learning** | Convierte las lecturas en ventanas de 5 minutos y crea las características para MLlib (Laboratorio 11) | PySpark MLlib sobre el mismo clúster |

## El sitio simulado

No es un generador de números al azar: cada equipo recuerda su estado anterior, y de ahí salen la inercia, la deriva y el ruido de las mediciones.

| Familia | Equipos | Métricas | Puntos de medición |
|:---|---:|:---|---:|
| Fajas transportadoras (`FAJA`) | 6 | vibración, corriente | 12 |
| Grúas móviles (`GRUA`) | 2 | corriente, peso | 4 |
| Báscula de acceso (`BASCULA`) | 1 | peso | 1 |
| Contenedores reefer (`REEFER`) | 48 | temperatura, corriente, humedad | 144 |
| Sensores ambientales (`AMB`) | 12 | temperatura, humedad | 24 |
| **Total** | **69** | | **185** |

Cada punto reporta una lectura cada **15 segundos**. Los 10 millones de eventos equivalen a unos 9,4 días de operación a partir del 1 de enero de 2026.

De los 48 reefers, uno de cada cuatro trabaja a +4 °C (carga refrigerada) y el resto a −18 °C (congelado). Los reefers cuelgan de tres alimentadores eléctricos (`ALIM_S3_R1` a `ALIM_S3_R3`, 16 cada uno).

Además, cada equipo tiene un **estado de calidad del sensor** (`buena`, `degradada` o `mala`; mientras no es `buena` la lectura sale con más ruido) y puede sufrir **fallas con efecto físico real** sobre sus valores:

| Falla | Equipo | Efecto en los valores | Severidad |
|:---|:---|:---|:---|
| `puerta_abierta` | Reefer | sube la temperatura y la humedad | baja (1) |
| `desalineamiento` | Faja | vibración ×2,2 + 1,5 mm/s, corriente +12 % | media (2) |
| `sobrecorriente` | Grúa | corriente +45 % | media (2) |
| `falla_compresor` | Reefer | la corriente cae a 0,8 A y la temperatura sube hacia la del aire | alta (3) |

Un equipo tiene como máximo una falla activa a la vez, así que sus intervalos de falla nunca se superponen. La báscula y los sensores ambientales no fallan, solo cambian de calidad.

## Formato de los datos

Cada evento es un objeto JSON en una línea (formato JSONL):

```json
{"timestamp":"2026-01-01T00:00:00.000Z","sensor_id":"FAJA_S3_C1","metric":"vibration","value":1.962,"unit":"mm/s","calidad_sensor":"buena","alimentador_id":null,"worker_id":0}
```

| Campo | Tipo | Descripción |
|:---|:---|:---|
| `timestamp` | texto | Instante de la lectura en UTC, formato ISO 8601 con milisegundos |
| `sensor_id` | texto | Equipo, con la convención `TIPO_SITIO_CORRELATIVO` |
| `metric` | texto | `vibration`, `current`, `weight`, `temperature` o `humidity` |
| `value` | número | Valor medido |
| `unit` | texto | `mm/s`, `A`, `kg`, `C` o `%` |
| `calidad_sensor` | texto | `buena`, `degradada` o `mala`: lo informa el propio instrumento |
| `alimentador_id` | texto o `null` | Alimentador del reefer; `null` en los demás equipos (no aplica) |
| `worker_id` | entero | Proceso que generó la lectura; permite auditar el reparto de carga |

La falla **no** va en el JSONL: un sensor real no informa que está fallando. El simulador la deja aparte, como **verdad de terreno**, en `data/raw/verdad_wNN/part-XXX.csv`:

| Campo | Descripción |
|:---|:---|
| `sensor_id` | Equipo con la falla |
| `t_inicio`, `t_fin` | Intervalo semiabierto `[t_inicio, t_fin)` en UTC |
| `tipo_falla` | `puerta_abierta`, `desalineamiento`, `sobrecorriente` o `falla_compresor` |
| `severidad`, `severidad_num` | `baja`/`media`/`alta` y su equivalente 1/2/3 |

Con la misma semilla y el mismo número de procesos, dos ejecuciones producen archivos idénticos (con semilla 42 y 16 procesos: 10.000.000 de eventos y 1.441 intervalos de falla).

## Requisitos

| Para | Se necesita |
|:---|:---|
| Fase 1 | Python 3, sin dependencias externas |
| Fase 2 | Docker Desktop con al menos 6 GB de RAM asignados |
| Espacio en disco | Unos 2 GB libres por cada configuración generada |

## Fase 1: generar los datos

```bash
python src/main.py
```

El comando corre la campaña completa de mediciones: genera los 10 millones de eventos con 1, 2, 4, 8 y 16 procesos, cuatro veces cada configuración. Descarta la primera corrida y reporta la mediana de las otras tres. Toma varios minutos.

Al terminar quedan:

- `data/raw/`: una carpeta por configuración (`w01`, `w02`, `w04`, `w08`, `w16`), con un archivo `.jsonl` por proceso (`part-000.jsonl`, `part-001.jsonl`, …), y su verdad de terreno en `verdad_w01`, …, `verdad_w16`. La Fase 2 lee `data/raw/w16/` y `data/raw/verdad_w16/`.
- `bench/mediciones.csv`: tiempos y eventos por segundo de cada configuración.

Si solo se necesitan los datos de la Fase 2 (sin la campaña de mediciones), basta con la configuración de 16 procesos, que tarda unos segundos y no toca `bench/mediciones.csv`:

```bash
python -c "import sys; sys.path.insert(0,'src'); from orquestador import correr_config; print(correr_config(16, 10_000_000, 'data/raw', 42, True))"
```

El generador usa **procesos y no hilos**. El trabajo es cálculo y formateo de texto, y en Python los hilos se turnan un solo núcleo por el GIL; cada proceso tiene su propio intérprete y el paralelismo es real. Cada proceso escribe su propio archivo, así ninguno espera a otro para escribir.

## Fase 2: procesar con PySpark

**1. Configurar el clúster.** Copia la plantilla y ajústala a la RAM de tu Docker:

```bash
cp .env.example .env
```

| RAM de Docker | Workers | Núcleos por worker | Memoria por worker | Memoria del driver |
|:---|---:|---:|---:|---:|
| 6 GB | 2 | 1 | 1 GB | 1 GB |
| 8 GB | 2 | 2 | 2 GB | 2 GB |
| 12 GB | 3 | 2 | 2 GB | 2 GB |
| 16 GB | 3 | 2 | 3 GB | 3 GB |
| 32 GB | 4 | 3 | 6 GB | 4 GB |

La regla es que `WORKERS × WORKER_MEMORY + DRIVER_MEMORY` quede holgadamente bajo la RAM de Docker, y que `SPARK_EXECUTOR_MEMORY` no supere a `SPARK_WORKER_MEMORY`.

**2. Levantar el clúster.**

```bash
docker compose up -d --build
```

**3. Verificar que funciona.** La prueba de humo revisa cuatro cosas: sesión, executors, visibilidad de los datos y lectura completa.

```bash
docker compose exec jupyter python3 verificar_cluster.py
```

**4. Abrir el notebook.** Entra a JupyterLab, abre `fase2_pyspark.ipynb` y ejecuta *Restart & Run All*.

| Servicio | Dirección | Notas |
|:---|:---|:---|
| JupyterLab | <http://localhost:8889> | Token: el valor de `JUPYTER_TOKEN` en el `.env` |
| UI del master | <http://localhost:8080> | Workers registrados |
| UI del job | <http://localhost:4040> | Solo mientras hay una sesión de Spark activa |

**5. Apagar.**

```bash
docker compose down
```

### Qué hace el notebook

| Hito | Etapa | Qué resuelve |
|:---:|:---|:---|
| 1 | Ingesta | Lee los JSONL con esquema declarado y mide lo que costaría inferirlo |
| 2 | Perfilado | 32 chequeos de calidad, sin modificar los datos |
| 3 | Limpieza | Marca las líneas defectuosas y las aparta en cuarentena, sin borrarlas |
| 4 | Shuffle | Compara configuraciones de particiones y AQE sobre una misma consulta |
| 5 | Escritura | Parquet particionado por día, releído y verificado |
| 6 | Sesgo y joins | Provoca una clave sesgada y la mitiga con *salting*; compara un join ingenuo con un *range join* |
| 7 | Etiquetado | *Range join* con *broadcast* contra la verdad de terreno; deriva `sensor_confiable` y `es_anomalia_conocida` y escribe `salida_fase2/telemetria_limpia` |

## Resultados

Medidos en un clúster de 3 workers con 2 núcleos y 3 GB cada uno (perfil de 16 GB). Los tiempos varían según el equipo.

| Etapa | Resultado |
|:---|:---|
| Ingesta | 10.000.000 de eventos (1,68 GiB); inferir el esquema habría sumado 6,8 s más |
| Perfilado | 32 de 32 chequeos correctos: 0 líneas corruptas, 0 duplicados, 0 huecos |
| Limpieza | 10.000.000 de eventos limpios, balance de conteos verificado |
| Shuffle | De 1,06 s a 0,45 s (2,35×) con 12 particiones sin AQE |
| Escritura | 39,8 MiB en Parquet, 43,3 veces menos que el JSONL |
| Consulta de un día | 1.065.600 filas en 0,11 s, leyendo 1 de 10 carpetas |
| Sesgo | Tarea rezagada de 726 ms reducida a 264 ms con *salting*; consulta 1,21× más rápida |
| Joins | El join ingenuo fabricó 486.486 filas; el *range join* con *broadcast* conservó las 10.000.000 |
| Etiquetado | 0,84 % de las lecturas cae dentro de una falla y 5,19 % es de un sensor no confiable; conteo intacto (10.000.000) |

## Fase 3: preparar los datos para MLlib

Corre en el mismo clúster. Requiere haber ejecutado completo `fase2_pyspark.ipynb` (su hito 7 escribe `salida_fase2/telemetria_limpia`). Cada integrante trabaja su propio `fase3_lab11_feature_engineering.ipynb` (es entrega individual, por eso no está en el repositorio y está en `.gitignore`): se copia en la carpeta del proyecto, junto a `fase2_pyspark.ipynb`, y se abre en JupyterLab (<http://localhost:8889>). La tabla resume lo que hace cada bloque.

| Bloque | Paso de la guía | Qué hace |
|:---:|:---:|:---|
| 0 | 1 | Guarda del entorno: Python ≥ 3.10, PySpark 4.x de `/opt/spark` y `numpy` |
| 1 | 2 | `SparkSession` contra el clúster e imports de MLlib |
| 2 | 3 | Lee la capa limpia y revisa esquema, conteos y nulos |
| 3 | 4 | Unidad de observación: una serie `(sensor_id, metric)` durante 5 minutos (500.055 ventanas, cacheadas) |
| 4 | 5 | Línea base por serie con *broadcast join*; `z_prom`, `desv_z`, `rango_z`, `delta_z` y hora cíclica (`hora_sin`, `hora_cos`) |

Los nombres de columna difieren de los de la guía: `timestamp_utc` → `timestamp`, `entidad_id` → `sensor_id`, `entidad_tipo` → `asset_type`, `variable` → `metric`, `valor` → `value`.

## Estructura del repositorio

```text
.
├── src/                      Fase 1
│   ├── main.py               punto de entrada de la campaña de mediciones
│   ├── simulador.py          modelos físicos de los equipos
│   ├── generador.py          bucle de un proceso: reloj, buffer y archivo
│   ├── orquestador.py        reparto entre procesos y medición
│   ├── esquema.py            formato de la línea JSONL
│   ├── reporte.py            tabla final e histórico de mediciones
│   ├── arquitectura_b.py     un proceso y un archivo por worker
│   ├── emisor_tcp.py         variante que envía los eventos por socket
│   └── receptor_tcp.py       variante que los recibe y los escribe
├── bench/                    experimentos y mediciones de rendimiento
├── docker/                   imagen única de Spark para los tres roles
├── docker-compose.yml        clúster: master, workers y Jupyter
├── .env.example              plantilla de recursos del clúster
├── verificar_cluster.py      prueba de humo del clúster
├── fase2_pyspark.ipynb       notebook de la Fase 2, con las celdas Markdown de la presentación
├── img/                      diagrama del clúster y capturas de la UI de Spark que usa el notebook
├── borradores_markdown/      fuente de las celdas Markdown y script que las inserta en el notebook
├── borradores/               resúmenes que genera el propio notebook (hito 6.5)
└── docs/                     informes
```

No se suben al repositorio: `data/raw/` (los datos generados), `salida_fase2/` y `salida_fase3/` (la salida de Spark), `.env` y el notebook individual de la Fase 3.

## Equipo

Pablo Manque · Ignacio Brizuela · Cristian Rojo · Mauricio Hernandez · Francisco Seura · Raul Muñoz
