<!-- ===== CELDA 8.1 · CONTEXTO · antes de Hito 6.3 ===== -->

## Joins distribuidos

**Qué hacemos:** cruzamos cada lectura con una tabla de **verdad de terreno**: ventanas de tiempo en que un equipo tuvo una falla conocida. Así cada lectura queda marcada como anomalía o como normal. La tabla `etiquetas` es **simulada** dentro del notebook para ejercitar el patrón, y tiene varias ventanas para un mismo equipo a propósito.

**Por qué importa en Big Data:** un *join* es una operación ancha. Las filas de las dos tablas con la misma clave tienen que encontrarse en el mismo executor, y Spark tiene dos formas de lograrlo:

| Estrategia | Cómo funciona | Cuándo conviene |
|:---|:---|:---|
| ***Sort-merge join*** | Hace *shuffle* de las **dos** tablas por la clave, las ordena y las recorre juntas. | Cuando las dos tablas son grandes. |
| ***Broadcast join*** | Copia la tabla chica **entera** a cada executor. La tabla grande no se mueve. | Cuando una tabla cabe holgada en la memoria de cada executor. |

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
| Ingenuo, solo por equipo | 10.486.486 | — | 0,7 s |
| ***Range join* con *broadcast*** | **10.000.000** | **216.218** | **0,5 s** |

El `assert` comprueba que el *range join* devuelve las mismas 10.000.000 de filas de entrada.

**Por qué 216.218 marcadas:**

| Ventanas | Qué cubren | Lecturas marcadas |
|:---|:---|---:|
| 4 de `REEFER_S3_10` | El período completo, sin superponerse | 162.162 |
| 1 de `FAJA_S3_C1` | La segunda mitad del período, 2 series × 27.028 instantes | 54.056 |
| **Total** | | **216.218** |

Las lecturas de `REEFER_S3_10` son exactamente las mismas 162.162 que el *join* ingenuo cuadruplicó. Ahora cada una calza con **una sola** ventana.

> **Idea clave.** En un *join* distribuido hay que decidir **qué se mueve** (*broadcast* de la tabla chica) y **verificar con un conteo** que no se fabricaron filas. Un *join* mal planteado no da error: entrega más filas de las que debería.

[↑ Volver al índice](#Índice)

---
