<!-- ===== CELDA 5.1 · CONTEXTO · antes de Hito 4 ===== -->

<div id="Diagnostico-del-shuffle"></div>

<div style="display:flex;justify-content:space-between;align-items:center;margin:4px 0 2px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><span style="font-size:0.72em;text-transform:uppercase;letter-spacing:0.08em;color:#0F2E5C;font-weight:600;">Laboratorio Terminal Puerto Coquimbo · Sitio 3 · Programación Avanzada</span><span style="font-size:0.72em;letter-spacing:0.08em;font-weight:800;color:#0F2E5C;border:2px solid #0F2E5C;padding:3px 10px;">ULS · BIG DATA</span></div>

## <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:800;">Diagnóstico </span><em style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#2F80ED;font-weight:700;">del shuffle</em>

<div style="display:flex;flex-wrap:wrap;margin:12px 0 20px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><div style="flex:1;min-width:260px;background-color:#1E4FA3;color:#FFFFFF;padding:20px 22px;line-height:1.6;display:flex;gap:14px;align-items:flex-start;"><span style="display:inline-block;flex:0 0 30px;width:30px;height:30px;border-radius:50%;background-color:#FFFFFF;text-align:center;line-height:30px;font-weight:800;color:#1E4FA3;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">→</span><div><b>Qué hacemos:</b> tomamos una consulta real (el resumen por hora de cada serie), leemos su plan físico y medimos la misma consulta con cuatro configuraciones de particiones.</div></div><div style="flex:1;min-width:260px;background-color:#D6E4F5;color:#0F2E5C;padding:20px 22px;line-height:1.6;"><b>Por qué importa en Big Data:</b> no todas las operaciones cuestan lo mismo en un clúster.</div></div>

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Tipo</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Ejemplos</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Qué necesita</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b>Estrecha</b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">filter</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">select</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">withColumn</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Cada partición se procesa sola, en el executor donde ya está.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b>Ancha</b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">groupBy</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">dropDuplicates</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">orderBy</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">join</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Juntar filas de la misma clave que están en particiones distintas.</td></tr></tbody></table>

Para juntar esas filas Spark hace un *shuffle*: cada executor ordena sus datos por clave, los escribe, los envía por la red y otro executor los vuelve a leer. Es lo más caro de un job, porque todo lo demás ocurre en memoria dentro de una misma máquina.

Dos ajustes controlan ese costo:

- `spark.sql.shuffle.partitions`: en cuántas particiones quedan los datos después del *shuffle*. Por defecto son **200**.
- **AQE** (*Adaptive Query Execution*): Spark mira el tamaño real de los datos mientras ejecuta y corrige el plan, por ejemplo uniendo particiones que quedaron casi vacías.

<div style="background-color:#EAF1FA;border-left:6px solid #2F80ED;color:#231F20;padding:14px 20px;margin:14px 0;line-height:1.55;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><i style="color:#2F80ED;font-weight:700;">Nota.</i> Cada configuración se mide con la mediana de 3 corridas y con una escritura <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">noop</code>, que ejecuta la consulta completa pero no guarda nada. Así medimos solo el cómputo.</div>

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
| 200 sin AQE (valor por defecto) | 3,11 s | 16 → 200 | 1,9 MiB | 1,00× |
| 200 con AQE | 1,44 s | 16 → 2 | 1,9 MiB | 2,16× |
| 6 sin AQE (1× núcleos) | 1,21 s | 16 → 6 | 1,2 MiB | 2,58× |
| **12 sin AQE** (2× núcleos) | **1,16 s** | 16 → 12 | 1,2 MiB | **2,68×** |

**Por qué 200 es lento aquí.** El *shuffle* mueve solo 1,9 MiB. Repartido en 200 particiones son unos 10 KiB por tarea: 200 tareas casi vacías, donde se gasta más tiempo en lanzarlas y coordinarlas que en procesar datos.

<div align="center">
<img src="img/ui_4040_stages.png" alt="Detalle de un job en la UI de Spark: etapa de 16 tareas y etapa de shuffle de 200 tareas" width="720"><br>
<em>Figura 3. Un job de la configuración «200 sin AQE» en <code>localhost:4040</code> (captura de nuestra ejecución de referencia). La etapa 1 lee 164 MiB del cache con 16 tareas; la etapa 2 usa 200 tareas para leer apenas 1.988 KiB de <em>shuffle</em>.</em>
</div>

**Qué resuelve AQE.** Con las mismas 200 particiones configuradas, AQE mide el tamaño real después de la etapa 1 y las une en **2**. El tiempo baja de 3,11 s a 1,44 s sin que tengamos que adivinar el número correcto.

**El ajuste manual y AQE llegan a tiempos parecidos.** Con 6 o 12 particiones, una o dos por núcleo, cada tarea tiene trabajo real y no sobra ninguna. Las tres configuraciones ajustadas quedan dentro de 0,27 s (1,16 s, 1,21 s y 1,44 s), y en ejecuciones anteriores el orden entre ellas cambió. La conclusión no depende de cuál gane: **lo que hay que evitar son las 200 tareas casi vacías**, y para eso sirve tanto ajustar el número a los núcleos como dejar que AQE lo ajuste solo.

**Por qué el *shuffle* pesa tan poco.** Gracias a la agregación parcial del paso 2, por la red viajan los resúmenes por serie y hora, no los 10 millones de filas.

El hito 4.4 aplica **12 particiones sin AQE** al resto del notebook. Esa configuración está fijada (dos particiones por núcleo) para que las ejecuciones del grupo sean comparables, y en esta ejecución también fue la más rápida.

> **Atención.** Ese número sirve para este volumen de datos. Si los datos crecen, un valor fijo se queda corto; por eso AQE es la opción segura cuando no se conoce de antemano el tamaño del *shuffle*.

> **Idea clave.** El *shuffle* es el costo que hay que vigilar, y el número de particiones tiene que calzar con el tamaño real de los datos: ni 200 tareas vacías ni unas pocas tareas gigantes.

[↑ Volver al índice](#Indice)

---
