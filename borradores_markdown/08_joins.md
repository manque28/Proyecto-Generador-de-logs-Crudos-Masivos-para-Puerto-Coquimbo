<!-- ===== CELDA 8.1 · CONTEXTO · antes de Hito 6.3 ===== -->

<div id="Joins-distribuidos"></div>

<div style="display:flex;justify-content:space-between;align-items:center;margin:4px 0 2px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><span style="font-size:0.72em;text-transform:uppercase;letter-spacing:0.08em;color:#0F2E5C;font-weight:600;">Laboratorio Terminal Puerto Coquimbo · Sitio 3 · Programación Avanzada</span><span style="font-size:0.72em;letter-spacing:0.08em;font-weight:800;color:#0F2E5C;border:2px solid #0F2E5C;padding:3px 10px;">ULS · BIG DATA</span></div>

## <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:800;">Joins </span><em style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#2F80ED;font-weight:700;">distribuidos</em>

<div style="display:flex;flex-wrap:wrap;margin:12px 0 20px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><div style="flex:1;min-width:260px;background-color:#1E4FA3;color:#FFFFFF;padding:20px 22px;line-height:1.6;display:flex;gap:14px;align-items:flex-start;"><span style="display:inline-block;flex:0 0 30px;width:30px;height:30px;border-radius:50%;background-color:#FFFFFF;text-align:center;line-height:30px;font-weight:800;color:#1E4FA3;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">→</span><div><b>Qué hacemos:</b> cruzamos cada lectura con una tabla de <b>verdad de terreno</b>: ventanas de tiempo en que un equipo tuvo una falla conocida. Así cada lectura queda marcada como anomalía o como normal. La tabla <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">etiquetas</code> es <b>simulada</b> dentro del notebook para ejercitar el patrón, y tiene varias ventanas para un mismo equipo a propósito.</div></div><div style="flex:1;min-width:260px;background-color:#D6E4F5;color:#0F2E5C;padding:20px 22px;line-height:1.6;"><b>Por qué importa en Big Data:</b> un <i>join</i> es una operación ancha. Las filas de las dos tablas con la misma clave tienen que encontrarse en el mismo executor, y Spark tiene dos formas de lograrlo:</div></div>

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Estrategia</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Cómo funciona</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Cuándo conviene</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b><i>Sort-merge join</i></b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Hace <i>shuffle</i> de las <b>dos</b> tablas por la clave, las ordena y las recorre juntas.</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Cuando las dos tablas son grandes.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b><i>Broadcast join</i></b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Copia la tabla chica <b>entera</b> a cada executor. La tabla grande no se mueve.</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Cuando una tabla cabe holgada en la memoria de cada executor.</td></tr></tbody></table>

Nuestra tabla de etiquetas tiene 5 filas y la de lecturas 10 millones: mover los 10 millones por la red para cruzarlos con 5 filas sería absurdo. Por eso pedimos el *broadcast* de forma explícita, con `F.broadcast(etiquetas)`.

**El peligro: el *fan-out*.** Si el *join* se hace **solo por equipo** y ese equipo tiene varias ventanas de falla, cada lectura se cruza con todas las ventanas y aparece repetida una vez por cada una. El *join* fabrica filas que no existen, y no da ningún error.

**La solución: *range join*.** La condición exige el mismo equipo **y** que el instante de la lectura caiga dentro de la ventana:

```python
(lecturas.sensor_id == etiquetas.entidad_id)
& (lecturas.timestamp >= etiquetas.t_inicio)
& (lecturas.timestamp <  etiquetas.t_fin)
```

Las ventanas son semiabiertas, `[t_inicio, t_fin)`: un instante justo en el borde entre dos ventanas pertenece solo a la segunda. Así cada lectura calza con una ventana como máximo, y como es un *left join* ninguna se pierde. El conteo debe quedar **exactamente igual**.

<!-- ===== CELDA 8.2 · INTERPRETACIÓN · antes de Hito 6.3c ===== -->

### El join ingenuo fabricó 486.486 filas

La tabla tiene **4 ventanas consecutivas** para `REEFER_S3_10` (una por cada cuarto del período) y 1 para `FAJA_S3_C1`. Uniendo solo por `sensor_id`:

| | Filas |
|:---|---:|
| Lecturas originales | 10.000.000 |
| Lecturas de `REEFER_S3_10` | 162.162 |
| Esas mismas lecturas tras el *join* ingenuo (× 4 ventanas) | 648.648 |
| **Total tras el *join* ingenuo** | **10.486.486** |

Cada lectura de `REEFER_S3_10` aparece 4 veces, una por ventana: son **486.486 filas fantasma** (3 copias de más × 162.162). El `assert` de la celda confirma que el conteo es exactamente ese. Cualquier promedio o conteo calculado después estaría inflado, y nada en el resultado avisa que hay filas repetidas.

<!-- ===== CELDA 8.3 · INTERPRETACIÓN · antes de Hito 6.4 ===== -->

### El range join no fabricó ni perdió filas

| *Join* | Filas resultantes | Lecturas marcadas | Tiempo |
|:---|---:|---:|---:|
| Ingenuo, solo por equipo | 10.486.486 | — | 1,4 s |
| ***Range join* con *broadcast*** | **10.000.000** | **216.218** | **1,1 s** |

El `assert` comprueba que el *range join* devuelve las mismas 10.000.000 de filas de entrada.

**Por qué 216.218 marcadas:**

| Ventanas | Qué cubren | Lecturas marcadas |
|:---|:---|---:|
| 4 de `REEFER_S3_10` | El período completo, sin superponerse | 162.162 |
| 1 de `FAJA_S3_C1` | La segunda mitad del período, 2 series × 27.028 instantes | 54.056 |
| **Total** | | **216.218** |

Las lecturas de `REEFER_S3_10` son exactamente las mismas 162.162 que el *join* ingenuo cuadruplicó. Ahora cada una calza con **una sola** ventana.

> **Idea clave.** En un *join* distribuido hay que decidir **qué se mueve** (*broadcast* de la tabla chica) y **verificar con un conteo** que no se fabricaron filas. Un *join* mal planteado no da error: entrega más filas de las que debería.

[↑ Volver al índice](#Indice)

---
