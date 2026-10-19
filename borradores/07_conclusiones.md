# 07 Conclusiones

- **Esquema explicito (Implicancia 3):** `inferSchema` lanzo 1 job(s) y tardo 9.9 s en leer
  1.18 GiB solo para deducir tipos; el `StructType` no lanzo ninguno (0.48 s).
- **Calidad:** 10,000,000 eventos crudos, 10,000,000 limpios, 0 en cuarentena; 27 chequeos OK.
- **Shuffle:** se aplico la configuracion fijada 8 sin AQE (0.93 s); la mas rapida fue 4 sin AQE (0.87 s).
- **Parquet:** 34.2 MiB frente a 1,212.6 MiB de JSONL (35.5x), con poda por fecha verificada.
- **Sesgo:** con `faja_1` al 47.0%, la tarea rezagada leyo 5,243,278 filas; el salting en dos
  fases la bajo a 1,790,754 con el mismo resultado (0.96x).
- **Joins (Implicancia 7):** el join ingenuo por `sensor_id` produjo 10,486,486 filas (+486,486);
  el range join con `broadcast` conservo las 10,000,000 filas.
