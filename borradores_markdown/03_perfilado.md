<!-- ===== CELDA 3.1 · CONTEXTO · antes de Hito 2 ===== -->

<div id="Perfilado-de-calidad"></div>

<div style="display:flex;justify-content:space-between;align-items:center;margin:4px 0 2px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><span style="font-size:0.72em;text-transform:uppercase;letter-spacing:0.08em;color:#0F2E5C;font-weight:600;">Laboratorio Terminal Puerto Coquimbo · Sitio 3 · Programación Avanzada</span><span style="font-size:0.72em;letter-spacing:0.08em;font-weight:800;color:#0F2E5C;border:2px solid #0F2E5C;padding:3px 10px;">ULS · BIG DATA</span></div>

## <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:800;">Perfilado </span><em style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#2F80ED;font-weight:700;">de calidad</em>

<div style="display:flex;flex-wrap:wrap;margin:12px 0 20px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><div style="flex:1;min-width:260px;background-color:#1E4FA3;color:#FFFFFF;padding:20px 22px;line-height:1.6;display:flex;gap:14px;align-items:flex-start;"><span style="display:inline-block;flex:0 0 30px;width:30px;height:30px;border-radius:50%;background-color:#FFFFFF;text-align:center;line-height:30px;font-weight:800;color:#1E4FA3;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">→</span><div><b>Qué hacemos:</b> medimos el estado de los datos <b>sin modificar nada</b>. Son 27 chequeos, y cada uno compara lo medido con lo que el dominio dice que debería haber (69 equipos, 185 series, 5 métricas, una lectura cada 15 s).</div></div><div style="flex:1;min-width:260px;background-color:#D6E4F5;color:#0F2E5C;padding:20px 22px;line-height:1.6;"><b>Por qué importa en Big Data:</b> con 10 millones de filas nadie puede revisar los datos a ojo, y un <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">show()</code> enseña 20 filas de 10 millones. Si se limpia sin haber medido antes, después no hay forma de saber cuánto se perdió ni por qué. El perfilado es lo que permite decidir qué limpiar y justificarlo con números.</div></div>

Cada chequeo responde una pregunta concreta:

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:center;">Hito</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Pregunta</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Qué se mide</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">2.2</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">¿Cada línea es válida?</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Líneas corruptas, nulos, formato del timestamp, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">NaN</code> y valores físicamente imposibles</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">2.3</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">¿Están todos los equipos?</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Equipos, series, métricas y unidades</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">2.4</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">¿Hay lecturas repetidas?</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Duplicados por <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">(sensor_id, metric, timestamp)</code></td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">2.5</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">¿Falta alguna lectura?</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Huecos de 15 s en cada serie</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:center;vertical-align:top;">2.6</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">¿Los valores son razonables?</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Media, dispersión y percentiles por métrica</td></tr></tbody></table>

<div style="background-color:#EAF1FA;border-left:6px solid #2F80ED;color:#231F20;padding:14px 20px;margin:14px 0;line-height:1.55;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><i style="color:#2F80ED;font-weight:700;">Nota.</i> Cada chequeo es una pasada sobre los 10 millones de filas, así que conviene agruparlos. El hito 2.2 calcula sus 10 chequeos en <b>una sola agregación</b>, es decir, en un solo recorrido del dataset.</div>

<!-- ===== CELDA 3.2 · INTERPRETACIÓN · antes de Hito 2.7 ===== -->

### Un promedio global puede esconder dos poblaciones

La temperatura media de todo el dataset es **−7,04 °C**, pero ningún equipo mide eso. Al separar por familia aparecen dos grupos que no tienen nada que ver:

| Familia | Lecturas | Mínimo | Mediana | Máximo |
|:---|---:|---:|---:|---:|
| `AMB` (sensores ambientales) | 648.648 | 9,42 °C | 14,66 °C | 20,62 °C |
| `REEFER` (contenedores refrigerados) | 2.594.592 | −18,37 °C | −17,98 °C | 5,89 °C |

Pasa lo mismo con la corriente: la mediana es 7,52 A, pero el percentil 99 llega a 283 A, porque conviven equipos de consumo muy distinto.

Por eso el perfilado se hace **por métrica y por familia**, no con un `describe()` de toda la tabla. La tabla también deja ver algo que vale la pena seguir: hay contenedores refrigerados que llegan a 5,89 °C, lejos de su mediana de −17,98 °C.

<!-- ===== CELDA 3.3 · INTERPRETACIÓN · antes de Hito 3 ===== -->

### Resultado del perfilado: 27 de 27 chequeos correctos

| Bloque | Resultado | Tiempo |
|:---|:---|---:|
| Validez por línea | 0 corruptas · 0 nulos · 0 valores imposibles | 4,2 s |
| Dominio | 69 equipos · 185 series · 5 métricas con su unidad | 7,3 s |
| Duplicados | 0 claves repetidas | 12,5 s |
| Continuidad | 54.054 a 54.055 lecturas por serie · 0 huecos · 9,38 días | 10,1 s |
| Perfil de valores | 5 métricas perfiladas | 5,4 s |
| **Total** | **27 de 27 correctos** | **39,5 s** |

Dos cosas que muestran los tiempos:

- **Buscar duplicados es lo más caro (12,5 s)** aunque no encuentre ninguno: para saber si una lectura se repite hay que juntar todas las filas con la misma clave, y eso obliga a mover datos entre executors. Es el *shuffle* que analizamos en la [sección 5](#Diagnostico-del-shuffle).
- **La validez por línea es lo más barato (4,2 s)**: cada fila se revisa por sí sola, sin depender de ninguna otra.

Todo esto se midió sobre el cache: los 1.212,6 MiB de JSONL ocupan **199,6 MiB** en la memoria de los executors (16 de 16 particiones), así que ningún chequeo volvió a leer los archivos.

Además, cada chequeo detiene el notebook con un `assert` apenas falla: si llegan datos dañados, la ejecución se corta aquí y no en medio de la limpieza.

> **Idea clave.** El perfilado decide la limpieza. Como medimos 0 duplicados, la sección siguiente se salta la deduplicación y se ahorra un *shuffle* de 10 millones de filas.

[↑ Volver al índice](#Indice)

---
