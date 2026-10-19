<!-- ===== CELDA 2.1 · CONTEXTO · antes de Hito 1.4 ===== -->

## Ingesta con esquema declarado

**Qué hacemos:** le decimos a Spark qué tipo de dato tiene cada columna (el *esquema*), le indicamos dónde están los 16 archivos y, al final, le pedimos el primer resultado.

**Por qué importa en Big Data:** aquí hay dos ideas.

**1. El esquema.** Si no le decimos a Spark qué tipo tiene cada columna, tiene que leer todos los archivos solo para adivinarlo, y después leerlos otra vez para trabajar. Con 1,18 GiB es una espera; con terabytes es pagar dos veces la lectura. Además, lo que adivina puede cambiar según los datos que lleguen. Si lo declaramos nosotros, los tipos son siempre los mismos.

| Columna | Tipo | Por qué |
|:---|:---|:---|
| `timestamp` | `String` (texto) | Primero se revisa como texto; en la limpieza se convierte a fecha. |
| `sensor_id`, `metric`, `unit` | `String` (texto) | Son nombres y etiquetas. |
| `value` | `Double` (número decimal) | Es la medición. Si fuera texto no se podría promediar ni comparar. |
| `worker_id` | `Long` (número entero) | Proceso que generó la lectura. |
| `_corrupt_record` | `String` (texto) | Guarda la línea completa cuando no se puede leer. |

Usamos el modo `PERMISSIVE`: si una línea viene dañada, la lectura no se cae ni la línea se pierde. Queda guardada en `_corrupt_record` para revisarla después.

**2. La evaluación perezosa.** Spark tiene dos tipos de instrucciones:

| | Qué hacen | Ejemplos | ¿Se ejecutan al tiro? |
|:---|:---|:---|:---:|
| **Transformaciones** | Describen un paso | `read`, `filter`, `select`, `withColumn`, `groupBy` | No |
| **Acciones** | Piden un resultado | `count`, `show`, `collect`, `write` | Sí |

Es como escribir una receta antes de cocinar: las transformaciones son los pasos anotados y la acción es la orden de empezar. Como Spark ve la receta completa antes de partir, puede buscar la forma más rápida de hacerla.

<!-- ===== CELDA 2.2 · INTERPRETACIÓN · antes de Hito 1.5b ===== -->

**Lectura del resultado.** La celda anterior no hizo ningún trabajo: Spark solo anotó dónde leer y con qué esquema.

- `printSchema()` muestra los tipos **que nosotros declaramos**, no los que hay en los archivos.
- Hay **16 particiones**, una por archivo. Una partición es un trozo de datos que un executor procesa por su cuenta. Cada archivo pesa unos 85 MiB, menos que el máximo de 128 MiB por partición (`maxPartitionBytes`), así que cabe entero en una.

> **Nota.** El aviso `WARN FileStreamSink`, con su texto largo de Java, no es un error. Aparece porque la ruta usa un comodín (`*.jsonl`), y la lectura funciona normal.

La celda siguiente mide qué pasa si **no** declaramos el esquema.

<!-- ===== CELDA 2.2b · INTERPRETACIÓN · antes de Hito 1.6 ===== -->

### Lo que cuesta no declarar el esquema

| Lectura | Tiempo | Trabajos lanzados |
|:---|---:|:---:|
| Esquema adivinado (`inferSchema`) | 7,88 s | 1 |
| Esquema declarado (`StructType`) | 0,35 s | 0 |

Con `inferSchema`, Spark **leyó los 1,18 GiB completos** solo para adivinar los tipos, sin que le pidiéramos ningún resultado. Esa lectura no queda guardada: cuando pidamos el primer resultado, tendrá que leer todo otra vez. Con `StructType` la definición es inmediata y no lee nada.

Aquí la diferencia es de 7,5 s. Con terabytes, adivinar el esquema es **pagar dos veces la parte más lenta del proceso**.

Esta vez Spark adivinó bien (`value` como `double` y `worker_id` como `bigint`). Pero fue suerte: si mañana llega un archivo con `value` escrito como texto, el tipo adivinado cambiaría y los cálculos de más adelante fallarían. El esquema declarado no cambia.

Las dos celdas siguientes son las primeras **acciones**: `show(5)` lee solo lo justo para mostrar cinco filas, y `count()` es la primera que recorre todos los datos.

<!-- ===== CELDA 2.3 · INTERPRETACIÓN · antes de Hito 2 ===== -->

### La primera acción lee los 10 millones de filas

| Lo que medimos | Resultado |
|:---|---:|
| Registros leídos | 10.000.000 |
| Registros esperados | 10.000.000 |
| Tiempo de lectura + cache | 7,9 s |

El `assert` confirma que no se perdió ninguna línea.

La lectura completa tomó 7,9 s, casi lo mismo que los 7,88 s que `inferSchema` gastó solo en adivinar los tipos. O sea, sin esquema declarado la carga habría tomado **el doble**.

Usamos `.cache()` porque las secciones siguientes recorren los datos muchas veces. El cache guarda los datos ya leídos en la memoria de los executors. Sin él, cada acción tendría que volver a abrir y leer los 1,18 GiB de JSON.

> **Idea clave.** Declarar el esquema evita leer todo dos veces, y la evaluación perezosa deja que Spark vea el plan completo antes de ejecutarlo. Esto se ve con nuestros datos en el [diagnóstico del shuffle](#Diagnóstico-del-shuffle).

[↑ Volver al índice](#Índice)

---
