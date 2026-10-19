<!-- ===== CELDA 9.1 · CONCLUSIONES · antes de Cierre ===== -->

## Conclusiones

Cada implicancia de PySpark para Big Data, con el resultado de nuestro clúster que la respalda:

| # | Implicancia | Nuestro resultado | Hito |
|:---:|:---|:---|:---:|
| 1 | Procesamiento distribuido | 3 executors y 6 tareas en paralelo; `.collect()` solo sobre resúmenes de 5 o 16 filas | 1.3 |
| 2 | Evaluación perezosa | Definir la lectura no lanza ningún job; las celdas de limpieza se funden en una sola etapa del plan | 1.5 · 4.2 |
| 3 | Esquemas e ingesta | `inferSchema`: 13,10 s y 1 job solo para adivinar tipos; `StructType`: 0,67 s y 0 jobs. Sin esquema, la ingesta habría tomado 1,7 veces lo que tomó | 1.4 – 1.6 |
| 4 | Calidad de datos | 27 de 27 chequeos en 39,5 s; balance de limpieza verificado, 0 filas perdidas | 2 · 3 |
| 5 | Shuffling | Un `Exchange` en el plan; de 3,11 s a 1,16 s (2,68×) con 12 particiones sin AQE, y a 1,44 s con AQE | 4 |
| 6 | Sesgo de datos | Con `faja_1` al 47 %, la tarea rezagada tardó 7,6 veces la mediana; el *salting* en dos fases la redujo de 1.142 ms a 600 ms y aceleró la consulta 1,06×, con el mismo resultado | 6.2 |
| 7 | Joins distribuidos | El *join* ingenuo fabricó 486.486 filas; el *range join* con *broadcast* conservó las 10.000.000 (verificado con `assert`) | 6.3 |
| 8 | Almacenamiento columnar | 35,1× menos espacio; un día consultado en 0,26 s abriendo 1 de 10 carpetas | 5 |

Lo que tienen en común: en cada paso la decisión fue **leer, mover y guardar menos datos**. Con 10 millones de filas la diferencia se mide en segundos; con datos que no caben en una máquina, es la diferencia entre que el trabajo termine o no.

> **Nota.** La celda siguiente cierra la sesión de Spark y con ella desaparece la UI del puerto 4040.

[↑ Volver al índice](#Índice)
