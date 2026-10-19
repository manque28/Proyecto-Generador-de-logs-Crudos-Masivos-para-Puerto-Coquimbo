# 05 Shuffle

## Hito 4: configuraciones de shuffle (mediana de 3 corridas, accion noop)

| Config | Mediana (s) | Shuffle (MiB) | Tareas por etapa |
|---|---|---|---|
| 200 sin AQE | 1.89 | 1.9 | [16, 200] |
| 200 con AQE | 1.04 | 1.9 | [16, 2] |
| 4 sin AQE | 0.87 | 1.2 | [16, 4] |
| 8 sin AQE | 0.93 | 1.2 | [16, 8] |

Configuracion elegida: **8 sin AQE** (2.04x frente a 200 sin AQE).

## Hito 6.2: sesgo fabricado y salting en dos fases

`faja_1` concentra 47.0% de las filas. Shuffle de filas completas (repartition por clave,
sin combiner), 8 particiones, AQE off, N_SAL = 16.

| Consulta | Mediana (s) | Tareas | Tarea mas cargada (filas) | Max tarea (ms) |
|---|---|---|---|---|
| sin salting | 1.60 | 8 | 5,243,278 (52.4%) | 792 |
| con salting | 1.67 | 8 | 1,790,754 (17.9%) | 404 |

Speedup del salting: 0.96x.
