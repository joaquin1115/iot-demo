import network
import time
from machine import Pin, ADC
import dht
import urequests
import random
import ujson

# -------------------------
# CONFIG
# -------------------------

SERVER_URL = "<>"
SSID = "Wokwi-GUEST"
PASSWORD = ""

# -----------------------------
# PINES
# -----------------------------
dht_temp = dht.DHT22(Pin(15))  # DHT #1: temperatura
dht_hum = dht.DHT22(Pin(4))    # DHT #2: humedad

led_verde = Pin(21, Pin.OUT)
led_amarillo = Pin(19, Pin.OUT)
led_rojo = Pin(18, Pin.OUT)

# Apagar LEDs al inicio
led_verde.value(0)
led_amarillo.value(0)
led_rojo.value(0)

# -----------------------------
# FERMENTACIÓN - PARÁMETROS
# -----------------------------
TEMP_FERMENT_IDEAL = 32
TEMP_FERMENT_STD = 1.74
TEMP_FERMENT_MIN_CRITICO = 26
TEMP_FERMENT_MAX_CRITICO = 36
TEMP_FERMENT_MIN_ALERTA = 29
TEMP_FERMENT_MAX_ALERTA = 34
PROB_TEMP_FERMENT_FUERA = 0.08

HUM_FERMENT_IDEAL = 61.26
HUM_FERMENT_STD = 12.82
HUM_FERMENT_MIN_CRITICO = 40
HUM_FERMENT_MAX_CRITICO = 85
HUM_FERMENT_MIN_ALERTA = 45
HUM_FERMENT_MAX_ALERTA = 80
PROB_HUM_FERMENT_ANOMALA = 0.20

CO_FERMENT_IDEAL = 9.3
CO_FERMENT_STD = 5.3
CO_FERMENT_MAX_ALERTA = 25
CO_FERMENT_MAX_CRITICO = 50
PROB_CO_FERMENT_ELEVADO = 0.05

CO2_FERMENT_IDEAL = 620
CO2_FERMENT_STD = 189.4
CO2_FERMENT_MIN_ALERTA = 400
CO2_FERMENT_MAX_ALERTA = 1000
CO2_FERMENT_MIN_CRITICO = 300
CO2_FERMENT_MAX_CRITICO = 1600
PROB_CO2_FERMENT_PICO = 0.08


# -----------------------------
# Gaussian simulation (normal distribution)
# -----------------------------
def gauss_approx(mu, sigma):
    s = sum(random.random() for _ in range(12))
    return mu + sigma * (s - 6)

# -----------------------------
# Simulación de sensores
# -----------------------------
def simular_temperatura():
    if random.random() < PROB_TEMP_FERMENT_FUERA:
        return round(random.uniform(20, 40), 1)
    return round(gauss_approx(TEMP_FERMENT_IDEAL, TEMP_FERMENT_STD), 1)

def simular_humedad():
    if random.random() < PROB_HUM_FERMENT_ANOMALA:
        return round(random.uniform(35, 95), 1)
    return round(gauss_approx(HUM_FERMENT_IDEAL, HUM_FERMENT_STD), 1)

def simular_co():
    if random.random() < PROB_CO_FERMENT_ELEVADO:
        return round(random.uniform(25, 80), 1)
    return round(gauss_approx(CO_FERMENT_IDEAL, CO_FERMENT_STD), 1)

def simular_co2():
    if random.random() < PROB_CO2_FERMENT_PICO:
        return round(random.uniform(1200, 2000), 1)
    return round(gauss_approx(CO2_FERMENT_IDEAL, CO2_FERMENT_STD), 1)


# -----------------------------
# Clasificación y alertas LED
# -----------------------------
def evaluar_alerta(temp, hum, co, co2):
    alertas = []  
    nivel = "verde"

    # --- Temperatura ---
    if temp < TEMP_FERMENT_MIN_CRITICO or temp > TEMP_FERMENT_MAX_CRITICO:
        alertas.append("temperatura")
        nivel = "rojo"
    elif temp < TEMP_FERMENT_MIN_ALERTA or temp > TEMP_FERMENT_MAX_ALERTA:
        alertas.append("temperatura")
        if nivel != "rojo":
            nivel = "amarillo"

    # --- Humedad ---
    if hum < HUM_FERMENT_MIN_CRITICO or hum > HUM_FERMENT_MAX_CRITICO:
        alertas.append("humedad")
        nivel = "rojo"
    elif hum < HUM_FERMENT_MIN_ALERTA or hum > HUM_FERMENT_MAX_ALERTA:
        alertas.append("humedad")
        if nivel != "rojo":
            nivel = "amarillo"

    # --- CO ---
    if co > CO_FERMENT_MAX_CRITICO:
        alertas.append("co")
        nivel = "rojo"
    elif co > CO_FERMENT_MAX_ALERTA:
        alertas.append("co")
        if nivel != "rojo":
            nivel = "amarillo"

    # --- CO2 ---
    if co2 < CO2_FERMENT_MIN_CRITICO or co2 > CO2_FERMENT_MAX_CRITICO:
        alertas.append("co2")
        nivel = "rojo"
    elif (co2 < CO2_FERMENT_MIN_ALERTA or co2 > CO2_FERMENT_MAX_ALERTA):
        alertas.append("co2")
        if nivel != "rojo":
            nivel = "amarillo"

    # ---------------- LED CONTROL ----------------
    led_verde.value(0)
    led_amarillo.value(0)
    led_rojo.value(0)

    if nivel == "verde":
        led_verde.value(1)
    elif nivel == "amarillo":
        led_amarillo.value(1)
    else:
        led_rojo.value(1)

    return "-".join(alertas) if alertas else "normal", nivel


# -----------------------------
# Conectar WiFi
# -----------------------------
print("Conectando WiFi...", end="")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)

while not sta.isconnected():
    print(".", end="")
    time.sleep(0.2)
print(" conectado!")


# -----------------------------
# LOOP PRINCIPAL
# -----------------------------
while True:
    for i in range (10):
        try:
            temp = simular_temperatura()
            hum = simular_humedad()
            co = simular_co()
            co2 = simular_co2()

            #print("T:", temp, "H:", hum, "CO:", co, "CO2:", co2)

            alerta, nivel = evaluar_alerta(temp, hum, co, co2)

            # Mantener LED visible
            time.sleep(1)

            # Apagar LEDs
            led_verde.value(0)
            led_amarillo.value(0)
            led_rojo.value(0)

            payload = {
                "proceso": "fermentacion",
                "sensor_id": "ferment_1",
                "temperatura": temp,
                "humedad": hum,
                "co": co,
                "co2": co2,
                "alerta": alerta,
                "nivel_alerta": nivel,
                "timestamp": time.time()
            }

            print("Enviando:", payload)
            r = urequests.post(SERVER_URL, json=payload)
            print("Resp:", r.status_code)
            r.close()

        except Exception as e:
            print("Error:", e)

        time.sleep(2)
    print("Esperando 10 segundos para siguiente ciclo...\n")
    time.sleep(10)
