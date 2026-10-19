<!-- ===== CELDA 5.1 · CONTEXTO · antes de Hito 4 ===== -->

## Diagnóstico del shuffle

**Qué hacemos:** tomamos una consulta real (el resumen por hora de cada serie), leemos su plan físico y medimos la misma consulta con cuatro configuraciones de particiones.

**Por qué importa en Big Data:** no todas las operaciones cuestan lo mismo en un clúster.

| Tipo | Ejemplos | Qué necesita |
|:---|:---|:---|
| **Estrecha** | `filter`, `select`, `withColumn` | Cada partición se procesa sola, en el executor donde ya está. |
| **Ancha** | `groupBy`, `dropDuplicates`, `orderBy`, `join` | Juntar filas de la misma clave que están en particiones distintas. |

Para juntar esas filas Spark hace un *shuffle*: cada executor ordena sus datos por clave, los escribe, los envía por la red y otro executor los vuelve a leer. Es lo más caro de un job, porque todo lo demás ocurre en memoria dentro de una misma máquina.

Dos ajustes controlan ese costo:

- `spark.sql.shuffle.partitions`: en cuántas particiones quedan los datos después del *shuffle*. Por defecto son **200**.
- **AQE** (*Adaptive Query Execution*): Spark mira el tamaño real de los datos mientras ejecuta y corrige el plan, por ejemplo uniendo particiones que quedaron casi vacías.

> **Nota.** Cada configuración se mide con la mediana de 3 corridas y con una escritura `noop`, que ejecuta la consulta completa pero no guarda nada. Así medimos solo el cómputo.

<!-- ===== CELDA 5.2 · INTERPRETACIÓN · antes de Hito 4.3 ===== -->

### Cómo leer el plan físico

El plan se lee **de abajo hacia arriba**. Los pasos propios de esta consulta son los cuatro de arriba:

| Paso | En el plan | Qué significa |
|:---:|:---|:---|
| 1 | `InMemoryTableScan [metric, sensor_id, timestamp, value]` | Lee del cache solo las 4 columnas que la consulta usa, de las 7 que existen. |
| 2 | `*(1) HashAggregate ... partial_count, partial_avg` | Cada partición calcula un resumen parcial por su cuenta. Es la etapa 1, estrecha. |
| 3 | `Exchange hashpartitioning(sensor_id, metric, hora, 200)` | **El *shuffle*.** Reparte los resúmenes por clave en 200 particiones. |
| 4 | `*(2) HashAggregate ... count, avg, min, max` | Junta los parciales de cada clave. Es la etapa 2. |

La consulta tiene **un solo `Exchange`**, y es el `groupBy` el que lo provoca.

**La evaluación perezosa, vista en nuestro plan.** Más abajo aparecen el `Filter` y el `Project` de la limpieza. Los escribimos en celdas distintas (hitos 3.1 y 3.2), pero Spark los fundió en una sola etapa, marcada con `*(1)`, y aplicó la condición de descarte directo en el filtro. Eso es posible porque conocía el plan completo antes de ejecutar.

Las particiones de entrada están parejas: 16 particiones con una razón de 1,30 entre la mayor y la menor.

<!-- ===== CELDA 5.3 · INTERPRETACIÓN · antes de Hito 5 ===== -->

### La misma consulta, cuatro configuraciones

| Configuración | Mediana | Tareas (etapa 1 → etapa 2) | Datos en *shuffle* | Frente a la base |
|:---|---:|:---:|---:|---:|
| 200 sin AQE (valor por defecto) | 1,89 s | 16 → 200 | 1,9 MiB | 1,00× |
| 200 con AQE | 1,04 s | 16 → 2 | 1,9 MiB | 1,83× |
| 4 sin AQE (1× núcleos) | 0,87 s | 16 → 4 | 1,2 MiB | 2,18× |
| **8 sin AQE** (2× núcleos) | **0,93 s** | 16 → 8 | 1,2 MiB | **2,04×** |

**Por qué 200 es lento aquí.** El *shuffle* mueve solo 1,9 MiB. Repartido en 200 particiones son unos 10 KiB por tarea: 200 tareas casi vacías, donde se gasta más tiempo en lanzarlas y coordinarlas que en procesar datos.

<div align="center">
<img src="img/ui_4040_stages.png" alt="Detalle de un job en la UI de Spark: etapa de 16 tareas y etapa de shuffle de 200 tareas" width="720"><br>
<em>Figura 3. Un job de la configuración «200 sin AQE» en <code>localhost:4040</code> (captura de nuestra ejecución de referencia). La etapa 1 lee 164 MiB del cache con 16 tareas; la etapa 2 usa 200 tareas para leer apenas 1.988 KiB de <em>shuffle</em>.</em>
</div>

**Qué resuelve AQE.** Con las mismas 200 particiones configuradas, AQE mide el tamaño real después de la etapa 1 y las une en **2**. El tiempo baja de 1,89 s a 1,04 s sin que tengamos que adivinar el número correcto.

**El ajuste manual y AQE llegan a tiempos parecidos.** Con 4 u 8 particiones, una o dos por núcleo, cada tarea tiene trabajo real y no sobra ninguna. Las tres configuraciones ajustadas quedan dentro de 0,17 s (0,87 s, 0,93 s y 1,04 s), y en ejecuciones anteriores el orden entre ellas cambió. La conclusión no depende de cuál gane: **lo que hay que evitar son las 200 tareas casi vacías**, y para eso sirve tanto ajustar el número a los núcleos como dejar que AQE lo ajuste solo.

**Por qué el *shuffle* pesa tan poco.** Gracias a la agregación parcial del paso 2, por la red viajan los resúmenes por serie y hora, no los 10 millones de filas.

El hito 4.4 aplica **8 particiones sin AQE** al resto del notebook. En esta ejecución 4 particiones fue apenas más rápida (0,87 s frente a 0,93 s), pero dejamos fijo 8 para que las ejecuciones del grupo sean comparables.

> **Atención.** Ese número sirve para este volumen de datos. Si los datos crecen, un valor fijo se queda corto; por eso AQE es la opción segura cuando no se conoce de antemano el tamaño del *shuffle*.

> **Idea clave.** El *shuffle* es el costo que hay que vigilar, y el número de particiones tiene que calzar con el tamaño real de los datos: ni 200 tareas vacías ni unas pocas tareas gigantes.

[↑ Volver al índice](#Índice)

---
