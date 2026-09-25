"""fisica de los equipos del sitio 3, fajas, gruas, bascula, reefers y sensores ambientales.

simular comportamiento fisico y no un generador de numeros aleatorios.
cada activo recuerda en que condicion quedo en el tick anterior, y de ahi salen la inercia, la deriva y el ruido que la fase 2
necesita para que el detector de anomalias sea interesante.

cada clase se guarda su propio estado y en cada tick me devuelve la lista de
metadatos que midieron sus sensores. nunca de golpe.

TRES DETALLES DE RENDIMIENTO que se repiten en las tres clases y que explico
una sola vez aca, en vez de tres veces mas abajo. salen medidos de
bench/microbench.py, ver bench/microbench_resultados.md:

  1. los dicts de metadatos se arman UNA vez en el constructor y en cada tick
     solo se les pisa el value. antes se construian de nuevo en cada tick, 17
     dicts por tick entre los 9 activos, casi 10 millones en la fase completa.
     el riesgo de esto es el aliasing: quien recibe estos dicts no puede
     guardarselos, porque en el proximo tick le cambian debajo. el generador
     los consume y los suelta en el acto, asi que es seguro, pero queda dicho.

  2. __slots__ le saca el __dict__ a la instancia. son 9 objetos nada mas, asi
     que el ahorro de memoria da igual; lo que interesa es que el acceso a los
     atributos pasa a ser por posicion y no por diccionario, y en un tick hay
     una docena de esos accesos.

  3. los metodos del rng quedan guardados como atributos en el constructor.
     self.rng.gauss son dos busquedas por llamada, self._gauss es una. self.rng
     se conserva igual porque es el que documenta de donde sale el stream.

el orden en que se consume el rng es parte del contrato del dataset, no un
detalle: si se cambia el orden de dos llamadas, o el orden en que se
construyen los activos, el stream se corre y el dataset deja de ser el mismo
aunque la semilla no cambie.
"""

import math
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

    __slots__ = (
        "sensor_id", "rng", "carga", "carga_objetivo", "operando",
        "vibracion", "corriente", "_random", "_uniform", "_gauss",
        "_m_vibracion", "_m_corriente", "_lecturas",
    )

    VIB_VACIO, VIB_PLENA = 1.2, 6.5      # mm/s
    CUR_VACIO, CUR_PLENA = 18.0, 95.0    # A
    TAU_MARCHA = 45.0                    # cuando esta andando normal
    TAU_PARADA = 6.0                     # al parar baja rapido pero no de golpe

    def __init__(self, sensor_id, rng):
        # el rng entra por el constructor y me lo quedo, lab1 trampa 4, cada
        # activo usa el stream de su worker y nunca el random del modulo
        self.sensor_id = sensor_id
        self.rng = rng
        self._random = rng.random
        self._uniform = rng.uniform
        self._gauss = rng.gauss
        self.carga = rng.uniform(0.2, 0.8)
        self.carga_objetivo = self.carga
        self.operando = True
        self.vibracion = self.VIB_VACIO
        self.corriente = self.CUR_VACIO

        # lab1 3.2, metric en minusculas y en ingles, unit con la unidad fisica.
        # los tres campos fijos se escriben aqui una vez y no se vuelven a tocar
        self._m_vibracion = {
            "sensor_id": sensor_id,
            "metric": "vibration",
            "value": 0.0,
            "unit": "mm/s",
        }
        self._m_corriente = {
            "sensor_id": sensor_id,
            "metric": "current",
            "value": 0.0,
            "unit": "A",
        }
        self._lecturas = [self._m_vibracion, self._m_corriente]

    def _actualizar_operacion(self):
        # a veces se detiene, pero le dejo mas probabilidad de arrancar de nuevo
        # que de pararse, si no la faja se me queda muerta mucho rato
        if self.operando:
            if self._random() < 0.02:
                self.operando = False
        elif self._random() < 0.25:
            self.operando = True

    def _actualizar_carga(self):
        # la carga no puede saltar de un tick a otro, va persiguiendo un objetivo
        # que le cambio cada tanto y asi queda con inercia
        if self._random() < 0.08:
            self.carga_objetivo = self._uniform(0.0, 1.0)
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

        # el gauss es el ruido del sensor del ejemplo del documento y el
        # max(0.0, ...) es para que ese ruido no me deje valores negativos.
        # primero la vibracion y despues la corriente, ese orden es el que
        # consume el stream del rng y no se puede dar vuelta
        self._m_vibracion["value"] = round(
            max(0.0, self.vibracion + self._gauss(0.0, 0.05)), 3
        )
        self._m_corriente["value"] = round(
            max(0.0, self.corriente + self._gauss(0.0, 0.4)), 2
        )
        return self._lecturas


