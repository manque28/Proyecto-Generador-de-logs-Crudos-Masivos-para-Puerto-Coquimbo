<!-- ===== CELDA 2.1 · CONTEXTO · antes de Hito 1.4 ===== -->

<div id="Ingesta-con-esquema-declarado"></div>

<div style="display:flex;justify-content:space-between;align-items:center;margin:4px 0 2px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><span style="font-size:0.72em;text-transform:uppercase;letter-spacing:0.08em;color:#0F2E5C;font-weight:600;">Laboratorio Terminal Puerto Coquimbo · Sitio 3 · Programación Avanzada</span><span style="font-size:0.72em;letter-spacing:0.08em;font-weight:800;color:#0F2E5C;border:2px solid #0F2E5C;padding:3px 10px;">ULS · BIG DATA</span></div>

## <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:800;">Ingesta con </span><em style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#2F80ED;font-weight:700;">esquema declarado</em>

<div style="display:flex;flex-wrap:wrap;margin:12px 0 20px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><div style="flex:1;min-width:260px;background-color:#1E4FA3;color:#FFFFFF;padding:20px 22px;line-height:1.6;display:flex;gap:14px;align-items:flex-start;"><span style="display:inline-block;flex:0 0 30px;width:30px;height:30px;border-radius:50%;background-color:#FFFFFF;text-align:center;line-height:30px;font-weight:800;color:#1E4FA3;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">→</span><div><b>Qué hacemos:</b> con el clúster listo, cargamos los datos. Primero declaramos el esquema, después dejamos anotada la lectura y recién al final le pedimos a Spark el primer resultado.</div></div></div>

### <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:700;">Qué es el esquema</span>

Es decirle a Spark qué tipo de dato tiene cada columna. Si no se lo decimos, tiene que leer todos los archivos solo para adivinarlo, y lo que adivina puede cambiar según los datos que lleguen.

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Columna</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Tipo</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Por qué</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">timestamp</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Texto</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Se revisa como texto y se convierte a fecha en la limpieza.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">sensor_id</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">metric</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">unit</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Texto</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Nombres y etiquetas.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">value</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Número decimal</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">La medición. Si quedara como texto no se podría promediar.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">worker_id</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Número entero</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Proceso que generó la lectura.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">_corrupt_record</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Texto</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Guarda la línea completa si viene dañada.</td></tr></tbody></table>

Una línea dañada no se pierde ni detiene la lectura: queda guardada en `_corrupt_record` para revisarla después (modo `PERMISSIVE`).

### <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:700;">Evaluación perezosa</span>

Spark no trabaja hasta que le pedimos un resultado.

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;"></th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Qué hacen</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Ejemplos</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:center;">¿Spark trabaja?</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b>Transformaciones</b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Anotan un paso</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">read</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">filter</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">select</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">No</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b>Acciones</b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Piden un resultado</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">count</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">show</code>, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">collect</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">Sí</td></tr></tbody></table>

<div align="center">
<img src="img/evaluacion_perezosa.svg" alt="Las transformaciones se anotan; la acción da la orden y Spark ejecuta el plan completo" width="720"><br>
<em>Figura 3. Las transformaciones solo se anotan. Cuando llega una acción, Spark mira el plan completo, busca la forma más rápida de hacerlo y recién ahí lee los datos.</em>
</div>

<!-- ===== CELDA 2.2 · INTERPRETACIÓN · antes de Hito 1.5b ===== -->

**Lectura del resultado.** La celda anterior no hizo ningún trabajo: Spark solo anotó dónde leer y con qué esquema.

- `printSchema()` muestra los tipos **que nosotros declaramos**, no los que hay en los archivos.
- Hay **16 particiones**, una por archivo. Una partición es un trozo de datos que un executor procesa por su cuenta. Cada archivo pesa unos 76 MiB, menos que el máximo de 128 MiB por partición (`maxPartitionBytes`), así que cabe entero en una.

> **Nota.** El aviso `WARN FileStreamSink`, con su texto largo de Java, no es un error. Aparece porque la ruta usa un comodín (`*.jsonl`), y la lectura funciona normal.

La celda siguiente mide qué pasa si **no** declaramos el esquema.

<!-- ===== CELDA 2.2b · INTERPRETACIÓN · antes de Hito 1.6 ===== -->

### Lo que cuesta no declarar el esquema

| Lectura | Tiempo | Trabajos lanzados |
|:---|---:|:---:|
| Esquema adivinado (`inferSchema`) | 13,10 s | 1 |
| Esquema declarado (`StructType`) | 0,67 s | 0 |

Con `inferSchema`, Spark **leyó los 1,18 GiB completos** solo para adivinar los tipos, sin que le pidiéramos ningún resultado. Esa lectura no queda guardada: cuando pidamos el primer resultado, tendrá que leer todo otra vez. Con `StructType` la definición es inmediata y no lee nada.

Aquí la diferencia es de 12,4 s. Con terabytes, adivinar el esquema es **pagar dos veces la parte más lenta del proceso**.

Esta vez Spark adivinó bien (`value` como `double` y `worker_id` como `bigint`). Pero fue suerte: si mañana llega un archivo con `value` escrito como texto, el tipo adivinado cambiaría y los cálculos de más adelante fallarían. El esquema declarado no cambia.

Las dos celdas siguientes son las primeras **acciones**: `show(5)` lee solo lo justo para mostrar cinco filas, y `count()` es la primera que recorre todos los datos.

<!-- ===== CELDA 2.3 · INTERPRETACIÓN · antes de Hito 2 ===== -->

### La primera acción lee los 10 millones de filas

| Lo que medimos | Resultado |
|:---|---:|
| Registros leídos | 10.000.000 |
| Registros esperados | 10.000.000 |
| Tiempo de lectura + cache | 17,5 s |

El `assert` confirma que no se perdió ninguna línea.

La lectura completa tomó 17,5 s, y `inferSchema` había gastado 13,10 s solo en adivinar los tipos. O sea, sin esquema declarado la carga habría tomado 30,6 s: **1,7 veces** lo que tomó.

Usamos `.cache()` porque las secciones siguientes recorren los datos muchas veces. El cache guarda los datos ya leídos en la memoria de los executors. Sin él, cada acción tendría que volver a abrir y leer los 1,18 GiB de JSON.

> **Idea clave.** Declarar el esquema evita leer todo dos veces, y la evaluación perezosa deja que Spark vea el plan completo antes de ejecutarlo. Esto se ve con nuestros datos en el [diagnóstico del shuffle](#Diagnostico-del-shuffle).

[↑ Volver al índice](#Indice)

---
