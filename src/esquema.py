def formatear_evento(timestamp_str, metadatos, worker_id):
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