# syntax=docker/dockerfile:1

# imagen unica de la fase 2 para los tres roles (master, worker y jupyter).
# driver y executors intercambian objetos python serializados: con la misma
# imagen, el error "python in worker has different version" no puede ocurrir
# (informe, 5.1). compose elige el rol de cada servicio con command:.

# imagen oficial de apache: spark 4.0.1 + java 17 + python 3.10.12 (ubuntu 22.04).
# no se usa 3.5 (trae python 3.8, sin soporte) ni bitnami (movida a bitnamilegacy).
FROM apache/spark:4.0.1

USER root

# jupyterlab y librerias de apoyo. pyspark NO se instala con pip: se usa el que
# trae la imagen en /opt/spark, asi driver y executors corren la misma version.
RUN pip3 install --no-cache-dir jupyterlab pandas pyarrow

# la imagen trae pyspark en /opt/spark/python pero python no lo encuentra
# (ModuleNotFoundError: pyspark). un archivo .pth agrega esa ruta y la de py4j.
RUN SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
    echo "/opt/spark/python" > "$SITE/pyspark.pth" && \
    ls /opt/spark/python/lib/py4j-*-src.zip >> "$SITE/pyspark.pth"

# configuracion comun: driver.host, AQE y zona horaria UTC
COPY spark-defaults.conf /opt/spark/conf/spark-defaults.conf

ENV SPARK_HOME=/opt/spark \
    PATH="/opt/spark/bin:/opt/spark/sbin:${PATH}" \
    PYSPARK_PYTHON=python3 \
    PYSPARK_DRIVER_PYTHON=python3

# la carpeta del proyecto se monta aqui en los tres servicios (informe, 5.4)
WORKDIR /opt/workspace
