# Pendientes para la presentación

Actualizado el 19-10-2026, con la ejecución de 2 workers sobre la última versión de GitHub.

## Estado

`fase2_pyspark.ipynb` está ejecutado completo dentro del contenedor, sin errores. Tiene 11 celdas Markdown de contexto (portada, índice, introducción de cada sección y título de Conclusiones) y 17 celdas de código `# Interpretacion X.Y` que arman el texto de resultados con los valores de cada corrida. Las 8 implicancias de la consigna tienen su evidencia en el notebook.

| Dato | Valor de la ejecución presentada |
|:---|:---|
| Clúster | 2 workers × 2 núcleos × 2 GB, driver de 2 GB (`.env`, perfil de 8 GB) |
| RAM de Docker | 11,7 GB |
| Imágenes | `img/arquitectura_cluster.svg`, `ui_8080_workers.png`, `ui_4040_stages.png` (job 60), `ui_4040_sesgo_sin_salting.png` (etapa 168), `ui_4040_sesgo_con_salting.png` (etapa 170) |
| Shuffle | Fijado en 8 particiones sin AQE en el hito 4.4 (celda 46 del notebook) |

## Falta

- [ ] Llenar la columna **«Expone»** del índice (`00_portada_indice.md`). Es el único «COMPLETAR» que queda.
- [ ] Antes de presentar, decidir si se vuelve a ejecutar. Con *Restart & Run All* las interpretaciones y la prueba de humo de la celda 1.3 se actualizan solas con los valores de ese equipo. Las capturas de `img/` y sus pies (figuras 2 a 5) son de la ejecución de referencia y no cambian: para reemplazarlas hay que tomarlas de nuevo mientras la sesión está viva y corregir los pies en las celdas de interpretación 1.3, 5.3 y 7.3.

## Números de la ejecución de referencia

En el notebook estos valores los calcula cada corrida. Los bloques INTERPRETACIÓN y CONCLUSIONES de los `.md` los repiten solo como referencia para preparar la presentación; el script de abajo no los inserta. Los conteos no cambian entre ejecuciones; los tiempos sí.

| Celda | Valores escritos |
|:---|:---|
| 2.2b | `inferSchema` 9,91 s y 1 job · `StructType` 0,48 s y 0 jobs |
| 2.3 | Lectura + cache: 13,4 s |
| 3.3 | 2,7 · 4,5 · 8,4 · 6,9 · 3,4 · total 25,9 s · cache de 199,6 MiB |
| 4.2 | Total de la limpieza: 14,7 s |
| 5.3 | 1,89 · 1,04 · 0,87 · 0,93 s · mejoras 1,83× / 2,18× / 2,04× · se aplica 8 sin AQE (fijado) |
| 6.2 | 40 archivos · 34,2 MiB · 35,5× · escritura 16,5 s |
| 6.3 | Conteo desde Parquet: 2,3 s · consulta de un día: 0,16 s |
| 7.3 | `faja_1` 4.698.974 (47,0 %) · tarea más cargada 5.243.278 / 1.790.754 · 792 / 404 ms · mediana 136 / 251 ms · 1,60 / 1,67 s · 0,96× |
| 8.2 | Join ingenuo: 10.486.486 (+486.486) |
| 8.3 | Range join: 10.000.000 · 216.218 marcadas · 0,9 s / 0,7 s |
| 9.1 | Repite los valores anteriores |

## Opcional (código de Cristian)

- El `WARN FileStreamSink` de los hitos 1.5 imprime una traza de Java. Se evita pasando a `spark.read.json()` la lista `archivos` en vez del patrón con comodín.
- El hito 2.5b deja una línea `DataFrame[...]` suelta; se evita con `_ = series.unpersist()`.
- `sc.setLocalProperty("spark.jobGroup.id", None)` no limpia la descripción del job en la UI; `sc.setJobDescription(None)` sí.

## Cómo volver a insertar los Markdown

Las celdas Markdown de contexto se editan en los `.md` de esta carpeta, nunca directo en el notebook. El texto de las interpretaciones se edita en su celda de código `# Interpretacion X.Y` del notebook. Después, desde la raíz del repositorio:

```text
python -I -s borradores_markdown/armar_vista_previa.py borradores_markdown fase2_pyspark.ipynb fase2_pyspark.ipynb
```

El script quita las celdas Markdown que tenga el notebook y vuelve a insertar las de los borradores, salvo los bloques INTERPRETACIÓN y CONCLUSIONES: esas celdas ya las genera el notebook con código, y si se insertaran quedarían duplicadas (conserva el título de Conclusiones del notebook). Cada bloque se ubica antes de la celda de código que indica su marcador `antes de Hito X`; si un hito se repite, la segunda celda es `Hito Xb`, la tercera `Hito Xc`, etc. Para revisar sin tocar el notebook, cambia el tercer argumento por `vista_previa.ipynb`.
