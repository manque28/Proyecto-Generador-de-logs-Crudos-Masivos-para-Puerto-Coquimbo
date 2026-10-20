<!-- ===== CELDA 1.1 · CONTEXTO · antes de Hito 1.1 ===== -->

<div id="Cluster-y-procesamiento-distribuido"></div>

<div style="display:flex;justify-content:space-between;align-items:center;margin:4px 0 2px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><span style="font-size:0.72em;text-transform:uppercase;letter-spacing:0.08em;color:#0F2E5C;font-weight:600;">Laboratorio Terminal Puerto Coquimbo · Sitio 3 · Programación Avanzada</span><span style="font-size:0.72em;letter-spacing:0.08em;font-weight:800;color:#0F2E5C;border:2px solid #0F2E5C;padding:3px 10px;">ULS · BIG DATA</span></div>

## <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:800;">Clúster y </span><em style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#2F80ED;font-weight:700;">procesamiento distribuido</em>

<div style="display:flex;flex-wrap:wrap;margin:12px 0 20px 0;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><div style="flex:1;min-width:260px;background-color:#1E4FA3;color:#FFFFFF;padding:20px 22px;line-height:1.6;display:flex;gap:14px;align-items:flex-start;"><span style="display:inline-block;flex:0 0 30px;width:30px;height:30px;border-radius:50%;background-color:#FFFFFF;text-align:center;line-height:30px;font-weight:800;color:#1E4FA3;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">→</span><div><b>Qué hacemos:</b> encendemos un clúster de Spark y abrimos la sesión desde la que trabaja todo el notebook.<br><br>Un clúster es un grupo de máquinas que trabajan juntas. En nuestro caso todo corre en un solo computador, y cada «máquina» es un contenedor de Docker.</div></div><div style="flex:1;min-width:260px;background-color:#D6E4F5;color:#0F2E5C;padding:20px 22px;line-height:1.6;"><b>Por qué importa en Big Data:</b> un solo computador tiene un límite. Se le puede poner más memoria y más núcleos (<i>escalado vertical</i>), pero en algún momento no se puede más o sale demasiado caro. Spark hace lo contrario: reparte el trabajo entre varias máquinas (<i>escalado horizontal</i>). Si los datos crecen, no compramos una máquina más grande: agregamos más máquinas.</div></div>

### <span style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;color:#0F2E5C;font-weight:700;">Quién hace qué</span>

<table style="width:100%;border-collapse:collapse;margin:10px 0 18px 0;font-size:0.95em;"><thead><tr><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Rol</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Contenedor</th><th style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#0F2E5C;color:#FFFFFF;font-weight:600;padding:10px 14px;border:none;text-align:left;">Qué hace</th></tr></thead><tbody><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b>Driver</b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">jupyter</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Es este notebook. Divide el trabajo en tareas y junta los resultados. <b>No procesa los datos.</b></td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b>Master</b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">spark-master</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#EAF1FA;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">Sabe cuántos workers hay y qué núcleos y memoria tiene cada uno.</td></tr><tr><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><b>Workers</b></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;"><code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">spark-worker-1</code> a <code style="font-family:'JetBrains Mono',Consolas,Menlo,monospace;font-size:0.88em;background-color:#FFFFFF;color:#0F2E5C;border:1px solid #D6E4F5;padding:1px 6px;border-radius:3px;">spark-worker-3</code></td><td style="font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;background-color:#FFFFFF;color:#231F20;padding:10px 14px;border:none;text-align:left;vertical-align:top;">En cada uno corre un <i>executor</i>, que es el que de verdad procesa las filas.<br><span style="display:inline-block;margin-top:6px;font-size:0.9em;color:#2F80ED;font-style:italic;">Los núcleos y la memoria de cada worker los fija el archivo <code>.env</code>; su executor ejecuta una tarea por núcleo a la vez. Los valores de esta ejecución aparecen más abajo.</span></td></tr></tbody></table>

<div align="center">
<img src="img/arquitectura_cluster.svg" alt="Diagrama del clúster: driver, master, tres workers y carpeta compartida" width="960"><br>
<em>Figura 1. Nuestro clúster: el driver pide recursos al master, el master lanza un executor en cada worker y los executors leen los datos directo de la carpeta compartida.</em>
</div>

<div style="background-color:#EAF1FA;border-left:6px solid #2F80ED;color:#231F20;padding:14px 20px;margin:14px 0;line-height:1.55;font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><i style="color:#2F80ED;font-weight:700;">Nota.</i> Los tres workers comparten la misma carpeta. Así cada executor abre sus propios archivos, sin pedírselos al driver.</div>