class Grua:
    """grua sts,
    da vueltas en un ciclo fijo, espera, levanta, traslada, baja, espera otra
    vez. cuando agarra un contenedor le sortea un peso, y ese peso no cambia
    hasta que lo suelta.
    """

    __slots__ = (
        "sensor_id", "rng", "estado", "restantes", "peso", "corriente",
        "_randint", "_uniform", "_gauss",
        "_m_corriente", "_m_peso", "_lecturas",
    )

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
        self._randint = rng.randint
        self._uniform = rng.uniform
        self._gauss = rng.gauss
        self.estado = "inactiva"
        self.restantes = rng.randint(1, 4)
        self.peso = 0.0
        self.corriente = self.CICLO["inactiva"][1]

        self._m_corriente = {
            "sensor_id": sensor_id,
            "metric": "current",
            "value": 0.0,
            "unit": "A",
        }
        self._m_peso = {
            "sensor_id": sensor_id,
            "metric": "weight",
            "value": 0.0,
            "unit": "kg",
        }
        self._lecturas = [self._m_corriente, self._m_peso]

    def _avanzar(self):
        self.restantes -= 1
        if self.restantes > 0:
            return

        self.estado = self.SIGUIENTE[self.estado]
        if self.estado == "inactiva":
            self.restantes = self._randint(1, 5)
            self.peso = 0.0                                # ya solto la carga
        else:
            self.restantes = self.CICLO[self.estado][0]
            if self.estado == "izando":
                # el peso del contenedor lo sorteo aqui una sola vez, despues no
                # lo toco en todo el ciclo para que no me quede fluctuando
                self.peso = round(self._uniform(6000.0, 30000.0), 1)

    def tick(self, dt_s):
        self._avanzar()

        cur_obj = self.CICLO[self.estado][1]
        self.corriente += (cur_obj - self.corriente) * _alfa(dt_s, self.TAU_CORRIENTE)

        self._m_corriente["value"] = round(
            max(0.0, self.corriente + self._gauss(0.0, 1.5)), 2
        )
        # el peso lo mando sin ruido, una carga colgando no le cambia el peso
        # entre una lectura y la otra. es la coherencia fisica de la serie que
        # lab1 4.6 evalua en calidad del dataset
        self._m_peso["value"] = self.peso
        return self._lecturas


class Bascula:
    """bascula de acceso vehicular,

    mientras el camion esta encima el peso se queda quieto, alterna entre hay
    camion y no hay camion, con camion encima marca siempre casi lo mismo,
    moviendose apenas decimas.
    """

    __slots__ = (
        "sensor_id", "rng", "peso_base", "restantes",
        "_randint", "_uniform", "_gauss", "_m_peso", "_lecturas",
    )

    def __init__(self, sensor_id, rng):
        self.sensor_id = sensor_id
        self.rng = rng
        self._randint = rng.randint
        self._uniform = rng.uniform
        self._gauss = rng.gauss
        self.peso_base = 0.0
        self.restantes = rng.randint(2, 6)

        self._m_peso = {
            "sensor_id": sensor_id,
            "metric": "weight",
            "value": 0.0,
            "unit": "kg",
        }
        self._lecturas = [self._m_peso]

    def tick(self, dt_s):
        # recibo dt_s aunque no lo use, aqui el estado avanza por ticks y no
        # por segundos, pero le dejo la misma firma que a los demas activos
        # asi el generador los recorre a todos igual sin preguntar que son
        self.restantes -= 1
        if self.restantes <= 0:
            if self.peso_base > 0.0:
                self.peso_base = 0.0                       # se fue el camion
                self.restantes = self._randint(2, 8)
            else:
                # llega un camion, le sorteo el peso una vez y ese queda fijo
                # durante todo el pesaje
                self.peso_base = round(self._uniform(14000.0, 42000.0), 1)
                self.restantes = self._randint(3, 6)

        if self.peso_base > 0.0:
            # solo le sumo decimas, lo que se mueve es la celda de carga y no el
            # camion, por eso el numero no me puede saltar entre ticks
            self._m_peso["value"] = round(self.peso_base + self._gauss(0.0, 0.08), 2)
        else:
            self._m_peso["value"] = round(abs(self._gauss(0.0, 0.05)), 2)

        return self._lecturas


