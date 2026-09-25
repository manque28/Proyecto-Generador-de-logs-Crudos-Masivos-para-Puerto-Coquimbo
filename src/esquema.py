"""el contrato del evento, todo lo que sale al jsonl pasa por aqui.

antes esto eran dos funciones, formatear_evento armaba un dict y
serializar_evento se lo pasaba a json.dumps. ahora es una sola que escribe la
linea directo, y el motivo es medido y no de gusto: bench/perfil_cpu.py mostro
que el modulo json se llevaba el 39,6% de la cpu del generador, y
bench/microbench.py midio esta version en x2,11 el throughput, de 310 mil a 655
mil eventos por segundo, con el jsonl byte identico al anterior.

el dict intermedio desaparecio de paso. no aportaba nada, se construia solo
para entregarselo a json y se tiraba, casi 10 millones de dicts en la fase
completa.
"""

# la plantilla ES el contrato: el orden de los campos, sus nombres y el formato
# de la linea viven aqui y en ningun otro lado del proyecto. si hay que agregar
# un campo se agrega en esta cadena y nada mas se entera.
#
# el %r del value es lo que hace que esto sea equivalente a json y no una
# imitacion: json serializa los numeros con float.__repr__, que es exactamente
# lo que produce %r. los otros campos van con %s y sin escapar porque
# sensor_id, metric y unit son constantes del simulador, ascii y sin comillas
# ni backslash.
#
# el salto de linea va incluido para poder mandar la lista completa con
# writelines, y no hay espacios en ningun separador porque son millones de
# lineas y cada byte de mas se nota en el 1,4 GB final.
_PLANTILLA = (
    '{"timestamp":"%s","sensor_id":"%s","metric":"%s","value":%r,'
    '"unit":"%s","worker_id":%d}\n'
)


def linea_evento(timestamp_str, metadatos, worker_id):
    """arma la linea jsonl de un evento, lista para escribir.

    un objeto json valido por linea, sin corchetes envolventes, sin comas al
    final y sin saltos adentro del objeto. eso es lo que hace el archivo
    divisible, spark parte por el salto de linea desde cualquier posicion y
    reparte los bloques entre ejecutores, cosa que un json con un arreglo
    grande no permite porque hay que leerlo entero.

    worker_id va en el evento porque es el campo que hace auditable el
    paralelismo, contando eventos por worker se verifica el balance de carga.

    la validacion del value se queda, y ahora importa MAS que antes. cuando
    esto pasaba por json.dumps, un value de tipo raro reventaba ahi con un
    TypeError y el problema salia a la luz solo. con la plantilla no: un string
    se formatearia igual, quedaria sin comillas y produciria una linea de json
    invalida en silencio, en medio de 10 millones. este chequeo es lo que
    convierte ese fallo mudo en un error ruidoso, y sale barato, se midio en un
    2,5% del throughput.
    """
    value = metadatos["value"]

    if not isinstance(value, (int, float)):
        raise ValueError("El campo value debe ser de tipo int o float")

    return _PLANTILLA % (
        timestamp_str,
        metadatos["sensor_id"],
        metadatos["metric"],
        value,
        metadatos["unit"],
        worker_id,
    )
