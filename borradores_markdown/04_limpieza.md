<!-- ===== CELDA 4.1 · CONTEXTO · antes de Hito 3 ===== -->

<div id="Limpieza-y-cuarentena"></div>

<div style="display:flex;justify-content:space-between;align-items:center;margin:4px 0 2px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><span style="font-size:0.72em;text-transform:uppercase;letter-spacing:0.08em;color:#0F2E5C;font-weight:600;">Laboratorio Terminal Puerto Coquimbo · Sitio 3 · Programación Avanzada</span><span style="font-size:0.72em;letter-spacing:0.08em;font-weight:800;color:#0F2E5C;border:2px solid #0F2E5C;padding:3px 10px;">ULS · BIG DATA</span></div>

## <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:800;">Limpieza y </span><em style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#2F80ED;font-weight:700;">cuarentena</em>

<div style="display:flex;flex-wrap:wrap;margin:12px 0 20px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><div style="flex:1;min-width:260px;background-color:#1E4FA3;color:#FFFFFF;padding:20px 22px;line-height:1.6;display:flex;gap:14px;align-items:flex-start;"><span style="display:inline-block;flex:0 0 30px;width:30px;height:30px;border-radius:50%;background-color:#FFFFFF;text-align:center;line-height:30px;font-weight:800;color:#1E4FA3;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">→</span><div><b>Qué hacemos:</b> le asignamos a cada línea un motivo de descarte (o ninguno), separamos las líneas limpias de las observadas, convertimos el timestamp a fecha y agregamos la familia del equipo.</div></div><div style="flex:1;min-width:260px;background-color:#D6E4F5;color:#0F2E5C;padding:20px 22px;line-height:1.6;"><b>Por qué importa en Big Data:</b> borrar es irreversible y, a esta escala, invisible: nadie nota que faltan 50.000 filas entre 10 millones. Además, una lectura defectuosa también es información, porque dice algo sobre el sensor que la produjo. Por eso las líneas con problemas <b>se marcan y se apartan</b>, no se eliminan.</div></div>

Cada línea recibe el primer motivo que le corresponda, en este orden:

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:center;">Orden</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Motivo</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Cuándo aplica</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">1</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">corrupta</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">La línea no se pudo interpretar como JSON</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">2</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">nulo</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Falta algún campo</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">3</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">timestamp invalido</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">La fecha no existe o no tiene el formato esperado</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">4</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">value NaN</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">La medición no es un número</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">5</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">fuera de rango fisico</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Corriente, vibración o peso negativos; humedad fuera de 0 a 100 %</td></tr></tbody></table>

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

Toda la sección tomó 20,1 s. Al terminar se libera el cache de los datos crudos, y desde aquí el notebook trabaja sobre los datos limpios.

> **Idea clave.** A escala, limpiar es clasificar y demostrar con conteos que no se perdió nada, no borrar lo que molesta.

[↑ Volver al índice](#Indice)

---
