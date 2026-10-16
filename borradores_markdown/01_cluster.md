<!-- ===== CELDA 1.1 · CONTEXTO · antes de Hito 1.1 ===== -->

## Clúster y procesamiento distribuido

**Qué hacemos:** levantamos un clúster de Spark y abrimos la sesión desde la que trabaja todo el notebook.

**Por qué importa en Big Data:** una sola máquina tiene un techo. Se le puede agregar RAM y núcleos (*escalado vertical*), pero llega un punto en que ya no hay más que agregar o deja de ser rentable. Spark toma el otro camino, el *escalado horizontal*: reparte el trabajo entre varias máquinas, y si los datos crecen se suman más máquinas en vez de una más grande.

En nuestro clúster cada pieza tiene un rol distinto:

| Rol | Contenedor | Qué hace |
|:---|:---|:---|
| **Driver** | `jupyter` | Es este notebook. Arma el plan de cada consulta, lo divide en tareas y recibe los resultados. **No procesa los datos.** |
| **Master** | `spark-master` | Administra los recursos: sabe qué workers existen y cuántos núcleos y memoria tiene cada uno. |
| **Workers** | `spark-worker-1` a `3` | Aportan los núcleos y la memoria. En ellos corren los *executors*, que son los que de verdad leen y procesan las filas. |

<div align="center">
<img src="img/arquitectura_cluster.svg" alt="Diagrama del clúster: driver, master, tres workers y volumen compartido" width="720"><br>
<em>Figura 1. Arquitectura de nuestro clúster. Los tres roles corren en contenedores Docker de un mismo equipo.</em>
</div>

> **Nota.** Los tres workers montan la misma carpeta `/opt/workspace`. Así cada executor abre sus propios archivos `.jsonl`: los datos nunca pasan por el driver.

<!-- ===== CELDA 1.2 · INTERPRETACIÓN + CONTEXTO · antes de Hito 1.3 ===== -->

**Lectura del resultado.** Hay **16 archivos** de unos 85 MiB cada uno, **1,18 GiB** en total. Esta comprobación solo mira nombres y tamaños desde el driver; todavía no se lee ni una fila.

### Dimensionamiento del clúster

Antes de abrir la sesión hay que asegurarse de que el clúster cabe en la memoria que Docker tiene asignada. La regla que usamos en el `.env` es:

$$
\text{workers} \times \text{memoria por worker} + \text{memoria del driver} < \text{RAM de Docker}
$$

Con nuestra configuración:

$$
3 \times 3\,\text{GB} + 3\,\text{GB} = 12\,\text{GB} < 15{,}4\,\text{GB}
$$

| Variable del `.env` | Valor |
|:---|---:|
| `SPARK_WORKERS` | 3 |
| `SPARK_WORKER_CORES` | 2 |
| `SPARK_WORKER_MEMORY` | 3g |
| `SPARK_EXECUTOR_MEMORY` | 3g |
| `SPARK_DRIVER_MEMORY` | 3g |

Los 15,4 GB son la memoria que Docker tiene asignada en nuestro equipo (`docker info --format "{{.MemTotal}}"`). Corresponde al perfil de 16 GB de la tabla del `README`, y deja 3,4 GB de holgura para el sistema y los propios contenedores.

> **Atención.** `SPARK_EXECUTOR_MEMORY` no puede superar a `SPARK_WORKER_MEMORY`. Si el executor pide más memoria de la que su worker ofrece, el clúster arranca igual pero queda con **0 executors** y ningún job avanza.

<!-- ===== CELDA 1.3 · INTERPRETACIÓN · antes de Hito 1.4 ===== -->

### El clúster está operativo

| Lo que medimos | Resultado | Qué significa |
|:---|:---:|:---|
| Executors vivos | **3 de 3** | Los tres workers se registraron y tienen recursos asignados. |
| Paralelismo | **6** | 3 workers × 2 núcleos: Spark puede ejecutar hasta 6 tareas al mismo tiempo. |
| Master | `spark://spark-master:7077` | El driver trabaja contra el clúster, no en modo local. |

La celda termina con un `assert`: si faltara algún executor, el notebook se detiene ahí en vez de seguir con menos recursos de los que creemos tener.

<div align="center">
<img src="img/ui_8080_workers.png" alt="UI del master en el puerto 8080 con los tres workers registrados" width="720"><br>
<em>Figura 2. UI del master (<code>localhost:8080</code>): tres workers en estado ALIVE, con 2 núcleos y 3 GiB cada uno, y este notebook (<code>fase2-sitio3</code>) usando los 6 núcleos.</em>
</div>

**Prueba de humo.** Antes de abrir el notebook ejecutamos `verificar_cluster.py`, que revisa cuatro cosas: que el driver alcanza al master, que hay executors, que todos ven los datos y que la lectura completa funciona.

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

La comprobación 3 es la más importante: la ejecuta **cada executor por su cuenta**, desde su propio contenedor (los tres nombres son los de los workers). Si algún worker no viera la carpeta compartida, el notebook fallaría recién a mitad de una lectura.

### Por qué un `.collect()` de millones de filas es un error

`.collect()` trae **todas** las filas del resultado a la memoria del driver, que es un solo proceso. Hacerlo con los 10 millones de lecturas sería volver al techo de una sola máquina que el clúster justamente evita, y lo más probable es que el driver se caiga por falta de memoria.

En este notebook `.collect()` aparece solo sobre resultados **ya resumidos** por los executors: 5 filas (una por métrica) o 16 filas (una por archivo de entrada). El trabajo pesado se queda en el clúster y al driver solo viaja la respuesta.

> **Idea clave.** El driver coordina, los executors procesan. Si un dato no cabe en una máquina, tampoco cabe en el driver.

[↑ Volver al índice](#Índice)

---
