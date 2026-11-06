# 05 Shuffle

## Hito 4: configuraciones de shuffle (mediana de 3 corridas, accion noop)

| Config | Mediana (s) | Shuffle (MiB) | Tareas por etapa |
|---|---|---|---|
| 200 sin AQE | 1.06 | 2.0 | [16, 200] |
| 200 con AQE | 0.51 | 2.0 | [16, 2] |
| 6 sin AQE | 0.45 | 1.2 | [16, 6] |
| 12 sin AQE | 0.45 | 1.3 | [16, 12] |

Configuracion elegida: **12 sin AQE** (2.35x frente a 200 sin AQE).

## Hito 6.2: sesgo fabricado y salting en dos fases

`faja_1` concentra 47.0% de las filas. Shuffle de filas completas (repartition por clave,
sin combiner), 12 particiones, AQE off, N_SAL = 16.

| Consulta | Mediana (s) | Tareas | Tarea mas cargada (filas) | Max tarea (ms) |
|---|---|---|---|---|
| sin salting | 1.22 | 12 | 5,214,599 (52.1%) | 726 |
| con salting | 1.01 | 12 | 1,604,452 (16.0%) | 264 |

Speedup del salting: 1.21x.
