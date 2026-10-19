<!-- ===== CELDA 4.1 · CONTEXTO · antes de Hito 3 ===== -->

## Limpieza y cuarentena

**Qué hacemos:** le asignamos a cada línea un motivo de descarte (o ninguno), separamos las líneas limpias de las observadas, convertimos el timestamp a fecha y agregamos la familia del equipo.

**Por qué importa en Big Data:** borrar es irreversible y, a esta escala, invisible: nadie nota que faltan 50.000 filas entre 10 millones. Además, una lectura defectuosa también es información, porque dice algo sobre el sensor que la produjo. Por eso las líneas con problemas **se marcan y se apartan**, no se eliminan.

Cada línea recibe el primer motivo que le corresponda, en este orden:

| Orden | Motivo | Cuándo aplica |
|:---:|:---|:---|
| 1 | `corrupta` | La línea no se pudo interpretar como JSON |
| 2 | `nulo` | Falta algún campo |
| 3 | `timestamp invalido` | La fecha no existe o no tiene el formato esperado |
| 4 | `value NaN` | La medición no es un número |
| 5 | `fuera de rango fisico` | Corriente, vibración o peso negativos; humedad fuera de 0 a 100 % |

Las líneas marcadas van a una **cuarentena** (`salida_fase2/descartes/`) con su motivo. La limpieza solo se da por buena si el balance cierra:

$$
\text{crudos} = \text{limpios} + \text{cuarentena} + \text{duplicados}
$$

<!-- ===== CELDA 4.2 · INTERPRETACIÓN · antes de Hito 4 ===== -->

### El balance cierra: no se perdió ninguna fila

| | Filas |
|:---|---:|
| Registros crudos | 10.000.000 |
| Enviados a cuarentena | 0 |
| Duplicados quitados | 0 |
| **Registros limpios** | **10.000.000** |

En esta ejecución no hubo descartes, que es lo que el perfilado había anticipado. El mecanismo queda igual en su lugar: tres `assert` comprueban el balance, y si una ejecución futura trae líneas dañadas terminarán en la cuarentena con su motivo, no borradas.

**Qué cambió en los datos:**

- `timestamp` pasó de texto a tipo `timestamp`. Usamos `try_to_timestamp`, que ante una fecha inválida devuelve nulo en vez de abortar el job completo.
- Se agregó `asset_type`, la familia del equipo, sacada del prefijo de `sensor_id`.
- La deduplicación se omitió porque el perfilado midió 0 duplicados.

La verificación por familia confirma que siguen estando las 185 series:

| Familia | Series | Lecturas | Proporción |
|:---|---:|---:|---:|
| `REEFER` | 144 | 7.783.776 | 77,8 % |
| `AMB` | 24 | 1.297.296 | 13,0 % |
| `FAJA` | 12 | 648.658 | 6,5 % |
| `GRUA` | 4 | 216.216 | 2,2 % |
| `BASCULA` | 1 | 54.054 | 0,5 % |
| **Total** | **185** | **10.000.000** | **100 %** |

Toda la sección tomó 14,7 s. Al terminar se libera el cache de los datos crudos, y desde aquí el notebook trabaja sobre los datos limpios.

> **Idea clave.** A escala, limpiar es clasificar y demostrar con conteos que no se perdió nada, no borrar lo que molesta.

[↑ Volver al índice](#Índice)

---
