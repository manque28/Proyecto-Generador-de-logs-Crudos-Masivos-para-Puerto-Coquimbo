# 07 Conclusiones

- **Esquema explicito (Implicancia 3):** `inferSchema` lanzo 1 job(s) y tardo 6.8 s en leer
  1.68 GiB solo para deducir tipos; el `StructType` no lanzo ninguno (0.19 s).
- **Calidad:** 10,000,000 eventos crudos, 10,000,000 limpios, 0 en cuarentena; 32 chequeos OK.
- **Shuffle:** se aplico la configuracion fijada 12 sin AQE (0.45 s); la mas rapida fue 6 sin AQE (0.45 s).
- **Parquet:** 39.8 MiB frente a 1,722.1 MiB de JSONL (43.3x), con poda por fecha verificada.
- **Sesgo:** con `faja_1` al 47.0%, la tarea rezagada leyo 5,214,599 filas; el salting en dos
  fases la bajo a 1,604,452 con el mismo resultado (1.21x).
- **Joins (Implicancia 7):** el join ingenuo por `sensor_id` produjo 10,486,486 filas (+486,486);
  el range join con `broadcast` conservo las 10,000,000 filas.
