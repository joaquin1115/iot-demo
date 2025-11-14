import network
import time
from machine import Pin
import dht
import ujson
import urequests
import random


# CONFIG

SERVER_URL = "http://<>"
SSID = "Wokwi-GUEST"
PASSWORD = ""


sensor_temp = dht.DHT22(Pin(15))
sensor_hum = dht.DHT22(Pin(4))


# LEDs del semáforo

led_verde = Pin(13, Pin.OUT)
led_amarillo = Pin(12, Pin.OUT)
led_rojo = Pin(14, Pin.OUT)

led_verde.value(0)
led_amarillo.value(0)
led_rojo.value(0)


# RANGOS DEL AMASADO

TEMP_IDEAL = 25.5
TEMP_STD = 1.5

TEMP_CRIT_MIN = 22
TEMP_CRIT_MAX = 29
TEMP_ALR_MIN = 23.5
TEMP_ALR_MAX = 27.5

HUM_IDEAL = 60
HUM_STD = 6

HUM_CRIT_MIN = 45
HUM_CRIT_MAX = 75
HUM_ALR_MIN = 50
HUM_ALR_MAX = 70


# Ruido gaussiano

def gauss(mu, sigma):
    s = sum(random.random() for _ in range(12))
    return mu + sigma * (s - 6)


# Detección del tipo de alerta

def detectar_fuente_alerta(temp, hum):
    alerta_temp = "normal"
    alerta_hum = "normal"

    # Temperatura
    if temp < TEMP_CRIT_MIN or temp > TEMP_CRIT_MAX:
        alerta_temp = "critico"
    elif temp < TEMP_ALR_MIN or temp > TEMP_ALR_MAX:
        alerta_temp = "alerta"

    # Humedad
    if hum < HUM_CRIT_MIN or hum > HUM_CRIT_MAX:
        alerta_hum = "critico"
    elif hum < HUM_ALR_MIN or hum > HUM_ALR_MAX:
        alerta_hum = "alerta"

    # Elegir mensaje
    if alerta_temp in ("alerta", "critico") and alerta_hum in ("alerta", "critico"):
        return "temperatura y humedad"

    if alerta_temp in ("alerta", "critico"):
        return "temperatura"

    if alerta_hum in ("alerta", "critico"):
        return "humedad"

    return "-"


# Clasificación del semáforo

def evaluar_alerta(temp, hum):
    led_verde.value(0)
    led_amarillo.value(0)
    led_rojo.value(0)

    # CRÍTICO (rojo)
    if temp < TEMP_CRIT_MIN or temp > TEMP_CRIT_MAX:
        led_rojo.value(1)
        return "critico-temp"

    if hum < HUM_CRIT_MIN or hum > HUM_CRIT_MAX:
        led_rojo.value(1)
        return "critico-humedad"

    # ALERTA (amarillo)
    if temp < TEMP_ALR_MIN or temp > TEMP_ALR_MAX:
        led_amarillo.value(1)
        return "alerta-temp"

    if hum < HUM_ALR_MIN or hum > HUM_ALR_MAX:
        led_amarillo.value(1)
        return "alerta-humedad"

    # NORMAL (verde)
    led_verde.value(1)
    return "normal"


# Conectar WiFi

print("Conectando a WiFi", end="")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)

while not sta.isconnected():
    print(".", end="")
    time.sleep(0.1)

print(" ¡Conectado!")


# LOOP PRINCIPAL

while True:
  for i in range (10):
    try:
        temp = round(gauss(TEMP_IDEAL, TEMP_STD), 1)
        hum = round(gauss(HUM_IDEAL, HUM_STD), 1)

        #print("Temp:", temp, " Hum:", hum)

        estado = evaluar_alerta(temp, hum)
        tipo_alerta = detectar_fuente_alerta(temp, hum)

        time.sleep(1)

        led_verde.value(0)
        led_amarillo.value(0)
        led_rojo.value(0)

        # Payload
        data = {
            "proceso": "amasado",
            "sensor_id": "amasado_1",
            "temperature": temp,
            "humidity": hum,
            "estado": estado,
            "alerta": tipo_alerta,
            "timestamp": time.time()
        }

        print("Enviando:", data)

        r = urequests.post(SERVER_URL, json=data)
        print("Respuesta:", r.status_code)
        r.close()

    except Exception as e:
        print("Error:", e)

    time.sleep(2)

  print("Esperando 10 segundos para siguiente ciclo...\n")
  time.sleep(10)
