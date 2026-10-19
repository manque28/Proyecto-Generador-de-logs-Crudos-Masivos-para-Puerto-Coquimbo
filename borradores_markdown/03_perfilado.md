<!-- ===== CELDA 3.1 · CONTEXTO · antes de Hito 2 ===== -->

## Perfilado de calidad

**Qué hacemos:** medimos el estado de los datos **sin modificar nada**. Son 27 chequeos, y cada uno compara lo medido con lo que el dominio dice que debería haber (69 equipos, 185 series, 5 métricas, una lectura cada 15 s).

**Por qué importa en Big Data:** con 10 millones de filas nadie puede revisar los datos a ojo, y un `show()` enseña 20 filas de 10 millones. Si se limpia sin haber medido antes, después no hay forma de saber cuánto se perdió ni por qué. El perfilado es lo que permite decidir qué limpiar y justificarlo con números.

Cada chequeo responde una pregunta concreta:

| Hito | Pregunta | Qué se mide |
|:---:|:---|:---|
| 2.2 | ¿Cada línea es válida? | Líneas corruptas, nulos, formato del timestamp, `NaN` y valores físicamente imposibles |
| 2.3 | ¿Están todos los equipos? | Equipos, series, métricas y unidades |
| 2.4 | ¿Hay lecturas repetidas? | Duplicados por `(sensor_id, metric, timestamp)` |
| 2.5 | ¿Falta alguna lectura? | Huecos de 15 s en cada serie |
| 2.6 | ¿Los valores son razonables? | Media, dispersión y percentiles por métrica |

> **Nota.** Cada chequeo es una pasada sobre los 10 millones de filas, así que conviene agruparlos. El hito 2.2 calcula sus 10 chequeos en **una sola agregación**, es decir, en un solo recorrido del dataset.

<!-- ===== CELDA 3.2 · INTERPRETACIÓN · antes de Hito 2.7 ===== -->

### Un promedio global puede esconder dos poblaciones

La temperatura media de todo el dataset es **−7,04 °C**, pero ningún equipo mide eso. Al separar por familia aparecen dos grupos que no tienen nada que ver:

| Familia | Lecturas | Mínimo | Mediana | Máximo |
|:---|---:|---:|---:|---:|
| `AMB` (sensores ambientales) | 648.648 | 9,42 °C | 14,66 °C | 20,62 °C |
| `REEFER` (contenedores refrigerados) | 2.594.592 | −18,37 °C | −17,98 °C | 5,89 °C |

Pasa lo mismo con la corriente: la mediana es 7,52 A, pero el percentil 99 llega a 283 A, porque conviven equipos de consumo muy distinto.

Por eso el perfilado se hace **por métrica y por familia**, no con un `describe()` de toda la tabla. La tabla también deja ver algo que vale la pena seguir: hay contenedores refrigerados que llegan a 5,89 °C, lejos de su mediana de −17,98 °C.

<!-- ===== CELDA 3.3 · INTERPRETACIÓN · antes de Hito 3 ===== -->

### Resultado del perfilado: 27 de 27 chequeos correctos

| Bloque | Resultado | Tiempo |
|:---|:---|---:|
| Validez por línea | 0 corruptas · 0 nulos · 0 valores imposibles | 4,2 s |
| Dominio | 69 equipos · 185 series · 5 métricas con su unidad | 7,3 s |
| Duplicados | 0 claves repetidas | 12,5 s |
| Continuidad | 54.054 a 54.055 lecturas por serie · 0 huecos · 9,38 días | 10,1 s |
| Perfil de valores | 5 métricas perfiladas | 5,4 s |
| **Total** | **27 de 27 correctos** | **39,5 s** |

Dos cosas que muestran los tiempos:

- **Buscar duplicados es lo más caro (12,5 s)** aunque no encuentre ninguno: para saber si una lectura se repite hay que juntar todas las filas con la misma clave, y eso obliga a mover datos entre executors. Es el *shuffle* que analizamos en la [sección 5](#Diagnóstico-del-shuffle).
- **La validez por línea es lo más barato (4,2 s)**: cada fila se revisa por sí sola, sin depender de ninguna otra.

Todo esto se midió sobre el cache: los 1.212,6 MiB de JSONL ocupan **199,6 MiB** en la memoria de los executors (16 de 16 particiones), así que ningún chequeo volvió a leer los archivos.

Además, cada chequeo detiene el notebook con un `assert` apenas falla: si llegan datos dañados, la ejecución se corta aquí y no en medio de la limpieza.

> **Idea clave.** El perfilado decide la limpieza. Como medimos 0 duplicados, la sección siguiente se salta la deduplicación y se ahorra un *shuffle* de 10 millones de filas.

[↑ Volver al índice](#Índice)

---
