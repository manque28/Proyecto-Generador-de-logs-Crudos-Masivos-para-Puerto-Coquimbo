<!-- ===== CELDA 0.1 · PORTADA · antes de Hito 1.1 ===== -->

# Fase 2 · Procesamiento distribuido con PySpark

**Laboratorio Terminal Puerto Coquimbo, Sitio 3** · Programación Avanzada

**Integrantes:** Pablo Manque · Ignacio Brizuela · Cristian Rojo · Mauricio Hernandez · Francisco Seura · Raul Muñoz

| Datos de entrada | Clúster | Salida |
|:---|:---|:---|
| 10.000.000 de lecturas de sensores<br>16 archivos `.jsonl` · 1,18 GiB | Spark 4.0.1 en Docker<br>1 master · 3 workers · driver en Jupyter | Parquet particionado por día<br>en `salida_fase2/` |

> **Idea central.** Todo lo que hacemos aquí está pensado para datos que **no caben en la memoria de una sola máquina**. Por eso cada decisión del notebook se respalda con una medición de nuestro propio clúster: un tiempo, un conteo o un plan de ejecución.

---

<!-- ===== CELDA 0.2 · ÍNDICE · antes de Hito 1.1 ===== -->

## Índice

| # | Sección | Hitos | Implicancia para Big Data | Expone |
|:---:|:---|:---:|:---|:---|
| 1 | [Clúster y procesamiento distribuido](#Clúster-y-procesamiento-distribuido) | 1.1 – 1.3 | 1 · Escalado horizontal: master, workers y driver | «COMPLETAR» |
| 2 | [Ingesta con esquema declarado](#Ingesta-con-esquema-declarado) | 1.4 – 1.6 | 2 · Evaluación perezosa<br>3 · Esquemas a escala | «COMPLETAR» |
| 3 | [Perfilado de calidad](#Perfilado-de-calidad) | 2 | 4 · Medir antes de limpiar | «COMPLETAR» |
| 4 | [Limpieza y cuarentena](#Limpieza-y-cuarentena) | 3 | 4 · Marcar en lugar de borrar | «COMPLETAR» |
| 5 | [Diagnóstico del shuffle](#Diagnóstico-del-shuffle) | 4 | 5 · Operaciones anchas, particiones y AQE | «COMPLETAR» |
| 6 | [Escritura en Parquet particionado](#Escritura-en-Parquet-particionado) | 5 | 8 · Almacenamiento columnar y *partition pruning* | «COMPLETAR» |
| 7 | [Sesgo de datos](#Sesgo-de-datos) | 6.1 – 6.2 | 6 · Tareas rezagadas y *salting* | «COMPLETAR» |
| 8 | [Joins distribuidos](#Joins-distribuidos) | 6.3 | 7 · *Broadcast*, *fan-out* y *range join* | «COMPLETAR» |
| 9 | [Conclusiones](#Conclusiones) | — | Las 8 implicancias con su evidencia | Todo el grupo |

El número de la columna «Implicancia» es el de la consigna; así se puede ubicar cada una aunque el notebook las trate en otro orden.

---
