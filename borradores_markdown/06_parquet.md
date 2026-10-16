<!-- ===== CELDA 6.1 · CONTEXTO · antes de Hito 5 ===== -->

## Escritura en Parquet particionado

**Qué hacemos:** guardamos los datos limpios en formato Parquet, con una carpeta por día. Después los volvemos a leer y comprobamos que son idénticos a lo que escribimos.

**Por qué importa en Big Data:** el formato decide cuánto hay que leer en cada consulta futura.

| | JSONL (entrada) | Parquet (salida) |
|:---|:---|:---|
| Organización | Por filas, en texto | Por columnas, en binario |
| Para leer una columna | Hay que interpretar todas las líneas completas | Se lee solo esa columna |
| Tipos | Hay que declararlos o adivinarlos | Viajan guardados junto a los datos |
| Compresión | Repite el nombre de cada campo en cada línea | Comprime cada columna por separado |

Al **particionar**, Spark crea una carpeta por cada valor de la columna elegida. Una consulta que filtra por esa columna abre solo las carpetas que necesita y ni siquiera mira las demás. Eso se llama *partition pruning*.

Las tres decisiones de esta escritura:

| Decisión | Qué elegimos | Por qué |
|:---|:---|:---|
| Columna de partición | `fecha` (el día) | Son 10 carpetas. Por `timestamp` serían 54.055 carpetas con 185 filas cada una: miles de archivos diminutos. |
| Cómo reducir particiones | `coalesce(6)` | Une particiones que ya existen, **sin *shuffle***. `repartition` movería los 10 millones de filas por la red. |
| Orden dentro de cada partición | Por fecha, serie y timestamp | Los valores parecidos quedan juntos y se comprimen mejor. |

> **Nota.** `repartition` sí conviene cuando hay que **aumentar** el número de particiones o volver a equilibrar datos muy desparejos. Para reducir, `coalesce` es más barato.

<!-- ===== CELDA 6.2 · INTERPRETACIÓN · antes de Hito 5.3 ===== -->

### Lo que quedó en disco

```text
salida_fase2/
├── descartes/                  cuarentena de la limpieza (0 filas)
└── eventos_limpios/
    ├── _SUCCESS                marca de escritura completa
    ├── fecha=2026-01-01/       6 archivos .parquet
    ├── fecha=2026-01-02/       6 archivos .parquet
    ├── ...
    └── fecha=2026-01-10/       6 archivos .parquet
```

| Lo que medimos | Resultado |
|:---|---:|
| Carpetas de partición | 10 |
| Archivos Parquet | 60 |
| Volumen en Parquet | 34,5 MiB |
| Volumen original en JSONL | 1.212,6 MiB |
| **Reducción** | **35,2×** |
| Tiempo de escritura | 12,9 s |

Son 60 archivos porque cada una de las 6 tareas de escritura deja un archivo por día (6 × 10). Los mismos 10 millones de lecturas ocupan 35 veces menos.

<!-- ===== CELDA 6.3 · INTERPRETACIÓN · antes de Hito 5.5 ===== -->

### Relectura verificada

Escribir no basta: releemos la salida y la comparamos con los datos limpios que teníamos en memoria.

| Verificación | Resultado | Comprobado con `assert` |
|:---|:---|:---:|
| Conteo de registros | 10.000.000, igual al original | Sí |
| Columnas | Las mismas 7, más `fecha` | Sí |
| Suma de control | Misma suma de `value`, mismo período y 185 series | Sí |

Contar los 10 millones de filas desde Parquet tomó **2,2 s**. La primera lectura del JSONL había tomado 7,9 s, aunque esa además cargaba el cache.

### La poda de particiones, medida

Consultamos un solo día, el 6 de enero:

| Lo que medimos | Resultado |
|:---|---:|
| Filas del día | 1.065.600 |
| Tiempo | 0,12 s |
| Carpetas abiertas | 1 de 10 |

El plan lo confirma con `PartitionFilters: [fecha = 2026-01-06]`: Spark descartó las otras nueve carpetas antes de leer un solo byte. El conteo además calza con lo esperado: 185 series × 5.760 lecturas diarias (una cada 15 s) = 1.065.600.

> **Idea clave.** En Big Data la consulta más rápida es la que no lee lo que no necesita. Parquet evita leer columnas de más y el particionado por día evita leer días de más.

[↑ Volver al índice](#Índice)

---
