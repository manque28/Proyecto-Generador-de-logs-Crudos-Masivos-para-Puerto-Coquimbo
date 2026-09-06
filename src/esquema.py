"""el contrato del evento, todo lo que sale al jsonl pasa por aqui.
"""

import json


def formatear_evento(timestamp_str, metadatos, worker_id):
    """
    los nombres son literales
    worker_id va aqui porque es el campo que hace auditable el paralelismo,
    contando eventos por worker se verifica el balance de carga.
    """
    value = metadatos["value"]

    if not isinstance(value, (int, float)):
        raise ValueError("El campo value debe ser de tipo int o float")

    return {
        "timestamp": timestamp_str,
        "sensor_id": metadatos["sensor_id"],
        "metric": metadatos["metric"],
        "value": value,
        "unit": metadatos["unit"],
        "worker_id": worker_id,
    }


def serializar_evento(evento):
    """me deja el evento listo como una linea del jsonl, 

    un objeto json valido por linea, sin corchetes envolventes, sin comas al
    final y sin saltos adentro del objeto. eso es lo que hace el archivo
    divisible, spark parte por el salto de linea desde cualquier posicion y
    reparte los bloques entre ejecutores, cosa que un json con un arreglo
    grande no permite porque hay que leerlo entero.

    el salto lo dejo puesto aqui para poder mandar la lista completa con
    writelines, y los separators van sin espacios porque son millones de
    lineas y cada byte de mas se me nota en el 1,4 GB final.
    """
    return json.dumps(evento, separators=(",", ":")) + "\n"
