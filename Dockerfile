# imagen del generador de logs crudos, fase 1 del proyecto tpc sitio 3.

FROM python:3.12-slim

# PYTHONDONTWRITEBYTECODE me evita los .pyc dentro del contenedor, y
# PYTHONUNBUFFERED es el importante: sin el, el print de cada configuracion se
# queda en el bufer y no veo el avance de una corrida que dura varios minutos.
# PYTHONPATH apunta a src porque los modulos se importan planos, "from esquema
# import ..." y no "from src.esquema import ...".
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# copio solo el generador.
COPY src/ ./src/


RUN useradd --create-home --uid 1000 tpc \
    && mkdir -p /app/data/raw \
    && chown -R tpc:tpc /app

VOLUME ["/app/data/raw"]

USER tpc


# if __name__ == "__main__" de main.py igual tiene que estar, la correccion
# puede hacerse en otra plataforma y sin el bloque spawn revienta.
CMD ["python", "src/main.py"]
