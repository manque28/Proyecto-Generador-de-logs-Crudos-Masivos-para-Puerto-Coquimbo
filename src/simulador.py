"""fisica de los equipos del sitio 3, fajas, gruas y bascula.

simular comportamiento fisico y no un generador de numeros aleatorios.
cada activo recuerda en que condicion quedo en el tick anterior, y de ahi salen la inercia, la deriva y el ruido que la fase 2
necesita para que el detector de anomalias sea interesante.

cada clase se guarda su propio estado y en cada tick me devuelve la lista de
metadatos que midieron sus sensores. nunca de golpe.
"""

import random


def _alfa(dt_s, tau_s):
    """me da la fraccion que avanza una magnitud hacia su objetivo en cada tick.
    es la misma idea del reefer del ejemplo del documento, el valor persigue a su objetivo y se le va acercando de a poco.
    """
    return dt_s / (tau_s + dt_s)


class Faja:
    """faja transportadora, la vibracion y la corriente van siguiendo a la carga.
    la vibracion de una faja sube con la carga y cae cuando se detiene el flujo, mas el amperaje del motor. a veces
    esta andando, a veces detenida. cuando anda, mientras mas material lleva,
    mas vibra y mas corriente consume. cuando se detiene, todo baja a cero, rapido pero no de golpe.
    """

    VIB_VACIO, VIB_PLENA = 1.2, 6.5      # mm/s
    CUR_VACIO, CUR_PLENA = 18.0, 95.0    # A
    TAU_MARCHA = 45.0                    # cuando esta andando normal
    TAU_PARADA = 6.0                     # al parar baja rapido pero no de golpe

    def __init__(self, sensor_id, rng):
        # el rng entra por el constructor y me lo quedo, lab1 trampa 4, cada
        # activo usa el stream de su worker y nunca el random del modulo
        self.sensor_id = sensor_id
        self.rng = rng
        self.carga = rng.uniform(0.2, 0.8)
        self.carga_objetivo = self.carga
        self.operando = True
        self.vibracion = self.VIB_VACIO
        self.corriente = self.CUR_VACIO

    def _actualizar_operacion(self):
        # a veces se detiene, pero le dejo mas probabilidad de arrancar de nuevo
        # que de pararse, si no la faja se me queda muerta mucho rato
        if self.operando:
            if self.rng.random() < 0.02:
                self.operando = False
        elif self.rng.random() < 0.25:
            self.operando = True

    def _actualizar_carga(self):
        # la carga no puede saltar de un tick a otro, va persiguiendo un objetivo
        # que le cambio cada tanto y asi queda con inercia
        if self.rng.random() < 0.08:
            self.carga_objetivo = self.rng.uniform(0.0, 1.0)
        self.carga += (self.carga_objetivo - self.carga) * 0.3

    def tick(self, dt_s):
        self._actualizar_operacion()

        if self.operando:
            self._actualizar_carga()
            vib_obj = self.VIB_VACIO + (self.VIB_PLENA - self.VIB_VACIO) * self.carga
            cur_obj = self.CUR_VACIO + (self.CUR_PLENA - self.CUR_VACIO) * self.carga
            a = _alfa(dt_s, self.TAU_MARCHA)
        else:
            # detenida las dos cosas se van a cero, pero con el tau corto
            vib_obj = cur_obj = 0.0
            a = _alfa(dt_s, self.TAU_PARADA)

        self.vibracion += (vib_obj - self.vibracion) * a
        self.corriente += (cur_obj - self.corriente) * a

        # lab1 3.2, metric en minusculas y en ingles, unit con la unidad fisica.
        # el gauss es el ruido del sensor del ejemplo del documento y el
        # max(0.0, ...) es para que ese ruido no me deje valores negativos
        return [
            {
                "sensor_id": self.sensor_id,
                "metric": "vibration",
                "value": round(max(0.0, self.vibracion + self.rng.gauss(0.0, 0.05)), 3),
                "unit": "mm/s",
            },
            {
                "sensor_id": self.sensor_id,
                "metric": "current",
                "value": round(max(0.0, self.corriente + self.rng.gauss(0.0, 0.4)), 2),
                "unit": "A",
            },
        ]


