<!-- ===== CELDA 6.1 · CONTEXTO · antes de Hito 5 ===== -->

<div id="Escritura-en-Parquet-particionado"></div>

<div style="display:flex;justify-content:space-between;align-items:center;margin:4px 0 2px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><span style="font-size:0.72em;text-transform:uppercase;letter-spacing:0.08em;color:#0F2E5C;font-weight:600;">Laboratorio Terminal Puerto Coquimbo · Sitio 3 · Programación Avanzada</span><span style="font-size:0.72em;letter-spacing:0.08em;font-weight:800;color:#0F2E5C;border:2px solid #0F2E5C;padding:3px 10px;">ULS · BIG DATA</span></div>

## <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:800;">Escritura en </span><em style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#2F80ED;font-weight:700;">Parquet particionado</em>

<div style="display:flex;flex-wrap:wrap;margin:12px 0 20px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><div style="flex:1;min-width:260px;background-color:#1E4FA3;color:#FFFFFF;padding:20px 22px;line-height:1.6;display:flex;gap:14px;align-items:flex-start;"><span style="display:inline-block;flex:0 0 30px;width:30px;height:30px;border-radius:50%;background-color:#FFFFFF;text-align:center;line-height:30px;font-weight:800;color:#1E4FA3;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">→</span><div><b>Qué hacemos:</b> guardamos los datos limpios en formato Parquet, con una carpeta por día. Después los volvemos a leer y comprobamos que son idénticos a lo que escribimos.</div></div><div style="flex:1;min-width:260px;background-color:#D6E4F5;color:#0F2E5C;padding:20px 22px;line-height:1.6;"><b>Por qué importa en Big Data:</b> el formato decide cuánto hay que leer en cada consulta futura.</div></div>

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;"></th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">JSONL (entrada)</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Parquet (salida)</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Organización</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Por filas, en texto</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Por columnas, en binario</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Para leer una columna</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Hay que interpretar todas las líneas completas</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Se lee solo esa columna</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Tipos</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Hay que declararlos o adivinarlos</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Viajan guardados junto a los datos</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Compresión</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Repite el nombre de cada campo en cada línea</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Comprime cada columna por separado</td></tr></tbody></table>

Al **particionar**, Spark crea una carpeta por cada valor de la columna elegida. Una consulta que filtra por esa columna abre solo las carpetas que necesita y ni siquiera mira las demás. Eso se llama *partition pruning*.

Las tres decisiones de esta escritura:

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Decisión</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Qué elegimos</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Por qué</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Columna de partición</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">fecha</code> (el día)</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Son 10 carpetas. Por <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">timestamp</code> serían 54.055 carpetas con 185 filas cada una: miles de archivos diminutos.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Cómo reducir particiones</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">coalesce(n)</code>, con n = núcleos del clúster</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Une particiones que ya existen, <b>sin <i>shuffle</b></i>. <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">repartition</code> movería los 10 millones de filas por la red.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Orden dentro de cada partición</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Por fecha, serie y timestamp</td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Los valores parecidos quedan juntos y se comprimen mejor.</td></tr></tbody></table>

<div style="background-color:#EAF1FA;border-left:6px solid #2F80ED;color:#231F20;padding:14px 20px;margin:14px 0;line-height:1.55;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><i style="color:#2F80ED;font-weight:700;">Nota.</i> <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">repartition</code> sí conviene cuando hay que <b>aumentar</b> el número de particiones o volver a equilibrar datos muy desparejos. Para reducir, <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">coalesce</code> es más barato.</div>

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
| **Reducción** | **35,1×** |
| Tiempo de escritura | 27,9 s |

Son 60 archivos porque cada una de las 6 tareas de escritura deja un archivo por día (6 × 10). Los mismos 10 millones de lecturas ocupan 35 veces menos.

<!-- ===== CELDA 6.3 · INTERPRETACIÓN · antes de Hito 5.5 ===== -->

### Relectura verificada

Escribir no basta: releemos la salida y la comparamos con los datos limpios que teníamos en memoria.

| Verificación | Resultado | Comprobado con `assert` |
|:---|:---|:---:|
| Conteo de registros | 10.000.000, igual al original | Sí |
| Columnas | Las mismas 7, más `fecha` | Sí |
| Suma de control | Misma suma de `value`, mismo período y 185 series | Sí |

Contar los 10 millones de filas desde Parquet tomó **4,4 s**. La primera lectura del JSONL había tomado 17,5 s, aunque esa además cargaba el cache.

### La poda de particiones, medida

Consultamos un solo día, el 6 de enero:

| Lo que medimos | Resultado |
|:---|---:|
| Filas del día | 1.065.600 |
| Tiempo | 0,26 s |
| Carpetas abiertas | 1 de 10 |

El plan lo confirma con `PartitionFilters: [fecha = 2026-01-06]`: Spark descartó las otras nueve carpetas antes de leer un solo byte. El conteo además calza con lo esperado: 185 series × 5.760 lecturas diarias (una cada 15 s) = 1.065.600.

> **Idea clave.** En Big Data la consulta más rápida es la que no lee lo que no necesita. Parquet evita leer columnas de más y el particionado por día evita leer días de más.

[↑ Volver al índice](#Indice)

---