class Reefer:
    """contenedor refrigerado conectado a la red del terminal.

    es el ejemplo del documento (lab1 1.1) con dos metricas mas. el compresor
    tira la temperatura hacia el setpoint y la puerta abierta la empuja en
    sentido contrario. las tres metricas se mueven juntas: con la puerta
    abierta sube la temperatura, entra aire humedo y el compresor consume mas
    para recuperar. cerrada, todo vuelve de a poco a su regimen.
    """

    __slots__ = (
        "sensor_id", "rng", "setpoint", "temp", "humedad", "corriente",
        "puerta_abierta", "restantes",
        "_random", "_randint", "_uniform", "_gauss",
        "_m_temp", "_m_corriente", "_m_humedad", "_lecturas",
    )

    P_ABRIR = 0.0005          # por tick, da unas 3 aperturas por dia
    HUM_CERRADA = 75.0        # % que mantiene el equipo
    HUM_ABIERTA = 92.0        # % hacia donde la empuja el aire de afuera
    CUR_BASE = 7.5            # A, compresor en regimen
    CUR_MAX = 19.0            # A, compresor a full
    CUR_POR_GRADO = 4.0       # A extra por cada grado sobre el setpoint
    TAU_HUMEDAD = 40.0
    TAU_CORRIENTE = 20.0

    def __init__(self, sensor_id, rng, setpoint=-18.0):
        self.sensor_id = sensor_id
        self.rng = rng
        self._random = rng.random
        self._randint = rng.randint
        self._uniform = rng.uniform
        self._gauss = rng.gauss
        self.setpoint = setpoint
        self.temp = setpoint + rng.uniform(-0.4, 0.4)
        self.humedad = self.HUM_CERRADA + rng.uniform(-2.0, 2.0)
        self.corriente = self.CUR_BASE
        self.puerta_abierta = False
        self.restantes = 0

        self._m_temp = {
            "sensor_id": sensor_id,
            "metric": "temperature",
            "value": 0.0,
            "unit": "C",
        }
        self._m_corriente = {
            "sensor_id": sensor_id,
            "metric": "current",
            "value": 0.0,
            "unit": "A",
        }
        self._m_humedad = {
            "sensor_id": sensor_id,
            "metric": "humidity",
            "value": 0.0,
            "unit": "%",
        }
        self._lecturas = [self._m_temp, self._m_corriente, self._m_humedad]

    def _actualizar_puerta(self):
        # la puerta se abre muy de vez en cuando y queda abierta unos ticks,
        # entre 30 s y 2 min, que es lo que dura una inspeccion
        if self.puerta_abierta:
            self.restantes -= 1
            if self.restantes <= 0:
                self.puerta_abierta = False
        elif self._random() < self.P_ABRIR:
            self.puerta_abierta = True
            self.restantes = self._randint(2, 8)

    def tick(self, dt_s):
        self._actualizar_puerta()

        # temperatura igual que el ejemplo del documento
        if self.puerta_abierta:
            self.temp += 0.9 * (dt_s / 60.0)
            hum_obj = self.HUM_ABIERTA
        else:
            self.temp += (self.setpoint - self.temp) * 0.08
            hum_obj = self.HUM_CERRADA

        # el compresor trabaja mas mientras mas lejos esta del setpoint
        error = max(0.0, self.temp - self.setpoint)
        cur_obj = min(self.CUR_MAX, self.CUR_BASE + self.CUR_POR_GRADO * error)

        self.humedad += (hum_obj - self.humedad) * _alfa(dt_s, self.TAU_HUMEDAD)
        self.corriente += (cur_obj - self.corriente) * _alfa(dt_s, self.TAU_CORRIENTE)

        # orden fijo de consumo del rng: temperatura, corriente, humedad
        self._m_temp["value"] = round(self.temp + self._gauss(0.0, 0.05), 2)
        self._m_corriente["value"] = round(
            max(0.0, self.corriente + self._gauss(0.0, 0.1)), 2
        )
        self._m_humedad["value"] = round(
            min(100.0, max(0.0, self.humedad + self._gauss(0.0, 0.3))), 1
        )
        return self._lecturas


