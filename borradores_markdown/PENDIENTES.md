# Pendientes para la presentación

Actualizado el 15-10-2026, después de integrar la última versión de Cristian.

## Estado

`fase2_pyspark.ipynb` está ejecutado completo dentro del contenedor (celdas 1 a 44, sin errores) y ya tiene insertadas las 27 celdas Markdown de esta carpeta. Las 8 implicancias de la consigna tienen su evidencia en el notebook.

| Dato | Valor de la ejecución presentada |
|:---|:---|
| Clúster | 3 workers × 2 núcleos × 3 GB, driver de 3 GB (`.env`, perfil de 16 GB) |
| RAM de Docker | 15,4 GB |
| Imágenes | `img/arquitectura_cluster.svg`, `ui_8080_workers.png`, `ui_4040_stages.png` (job 52), `ui_4040_sesgo_sin_salting.png` (etapa 146), `ui_4040_sesgo_con_salting.png` (etapa 148) |

## Falta

- [ ] Llenar la columna **«Expone»** del índice (`00_portada_indice.md`). Es el único «COMPLETAR» que queda.
- [ ] Antes de presentar, decidir si se vuelve a ejecutar. Si se hace *Restart & Run All*, **los tiempos cambian** y hay que revisar los números de la tabla de abajo. Además, las capturas de la UI se tienen que repetir mientras la sesión está viva, porque los números de etapa (146, 148) y de job (52) pueden cambiar.

## Números escritos en el Markdown

Los conteos no cambian entre ejecuciones; los tiempos sí.

| Celda | Valores escritos |
|:---|:---|
| 2.2b | `inferSchema` 7,88 s y 1 job · `StructType` 0,35 s y 0 jobs |
| 2.3 | Lectura + cache: 7,9 s |
| 3.3 | 2,2 · 3,5 · 6,7 · 5,3 · 2,8 · total 20,5 s · cache de 199,6 MiB |
| 4.2 | Total de la limpieza: 8,9 s |
| 5.3 | 1,30 · 0,55 · 0,53 · 0,51 s · mejoras 2,36× / 2,45× / 2,56× · gana 12 sin AQE |
| 6.2 | 34,5 MiB · 35,2× · escritura 12,9 s |
| 6.3 | Conteo desde Parquet: 2,2 s · consulta de un día: 0,12 s |
| 7.3 | `faja_1` 4.698.974 (47,0 %) · tarea más cargada 5.214.599 / 1.605.409 · 747 / 274 ms · mediana 90 / 137 ms · 1,45 / 1,14 s · 1,27× |
| 8.2 | Join ingenuo: 10.486.486 (+486.486) |
| 8.3 | Range join: 10.000.000 · 216.218 marcadas · 0,7 s / 0,5 s |
| 9.1 | Repite los valores anteriores |

## Opcional (código de Cristian)

- El `WARN FileStreamSink` de los hitos 1.5 imprime una traza de Java. Se evita pasando a `spark.read.json()` la lista `archivos` en vez del patrón con comodín.
- El hito 2.5b deja una línea `DataFrame[...]` suelta; se evita con `_ = series.unpersist()`.
- `sc.setLocalProperty("spark.jobGroup.id", None)` no limpia la descripción del job en la UI; `sc.setJobDescription(None)` sí.

## Cómo volver a insertar los Markdown

Las celdas Markdown se editan en los `.md` de esta carpeta, nunca directo en el notebook. Después, desde la raíz del repositorio:

```text
python -I -s borradores_markdown/armar_vista_previa.py borradores_markdown fase2_pyspark.ipynb fase2_pyspark.ipynb
```

El script quita las celdas Markdown que tenga el notebook y vuelve a insertar las de los borradores. Cada bloque se ubica antes de la celda de código que indica su marcador `antes de Hito X`; si un hito se repite, la segunda celda es `Hito Xb`, la tercera `Hito Xc`, etc. Para revisar sin tocar el notebook, cambia el tercer argumento por `vista_previa.ipynb`.
