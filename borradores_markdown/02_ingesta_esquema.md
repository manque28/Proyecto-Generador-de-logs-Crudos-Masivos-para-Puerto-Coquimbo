<!-- ===== CELDA 2.1 · CONTEXTO · antes de Hito 1.4 ===== -->

## Ingesta con esquema declarado

**Qué hacemos:** declaramos el esquema de los datos, definimos la lectura de los 16 archivos y recién al final ejecutamos la primera acción sobre el dataset completo.

**Por qué importa en Big Data:** aquí se juntan dos ideas.

**1. El esquema.** Si no le decimos a Spark qué tipo tiene cada columna, tiene que leer todos los archivos una vez solo para adivinarlo, y después otra vez para trabajar. Con 1,18 GiB es una espera; con terabytes es pagar la lectura dos veces. Además, un esquema adivinado puede cambiar de una ejecución a otra según los datos que lleguen. Declarado, los tipos son siempre los mismos.

| Columna | Tipo | Por qué |
|:---|:---|:---|
| `timestamp` | `String` | Primero se valida como texto; se convierte a fecha en la limpieza. |
| `sensor_id`, `metric`, `unit` | `String` | Identificadores y etiquetas. |
| `value` | `Double` | La medición. Si quedara como texto no se podría promediar ni comparar. |
| `worker_id` | `Long` | Proceso que generó la lectura. |
| `_corrupt_record` | `String` | Recibe la línea completa cuando no se puede interpretar. |

Leemos en modo `PERMISSIVE`: una línea dañada no bota la lectura ni se pierde, queda guardada en `_corrupt_record` para revisarla después.

**2. La evaluación perezosa.** Spark distingue dos tipos de instrucciones:

| | Qué hacen | Ejemplos | ¿Ejecutan algo? |
|:---|:---|:---|:---:|
| **Transformaciones** | Describen un paso | `read`, `filter`, `select`, `withColumn`, `groupBy` | No |
| **Acciones** | Piden un resultado | `count`, `show`, `collect`, `write` | Sí |

Las transformaciones solo se anotan. Cuando llega una acción, Spark ya conoce el plan completo y puede optimizarlo antes de mover un solo dato.

<!-- ===== CELDA 2.2 · INTERPRETACIÓN · antes de Hito 1.5b ===== -->

**Lectura del resultado.** La celda anterior no lanzó ningún job: Spark solo anotó de dónde leer y con qué esquema.

- `printSchema()` muestra los tipos **que declaramos**, no los que encontró en los archivos.
- Hay **16 particiones de lectura**, una por archivo: cada archivo pesa unos 85 MiB y cabe completo bajo el límite de 128 MiB por partición (`maxPartitionBytes`). Cada partición es una tarea que un executor puede tomar por separado.

> **Nota.** El aviso `WARN FileStreamSink` con su traza de Java no es un error. Aparece porque la ruta lleva un comodín (`*.jsonl`) y la lectura sigue con normalidad.

La celda siguiente mide qué habría pasado si **no** hubiéramos declarado el esquema.

<!-- ===== CELDA 2.2b · INTERPRETACIÓN · antes de Hito 1.6 ===== -->

### Lo que cuesta no declarar el esquema

| Lectura | Tiempo | Jobs lanzados |
|:---|---:|:---:|
| Esquema inferido (`inferSchema`) | 7,88 s | 1 |
| Esquema declarado (`StructType`) | 0,35 s | 0 |

Con `inferSchema`, Spark **recorrió los 1,18 GiB completos** solo para adivinar los tipos, y eso ocurrió antes de que pidiéramos cualquier resultado. Esa lectura no deja nada guardado: cuando llegue la primera acción habrá que leer todo de nuevo. Con el `StructType` la definición es instantánea y no lanza ningún job.

A esta escala son 7,5 s de diferencia. Con terabytes, inferir el esquema significa **pagar dos veces la lectura más cara del proceso**.

Aquí los tipos inferidos coincidieron con los declarados (`value` como `double`, `worker_id` como `bigint`). Pero eso es suerte de estos datos: si un día llegara un archivo con `value` escrito como texto, el esquema inferido cambiaría solo y los cálculos de más adelante fallarían. El esquema declarado no cambia.

Las dos celdas que siguen son las primeras **acciones**: `show(5)` lee solo lo necesario para mostrar cinco filas, y `count()` es la primera que recorre el dataset completo.

<!-- ===== CELDA 2.3 · INTERPRETACIÓN · antes de Hito 2 ===== -->

### La primera acción recorre los 10 millones de filas

| Lo que medimos | Resultado |
|:---|---:|
| Registros leídos | 10.000.000 |
| Registros esperados | 10.000.000 |
| Tiempo de lectura + cache | 7,9 s |

El `assert` confirma que no se perdió ninguna línea entre los archivos y Spark.

Esta lectura completa tomó 7,9 s, prácticamente lo mismo que los 7,88 s que `inferSchema` gastó solo en adivinar los tipos. Es decir, sin esquema declarado la ingesta habría costado **el doble**.

Usamos `.cache()` porque las secciones que siguen recorren el dataset muchas veces. Sin cache, cada acción volvería a abrir y a interpretar los 1,18 GiB de JSON; con cache, los executors guardan el resultado en su memoria y lo reutilizan.

> **Idea clave.** Declarar el esquema evita una lectura completa de más, y la evaluación perezosa permite que Spark vea todo el plan antes de ejecutarlo. Más adelante, en el plan del [diagnóstico del shuffle](#Diagnóstico-del-shuffle), se ve esa optimización con nuestros propios datos.

[↑ Volver al índice](#Índice)

---
