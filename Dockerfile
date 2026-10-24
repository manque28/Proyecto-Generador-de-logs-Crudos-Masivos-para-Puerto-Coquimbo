# syntax=docker/dockerfile:1

# Dockerfile v2 del laboratorio: multi-etapa, cache eficiente y hardening.
# la misma imagen sirve para los dos servicios de la parte 3; compose elige el
# programa con command: (src/receptor_tcp.py o src/emisor_tcp.py).

# ============================================================
# ETAPA 1 - builder: aqui se arma el entorno de python
# ============================================================
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# la guia instala build-essential y gcc en esta etapa para compilar
# dependencias con extensiones en C. este proyecto solo usa la biblioteca
# estandar (ver requirements.txt), asi que no hacen falta y se omiten: son
# ~200 MB y ~30 s de apt-get por build. si algun dia se agrega una dependencia
# nativa, se descomenta y, como es la etapa builder, igual no llega a la final.
# RUN apt-get update && apt-get install -y --no-install-recommends \
#         build-essential gcc \
#     && rm -rf /var/lib/apt/lists/*

# entorno virtual aislado: es lo unico que viaja a la etapa final
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# CACHE: requirements ANTES que el codigo fuente. si solo cambia el codigo,
# docker reutiliza esta capa y no vuelve a instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# ETAPA 2 - runtime: minima, sin toolchain, sin privilegios
# ============================================================
FROM python:3.12-slim AS runtime

# PYTHONUNBUFFERED: docker logs muestra el avance de la ingesta en vivo
# PYTHONDONTWRITEBYTECODE: sin .pyc dentro del contenedor
# PYTHONFAULTHANDLER: traza de python ante senales fatales, distingue un fallo
#   del codigo de un SIGKILL del kernel
# PATH: python y pip resuelven al venv copiado desde builder
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/venv/bin:$PATH"

# tini: init minimo para el PID 1, reenvia SIGTERM a python y adopta zombies
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

# usuario sin privilegios con UID fijo, tiene que coincidir con el dueno del
# bind mount de data/raw en la parte 3
RUN groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid appgroup --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

# solo el venv ya construido; lo que se instale en builder se queda alla
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup src/ ./src/

# carpeta de salida del receptor (DATA_DIR), escribible por appuser
RUN mkdir -p /app/data && chown -R appuser:appgroup /app/data

USER appuser

# puerto del receptor tcp
EXPOSE 9009

# forma exec en ENTRYPOINT y CMD: tini es el PID 1 y python su hijo directo
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-u", "src/receptor_tcp.py"]