class SensorAmbiental:
    """sensor de patio, temperatura y humedad del aire.

    siguen el ciclo del dia: la temperatura sube hacia la tarde y baja en la
    noche, y la humedad hace lo contrario. encima de eso cada sensor tiene una
    deriva lenta propia, para que los 12 no marquen exactamente lo mismo.

    t = 0 se toma como la medianoche del inicio de la simulacion. si el
    generador parte a otra hora, el ciclo queda desfasado pero sigue siendo
    un ciclo de 24 h valido.
    """

    __slots__ = (
        "sensor_id", "rng", "t_s", "deriva_t", "deriva_h", "temp", "humedad",
        "_gauss", "_m_temp", "_m_humedad", "_lecturas",
    )

    TEMP_MEDIA, TEMP_AMPLITUD = 15.0, 4.0     # C, clima costero de coquimbo
    HUM_MEDIA, HUM_AMPLITUD = 78.0, 10.0      # %
    HORA_PEAK = 15.0                          # hora mas calurosa del dia
    DIA_S = 86400.0
    TAU = 300.0                               # el aire no cambia de golpe

    def __init__(self, sensor_id, rng):
        self.sensor_id = sensor_id
        self.rng = rng
        self._gauss = rng.gauss
        self.t_s = 0.0
        self.deriva_t = rng.uniform(-0.8, 0.8)
        self.deriva_h = rng.uniform(-3.0, 3.0)
        self.temp, self.humedad = self._objetivo()

        self._m_temp = {
            "sensor_id": sensor_id,
            "metric": "temperature",
            "value": 0.0,
            "unit": "C",
        }
        self._m_humedad = {
            "sensor_id": sensor_id,
            "metric": "humidity",
            "value": 0.0,
            "unit": "%",
        }
        self._lecturas = [self._m_temp, self._m_humedad]

    def _objetivo(self):
        # coseno con el maximo en HORA_PEAK; la humedad va en contrafase
        fase = 2.0 * math.pi * (self.t_s / self.DIA_S - self.HORA_PEAK / 24.0)
        c = math.cos(fase)
        temp = self.TEMP_MEDIA + self.TEMP_AMPLITUD * c + self.deriva_t
        hum = self.HUM_MEDIA - self.HUM_AMPLITUD * c + self.deriva_h
        return temp, hum

    def tick(self, dt_s):
        self.t_s += dt_s

        # la deriva camina despacio y queda acotada para que no se escape
        self.deriva_t = max(-1.5, min(1.5, self.deriva_t + self._gauss(0.0, 0.01)))
        self.deriva_h = max(-5.0, min(5.0, self.deriva_h + self._gauss(0.0, 0.03)))

        temp_obj, hum_obj = self._objetivo()
        a = _alfa(dt_s, self.TAU)
        self.temp += (temp_obj - self.temp) * a
        self.humedad += (hum_obj - self.humedad) * a

        self._m_temp["value"] = round(self.temp + self._gauss(0.0, 0.05), 2)
        self._m_humedad["value"] = round(
            min(100.0, max(0.0, self.humedad + self._gauss(0.0, 0.3))), 1
        )
        return self._lecturas


