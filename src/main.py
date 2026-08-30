"""fase 1 del proyecto, terminal puerto coquimbo sitio 3.

cada worker escribe su propio archivo .jsonl porque estamos usando la opcion B de arquitectura.

para correrlo: python src/main.py"""

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path

from esquema import formatear_evento

DT_MS = 15_000              # cada tick del reloj simulado avanza 15 segundos
DT_S = DT_MS / 1000.0
LOTE_BUFFER = 10_000        # cuantas lineas junto antes de mandarlas al archivo


def _alfa(dt_s, tau_s):
    """me da la fraccion que avanza una magnitud hacia su objetivo en cada tick.

    seria el 1 - exp(-dt/tau) de siempre pero no puedo importar math, asi que
    lo dejo como division y queda igual, el valor se va acercando de a poco y
    nunca llega de golpe. si tau es chico responde mas rapido.
    """
    return dt_s / (tau_s + dt_s)


class Faja:
    """faja transportadora, la vibracion y la corriente van siguiendo a la carga."""

    VIB_VACIO, VIB_PLENA = 1.2, 6.5      # mm/s
    CUR_VACIO, CUR_PLENA = 18.0, 95.0    # A
    TAU_MARCHA = 45.0                    # cuando esta andando normal
    TAU_PARADA = 6.0                     # al parar baja rapido pero no de golpe

    def __init__(self, sensor_id, rng):
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

        # el max(0.0, ...) es para que el ruido no me deje valores negativos
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
    """grua sts, hace el ciclo de izar, trasladar y bajar.

    el peso lo fijo cuando toma la carga y no lo vuelvo a tocar hasta que la suelta.
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
            # entre una lectura y la otra
            {
                "sensor_id": self.sensor_id,
                "metric": "weight",
                "value": self.peso,
                "unit": "kg",
            },
        ]


class Bascula:
    """bascula de la entrada, mientras el camion esta encima el peso se queda quieto."""

    def __init__(self, sensor_id, rng):
        self.sensor_id = sensor_id
        self.rng = rng
        self.peso_base = 0.0
        self.restantes = rng.randint(2, 6)

    def tick(self, dt_s):
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


def crear_activos(rng):
    """los equipos del sitio 3, son 6 fajas, 2 gruas sts y 1 bascula."""
    activos = [Faja(f"FAJA_S3_C{i}", rng) for i in range(1, 7)]
    activos.append(Grua("GRUA_S3_STS01", rng))
    activos.append(Grua("GRUA_S3_STS02", rng))
    activos.append(Bascula("BASCULA_S3_01", rng))
    return activos


def worker_shard(wid, n_eventos, carpeta, semilla):
    """genera n_eventos y me los deja escritos en carpeta/part-<wid>.jsonl."""
    rng = random.Random(semilla + wid)          # rng mio, nunca el random global
    activos = crear_activos(rng)

    # esta es la unica vez que miro la hora real, de aqui en adelante voy sumando
    # milisegundos enteros asi no se me desfasa el reloj
    t_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    # me guardo el prefijo de la fecha y solo lo rearmo cuando cambia el segundo
    seg_cache = -1
    prefijo = ""

    ruta = Path(carpeta) / f"part-{wid:03d}.jsonl"
    buf = []
    escritos = 0

    with open(ruta, "w", encoding="utf-8", newline="\n", buffering=4 * 1024 * 1024) as f:
        while escritos < n_eventos:
            seg, ms = divmod(t_ms, 1000)
            if seg != seg_cache:
                seg_cache = seg
                prefijo = datetime.fromtimestamp(seg, timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S."
                )
            timestamp_str = f"{prefijo}{ms:03d}Z"

            for activo in activos:
                for metadatos in activo.tick(DT_S):
                    if escritos >= n_eventos:      # corto aqui aunque el tick no termine
                        break
                    ev = formatear_evento(timestamp_str, metadatos, wid)
                    buf.append(json.dumps(ev, separators=(",", ":")) + "\n")
                    escritos += 1

                    # cuando junto el lote lo mando de una y vacio la lista
                    if len(buf) >= LOTE_BUFFER:
                        f.writelines(buf)
                        buf = []
                if escritos >= n_eventos:
                    break

            t_ms += DT_MS

        # lo que quedo sin alcanzar el lote completo
        if buf:
            f.writelines(buf)

    # el stat va aqui afuera, con el archivo ya cerrado, si no me da menos bytes
    return {
        "worker_id": wid,
        "archivo": ruta.name,
        "eventos": escritos,
        "bytes": ruta.stat().st_size,
    }


if __name__ == "__main__":
    carpeta = Path("data/raw")
    carpeta.mkdir(parents=True, exist_ok=True)

    inicio = time.perf_counter()
    stats = worker_shard(0, 100_000, carpeta, 42)
    transcurrido = time.perf_counter() - inicio

    print(stats)
    print(f"eventos/s: {stats['eventos'] / transcurrido:,.0f}")
