<!-- ===== CELDA 1.1 · CONTEXTO · antes de Hito 1.1 ===== -->

## Clúster y procesamiento distribuido

**Qué hacemos:** encendemos un clúster de Spark, es decir, un grupo de máquinas que trabajan juntas, y conectamos este notebook a él.

**Por qué importa en Big Data:** un solo computador tiene un límite. Se le puede poner más memoria y más núcleos (*escalado vertical*), pero llega un momento en que no se puede más o sale demasiado caro. Spark hace lo contrario: reparte el trabajo entre varias máquinas (*escalado horizontal*). Si los datos crecen, se agregan más máquinas en vez de comprar una más grande.

Es como una cocina: el jefe de cocina reparte los pedidos, el encargado sabe cuántos cocineros hay disponibles, y los cocineros preparan los platos. En nuestro clúster:

| Rol | Contenedor | Qué hace |
|:---|:---|:---|
| **Driver** (jefe de cocina) | `jupyter` | Es este notebook. Divide cada consulta en tareas pequeñas y junta los resultados. **No procesa los datos.** |
| **Master** (encargado) | `spark-master` | Sabe qué workers hay y cuántos núcleos y memoria tiene cada uno. |
| **Workers** (cocineros) | `spark-worker-1` a `3` | Ponen los núcleos y la memoria. Dentro de ellos corren los *executors*, que son los que leen y procesan las filas. |

<div align="center">
<img src="img/arquitectura_cluster.svg" alt="Diagrama del clúster: driver, master, tres workers y volumen compartido" width="720"><br>
<em>Figura 1. Arquitectura de nuestro clúster. Los tres roles corren en contenedores Docker de un mismo equipo.</em>
</div>

> **Nota.** Los tres workers comparten la misma carpeta, `/opt/workspace`. Así cada executor abre sus archivos `.jsonl` directamente, sin pedírselos al driver.

<!-- ===== CELDA 1.2 · INTERPRETACIÓN + CONTEXTO · antes de Hito 1.3 ===== -->

**Lectura del resultado.** Hay **16 archivos** de unos 85 MiB cada uno, **1,18 GiB** en total. Aquí solo revisamos nombres y tamaños; todavía no se lee ninguna fila.

### Tamaño del clúster

Antes de encender el clúster hay que comprobar que cabe en la memoria que tiene Docker. La regla es simple: la memoria de todos los workers más la del driver tiene que ser menor que la memoria de Docker.

$$
\text{workers} \times \text{memoria por worker} + \text{memoria del driver} < \text{RAM de Docker}
$$

Con nuestros números:

$$
3 \times 3\,\text{GB} + 3\,\text{GB} = 12\,\text{GB} < 15{,}4\,\text{GB}
$$

Estos valores se configuran en el archivo `.env`:

| Variable del `.env` | Valor |
|:---|---:|
| `SPARK_WORKERS` | 3 |
| `SPARK_WORKER_CORES` | 2 |
| `SPARK_WORKER_MEMORY` | 3g |
| `SPARK_EXECUTOR_MEMORY` | 3g |
| `SPARK_DRIVER_MEMORY` | 3g |

Docker tiene 15,4 GB en nuestro equipo (lo vimos con `docker info --format "{{.MemTotal}}"`). Es el perfil de 16 GB de la tabla del `README`. Sobran 3,4 GB para el sistema y los contenedores.

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
<em>Figura 2. Página del master (<code>localhost:8080</code>): tres workers activos (ALIVE), con 2 núcleos y 3 GiB cada uno, y este notebook (<code>fase2-sitio3</code>) usando los 6 núcleos.</em>
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
      6ce4c40fa9ab                   ve los datos (16 archivos)
      82164bf597cc                   ve los datos (16 archivos)
      a6c351f4c851                   ve los datos (16 archivos)
[4/4] Leyendo los datos crudos de la Fase 1...
      Registros leidos : 10,000,000
      Particiones      : 16
```

El paso 3 es el más importante: **cada worker** revisa por su cuenta que ve la carpeta (los tres códigos son los nombres de los workers). Si uno no la viera, el notebook fallaría más adelante, a mitad de una lectura.

### Por qué no usar `.collect()` con millones de filas

`.collect()` trae **todas** las filas al driver, que es un solo proceso. Hacerlo con 10 millones de lecturas es volver al límite de un solo computador, justo lo que el clúster evita. Lo más probable es que el driver se quede sin memoria y se caiga.

En este notebook solo usamos `.collect()` con resultados **ya resumidos** por los executors: 5 filas (una por métrica) o 16 filas (una por archivo). El trabajo pesado lo hace el clúster y al driver solo le llega la respuesta.

> **Idea clave.** El driver organiza y los executors trabajan. Si los datos no caben en una máquina, tampoco caben en el driver.

[↑ Volver al índice](#Índice)

---