class Grua:
    """grua sts,
    da vueltas en un ciclo fijo, espera, levanta, traslada, baja, espera otra
    vez. cuando agarra un contenedor le sortea un peso, y ese peso no cambia
    hasta que lo suelta.
    """

    # estado -> (cuantos ticks dura, corriente a la que tiende en A)
    CICLO = {
        "inactiva": (None, 35.0),
        "izando": (3, 420.0),
        "trasladando": (4, 260.0),
        "bajando": (2, 110.0),
    }
    SIGUIENTE = {
        "inactiva": "izando",
        "izando": "trasladando",
        "trasladando": "bajando",
        "bajando": "inactiva",
    }
    TAU_CORRIENTE = 10.0

    def __init__(self, sensor_id, rng):
        self.sensor_id = sensor_id
        self.rng = rng
        self.estado = "inactiva"
        self.restantes = rng.randint(1, 4)
        self.peso = 0.0
        self.corriente = self.CICLO["inactiva"][1]

    def _avanzar(self):
        self.restantes -= 1
        if self.restantes > 0:
            return

        self.estado = self.SIGUIENTE[self.estado]
        if self.estado == "inactiva":
            self.restantes = self.rng.randint(1, 5)
            self.peso = 0.0                                # ya solto la carga
        else:
            self.restantes = self.CICLO[self.estado][0]
            if self.estado == "izando":
                # el peso del contenedor lo sorteo aqui una sola vez, despues no
                # lo toco en todo el ciclo para que no me quede fluctuando
                self.peso = round(self.rng.uniform(6000.0, 30000.0), 1)

    def tick(self, dt_s):
        self._avanzar()

        cur_obj = self.CICLO[self.estado][1]
        self.corriente += (cur_obj - self.corriente) * _alfa(dt_s, self.TAU_CORRIENTE)

        return [
            {
                "sensor_id": self.sensor_id,
                "metric": "current",
                "value": round(max(0.0, self.corriente + self.rng.gauss(0.0, 1.5)), 2),
                "unit": "A",
            },
            # este lo mando sin ruido, una carga colgando no le cambia el peso
            # entre una lectura y la otra. es la coherencia fisica de la serie
            # que lab1 4.6 evalua en calidad del dataset
            {
                "sensor_id": self.sensor_id,
                "metric": "weight",
                "value": self.peso,
                "unit": "kg",
            },
        ]


class Bascula:
    """bascula de acceso vehicular, 

    mientras el camion esta encima el peso se queda quieto, alterna entre hay
    camion y no hay camion, con camion encima marca siempre casi lo mismo,
    moviendose apenas decimas.
    """

    def __init__(self, sensor_id, rng):
        self.sensor_id = sensor_id
        self.rng = rng
        self.peso_base = 0.0
        self.restantes = rng.randint(2, 6)

    def tick(self, dt_s):
        # recibo dt_s aunque no lo use, aqui el estado avanza por ticks y no
        # por segundos, pero le dejo la misma firma que a los demas activos
        # asi el generador los recorre a todos igual sin preguntar que son
        self.restantes -= 1
        if self.restantes <= 0:
            if self.peso_base > 0.0:
                self.peso_base = 0.0                       # se fue el camion
                self.restantes = self.rng.randint(2, 8)
            else:
                # llega un camion, le sorteo el peso una vez y ese queda fijo
                # durante todo el pesaje
                self.peso_base = round(self.rng.uniform(14000.0, 42000.0), 1)
                self.restantes = self.rng.randint(3, 6)

        if self.peso_base > 0.0:
            # solo le sumo decimas, lo que se mueve es la celda de carga y no el
            # camion, por eso el numero no me puede saltar entre ticks
            valor = round(self.peso_base + self.rng.gauss(0.0, 0.08), 2)
        else:
            valor = round(abs(self.rng.gauss(0.0, 0.05)), 2)

        return [
            {
                "sensor_id": self.sensor_id,
                "metric": "weight",
                "value": valor,
                "unit": "kg",
            }
        ]


def crear_activos(semilla, worker_id):
    """los equipos del sitio 3, son 6 fajas, 2 gruas sts y 1 bascula.

    los sensor_id siguen la convencion TIPO_SITIO_CORRELATIVO de lab1 3.2,
    y las cantidades salen del inventario sugerido en lab1 1.1: 6 tramos de
    faja con vibracion y corriente, 2 gruas con telemetria de ciclo y 1
    bascula de acceso.

    pendiente de lab1 1.1: faltan las 48 posiciones reefer y los 12 sensores
    ambientales de patio para llegar a los ~180 puntos de medicion, con eso
    entrarian las metricas temperature y humidity que hoy no genero.

    el rng lo armo aqui adentro, uno propio por worker con
    random.Random(semilla + worker_id), y se lo paso a cada clase en el
    constructor. si sembrara el modulo global antes de repartir el trabajo,
    los hijos heredarian el mismo estado y el dataset quedaria con n copias
    identicas de la misma serie
    """
    rng = random.Random(semilla + worker_id)
    activos = [Faja(f"FAJA_S3_C{i}", rng) for i in range(1, 7)]
    activos.append(Grua("GRUA_S3_STS01", rng))
    activos.append(Grua("GRUA_S3_STS02", rng))
    activos.append(Bascula("BASCULA_S3_01", rng))
    return activos