def _inventario():
    """los equipos del sitio 3 segun el inventario de lab1 1.1, en orden fijo.

    cada entrada es (clase, sensor_id, argumentos extra, puntos de medicion).
    los sensor_id siguen la convencion TIPO_SITIO_CORRELATIVO de lab1 3.2.

      6 fajas x 2 metricas (vibration, current)                =  12
      2 gruas x 2 metricas (current, weight)                   =   4
      1 bascula x 1 metrica (weight)                           =   1
      48 reefers x 3 metricas (temperature, current, humidity) = 144
      12 ambientales x 2 metricas (temperature, humidity)      =  24
                                                          total 185 puntos

    de los 48 reefers, 1 de cada 4 va con setpoint de +4 C (carga refrigerada,
    fruta) y el resto con -18 C (congelado).

    el orden no es libre: define la posicion global de cada punto de medicion
    dentro del tick, y con eso donde se corta el ultimo tick (ver
    generador.iter_eventos) y el orden en que se consume el rng.
    """
    inv = [(Faja, f"FAJA_S3_C{i}", (), 2) for i in range(1, 7)]
    inv.append((Grua, "GRUA_S3_STS01", (), 2))
    inv.append((Grua, "GRUA_S3_STS02", (), 2))
    inv.append((Bascula, "BASCULA_S3_01", (), 1))
    for i in range(1, 49):
        setpoint = 4.0 if i % 4 == 0 else -18.0
        inv.append((Reefer, f"REEFER_S3_{i:02d}", (setpoint,), 3))
    for i in range(1, 13):
        inv.append((SensorAmbiental, f"AMB_S3_{i:02d}", (), 2))
    return inv


def puntos_por_tick():
    """cuantos eventos produce el sitio completo en un tick, hoy 185."""
    return sum(p for _, _, _, p in _inventario())


def _validar_reparto(worker_id, n_workers):
    if n_workers < 1:
        raise ValueError(f"n_workers tiene que ser >= 1, llego {n_workers}")
    if n_workers > 1 and not 0 <= worker_id < n_workers:
        raise ValueError(
            f"worker_id {worker_id} fuera de rango para {n_workers} workers"
        )


def primeros_puntos(worker_id, n_workers=1):
    """la posicion global, dentro del tick, del primer punto de cada activo
    que le toca a este worker. va en el mismo orden que crear_activos.

    con esto el generador sabe que evento global es cada lectura, y puede
    cortar el ultimo tick exactamente igual sin importar cuantos workers haya.
    """
    _validar_reparto(worker_id, n_workers)
    posiciones = []
    acumulado = 0
    for i, (_, _, _, p) in enumerate(_inventario()):
        if n_workers == 1 or i % n_workers == worker_id:
            posiciones.append(acumulado)
        acumulado += p
    return posiciones


def crear_activos(semilla, worker_id, n_workers=1):
    """los activos que simula este worker.

    reparto por activos (punto 3): cada activo lo simula UN solo worker durante
    todo el periodo, asi cada sensor_id tiene una unica serie continua en el
    dataset. el activo i del inventario le toca al worker i % n_workers. con
    n_workers=1 (el valor por defecto) se crean todos, igual que antes.

    el reparto es por activo y no por punto, porque las metricas de un mismo
    activo salen del mismo estado fisico y no se pueden separar. como los
    activos tienen 1, 2 o 3 puntos, la carga no queda exacta: con 16 workers
    van de 10 a 13 puntos por worker, con 8 de 22 a 24.

    el rng lo armo aqui adentro, uno propio por worker con
    random.Random(semilla + worker_id), y se lo paso a cada clase en el
    constructor. si sembrara el modulo global antes de repartir el trabajo,
    los hijos heredarian el mismo estado y el dataset quedaria con n copias
    identicas de la misma serie

    el orden de construccion tampoco es libre: cada constructor consume
    numeros del rng, asi que si se reordena el inventario el stream se corre y
    el dataset cambia entero aunque la semilla sea la misma.
    """
    _validar_reparto(worker_id, n_workers)
    rng = random.Random(semilla + worker_id)
    activos = []
    for i, (clase, sid, extra, puntos) in enumerate(_inventario()):
        if n_workers == 1 or i % n_workers == worker_id:
            activo = clase(sid, rng, *extra)
            # si una clase cambia sus metricas y no se actualiza el inventario,
            # prefiero que reviente aqui y no que el corte del tick quede mal
            assert len(activo._lecturas) == puntos, sid
            activos.append(activo)
    return activos