<!-- ===== CELDA 1.2 · INTERPRETACIÓN + CONTEXTO · antes de Hito 1.3 ===== -->

**Lectura del resultado.** Hay **16 archivos** de unos 76 MiB cada uno, **1,18 GiB** en total. Aquí solo revisamos nombres y tamaños; todavía no se lee ninguna fila.

### Tamaño del clúster

Antes de encender el clúster hay que comprobar que cabe en la memoria que tiene Docker. La regla es simple: la memoria de todos los workers más la del driver tiene que ser menor que la memoria de Docker.

$$
\text{workers} \times \text{memoria por worker} + \text{memoria del driver} < \text{RAM de Docker}
$$

Con nuestros números:

$$
3 \times 2\,\text{GB} + 2\,\text{GB} = 8\,\text{GB} < 11{,}7\,\text{GB}
$$

Estos valores se configuran en el archivo `.env`:

| Variable del `.env` | Valor |
|:---|---:|
| `SPARK_WORKERS` | 3 |
| `SPARK_WORKER_CORES` | 2 |
| `SPARK_WORKER_MEMORY` | 2g |
| `SPARK_EXECUTOR_MEMORY` | 2g |
| `SPARK_DRIVER_MEMORY` | 2g |

Docker tiene 11,7 GB en nuestro equipo (lo vimos con `docker info --format "{{.MemTotal}}"`). Es el perfil de 12 GB de la tabla del `README`. Sobran 3,7 GB para el sistema y los contenedores.

> **Atención.** `SPARK_EXECUTOR_MEMORY` no puede ser mayor que `SPARK_WORKER_MEMORY`. Si el executor pide más memoria de la que tiene su worker, el clúster enciende igual, pero con **0 executors**, y nada avanza.

<!-- ===== CELDA 1.3 · INTERPRETACIÓN · antes de Hito 1.4 ===== -->

### El clúster funciona

| Lo que medimos | Resultado | Qué significa |
|:---|:---:|:---|
| Executors activos | **3 de 3** | Los tres workers están conectados y listos. |
| Paralelismo | **6** | 3 workers × 2 núcleos: Spark puede hacer hasta 6 tareas a la vez. |
| Master | `spark://spark-master:7077` | El notebook usa el clúster, no solo el computador local. |

La celda termina con un `assert`, que es una revisión automática: si falta algún executor, el notebook se detiene ahí en vez de seguir con menos recursos de los que creemos tener.

<div align="center">
<img src="img/ui_8080_workers.png" alt="UI del master en el puerto 8080 con los tres workers registrados" width="720"><br>
<em>Figura 2. Página del master (<code>localhost:8080</code>), captura de nuestra ejecución de referencia: tres workers activos (ALIVE), con 2 núcleos y 2 GiB cada uno, y el notebook (<code>fase2-sitio3</code>) usando los 6 núcleos.</em>
</div>

**Prueba rápida.** Antes de abrir el notebook corremos `verificar_cluster.py`, que revisa cuatro cosas: que el driver se conecta al master, que hay executors, que todos ven los datos y que se pueden leer completos.

```text
$ docker compose exec jupyter python3 verificar_cluster.py
[1/4] Sesion creada
      Spark   : 4.0.1
      Python  : 3.10.12
      Master  : spark://spark-master:7077
[2/4] Executors vivos : 3
      Paralelismo     : 6 tareas en paralelo
[3/4] Visibilidad de /opt/workspace/data/raw/w16 desde los executors:
      9619bdc030de                   ve los datos (16 archivos)
      bb5897aff8ff                   ve los datos (16 archivos)
      db1a08059c20                   ve los datos (16 archivos)
[4/4] Leyendo los datos crudos de la Fase 1...
      Registros leidos : 10,000,000
      Particiones      : 16
```

El paso 3 es el más importante: **cada worker** revisa por su cuenta que ve la carpeta (los tres códigos son los nombres de los workers). Si uno no la viera, el notebook fallaría más adelante, a mitad de una lectura.

### Por qué no usar `.collect()` con millones de filas

`.collect()` trae **todas** las filas al driver, que es un solo proceso. Hacerlo con 10 millones de lecturas es volver al límite de un solo computador, justo lo que el clúster evita. Lo más probable es que el driver se quede sin memoria y se caiga.

En este notebook solo usamos `.collect()` con resultados **ya resumidos** por los executors: 5 filas (una por métrica) o 16 filas (una por archivo). El trabajo pesado lo hace el clúster y al driver solo le llega la respuesta.

> **Idea clave.** El driver organiza y los executors trabajan. Si los datos no caben en una máquina, tampoco caben en el driver.

[↑ Volver al índice](#Indice)

---
