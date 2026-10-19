<!-- ===== CELDA 7.1 · CONTEXTO · antes de Hito 6.1 ===== -->

## Sesgo de datos

**Qué hacemos:** buscamos si alguna clave concentra una parte desproporcionada de las filas, provocamos el caso que plantea la consigna (`faja_1` con el 47 % de los datos), lo vemos en la UI de Spark y lo mitigamos con *salting*.

**Por qué importa en Big Data:** una etapa termina recién cuando termina **su tarea más lenta**. Después de un *shuffle*, todas las filas de una misma clave van a parar a la misma partición. Si una clave tiene la mitad de los datos, una sola tarea hace la mitad del trabajo mientras los demás núcleos esperan sin hacer nada. Esa tarea es el *straggler* (tarea rezagada).

Lo grave es que **agregar más máquinas no lo arregla**: una clave no se puede repartir entre executors, así que con 6 núcleos o con 600 esa tarea tarda lo mismo.

| | Sin sesgo | Con sesgo |
|:---|:---|:---|
| Filas por tarea | Parecidas | Una tarea recibe muchas más que el resto |
| En la pestaña Stages | Duración máxima ≈ mediana | Duración máxima ≫ mediana |
| Agregar workers | Acelera la etapa | No ayuda: la clave grande sigue en una sola tarea |

**Cómo se mitiga: *salting*.** A la clave pesada se le agrega un número al azar (aquí de 0 a 15), lo que la parte en 16 sub-claves que sí se pueden repartir. Después se agrega en **dos fases**:

1. Por sub-clave, en paralelo, guardando la suma y el conteo de cada una.
2. Por la clave original, que ya trae solo 16 filas parciales.

El promedio final se calcula como suma total dividida por conteo total, así que da **exactamente** lo mismo que sin *salting*.

> **Nota.** AQE puede dividir particiones sesgadas por su cuenta, pero solo en los *joins* (`skewJoin`). En una agregación hay que hacerlo a mano, y por eso esta sección trabaja con AQE apagado.

<!-- ===== CELDA 7.2 · INTERPRETACIÓN · antes de Hito 6.2 ===== -->

**Una familia grande no es lo mismo que una clave grande.** La familia `REEFER` tiene el 77,8 % de las filas, pero repartidas en 48 equipos de unas 162 mil lecturas cada uno. Agrupando por equipo, el más cargado tiene apenas 3 veces las filas del menos cargado: **nuestros datos no tienen sesgo de clave**.

Por eso la celda siguiente **fabrica** el caso de la consigna. A cada fila se le calcula un hash, y el 47 % de ellas pasa a llamarse `faja_1`. Además, la consulta mueve las **filas completas** por la red (`repartition` por la clave antes de agregar). Si Spark pudiera resumir cada partición antes del *shuffle*, como en el hito 4, el sesgo quedaría escondido.

<!-- ===== CELDA 7.3 · INTERPRETACIÓN · antes de Hito 6.3 ===== -->

### La tarea rezagada, medida

`faja_1` concentra **4.698.974 filas (47,0 %)**. La misma agregación, con y sin *salting*, sobre 12 particiones:

| Lo que medimos | Sin *salting* | Con *salting* |
|:---|---:|---:|
| Filas de la tarea más cargada | 5.214.599 (52,1 %) | 1.605.409 (16,1 %) |
| Duración de la tarea más lenta | **1.142 ms** | **600 ms** |
| Duración mediana de las tareas | 151 ms | 288 ms |
| Tarea más lenta frente a la mediana | **7,6×** | 2,1× |
| Tiempo de la consulta (mediana de 3) | 2,41 s | **2,28 s** |

<div align="center">
<img src="img/ui_4040_sesgo_sin_salting.png" alt="Resumen de tareas de la etapa 169: mediana de 160 ms y máximo de 1,1 s con 5.214.599 filas" width="720"><br>
<em>Figura 4. Sin <em>salting</em> (etapa 169 en <code>localhost:4040</code>, captura de nuestra ejecución de referencia): la mediana de las tareas lee 486.848 filas en 160 ms, pero la más cargada lee 5.214.599 y tarda 1,1 s. Esa es la tarea rezagada.</em>
</div>

<div align="center">
<img src="img/ui_4040_sesgo_con_salting.png" alt="Resumen de tareas de la etapa 171: máximo de 0,6 s con 1.605.409 filas" width="720"><br>
<em>Figura 5. Con <em>salting</em> (etapa 171, captura de nuestra ejecución de referencia): la tarea más cargada baja a 1.605.409 filas y 0,6 s. Las tareas quedan mucho más parejas.</em>
</div>

**Qué muestran las cifras:**

- **Sin *salting*, una sola tarea hace más de la mitad del trabajo.** Lee el 52,1 % de las filas (todo `faja_1`, más las claves que el hash le asignó a la misma partición) y tarda 7,6 veces la mediana. Las otras 11 tareas terminan rápido y sus núcleos quedan esperando.
- **Con *salting*, la carga se reparte.** La tarea más cargada lee 3,2 veces menos filas y tarda 1,9 veces menos. Queda 2,1 veces sobre la mediana y no 7,6: las 16 sub-claves se reparten en 12 particiones, así que algunas comparten partición.
- **La consulta completa es 1,06 veces más rápida**, a pesar de que el *salting* agrega una segunda agregación. El `assert` de la celda confirma que las medias y los conteos por clave son **idénticos** a los de la versión sin *salting*.

> **Ojo.** El *salting* no es gratis: suma una etapa y un *shuffle* más. Conviene cuando la tarea rezagada pesa más que ese costo extra, es decir, cuando una clave tiene una parte grande de los datos.

> **Idea clave.** Con sesgo, el tiempo de una etapa lo pone la clave más grande, no el tamaño del clúster. Repartir mejor los datos sirve más que comprar más máquinas.

[↑ Volver al índice](#Índice)

---
