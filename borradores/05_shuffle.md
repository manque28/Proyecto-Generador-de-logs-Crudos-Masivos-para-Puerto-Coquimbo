# 05 Shuffle

## Hito 4: configuraciones de shuffle (mediana de 3 corridas, accion noop)

| Config | Mediana (s) | Shuffle (MiB) | Tareas por etapa |
|---|---|---|---|
| 200 sin AQE | 1.30 | 1.9 | [16, 200] |
| 200 con AQE | 0.55 | 1.9 | [16, 2] |
| 6 sin AQE | 0.53 | 1.2 | [16, 6] |
| 12 sin AQE | 0.51 | 1.2 | [16, 12] |

Configuracion elegida: **12 sin AQE** (2.56x frente a 200 sin AQE).

## Hito 6.2: sesgo fabricado y salting en dos fases

`faja_1` concentra 47.0% de las filas. Shuffle de filas completas (repartition por clave,
sin combiner), 12 particiones, AQE off, N_SAL = 16.

| Consulta | Mediana (s) | Tareas | Tarea mas cargada (filas) | Max tarea (ms) |
|---|---|---|---|---|
| sin salting | 1.45 | 12 | 5,214,599 (52.1%) | 747 |
| con salting | 1.14 | 12 | 1,605,409 (16.1%) | 274 |

Speedup del salting: 1.27x.
