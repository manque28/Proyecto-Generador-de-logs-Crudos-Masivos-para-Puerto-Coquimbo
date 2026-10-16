# 05 Shuffle

## Hito 4: configuraciones de shuffle (mediana de 3 corridas, accion noop)

| Config | Mediana (s) | Shuffle (MiB) | Tareas por etapa |
|---|---|---|---|
| 200 sin AQE | 4.62 | 1.9 | [16, 200] |
| 200 con AQE | 2.33 | 1.9 | [16, 2] |
| 6 sin AQE | 2.48 | 1.2 | [16, 6] |
| 12 sin AQE | 4.83 | 1.2 | [16, 12] |

Configuracion elegida: **200 con AQE** (1.98x frente a 200 sin AQE).

## Hito 6.2: sesgo fabricado y salting en dos fases

`faja_1` concentra 47.0% de las filas. Shuffle de filas completas (repartition por clave,
sin combiner), 200 particiones, AQE off, N_SAL = 16.

| Consulta | Mediana (s) | Tareas | Tarea mas cargada (filas) | Max tarea (ms) |
|---|---|---|---|---|
| sin salting | 7.36 | 200 | 4,784,996 (47.8%) | 3633 |
| con salting | 10.45 | 200 | 335,682 (3.4%) | 736 |

Speedup del salting: 0.70x.
