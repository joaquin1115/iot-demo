# 🍞 Sistema IoT + ML para Análisis de Producción de Pan

Sistema de microservicios para monitoreo en tiempo real de procesos de amasado y fermentación, con análisis automatizado mediante Machine Learning de características de pan (color, textura y tamaño).

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📑 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Reference](#-api-reference)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Troubleshooting](#-troubleshooting)
- [Contribuir](#-contribuir)

---

## ✨ Características

### 🏭 Monitoreo de Procesos IoT
- ✅ Ingesta de datos en tiempo real desde sensores Wokwi
- ✅ Monitoreo de proceso de amasado (temperatura, humedad)
- ✅ Monitoreo de proceso de fermentación (temperatura, humedad, CO, CO2)
- ✅ Envío automático a ThingsBoard para visualización

### 🤖 Análisis ML Automatizado
- ✅ Predicción de color del pan (Normal/Quemado)
- ✅ Análisis de textura de la corteza
- ✅ Medición de dimensiones (ancho, alto, volumen)
- ✅ Procesamiento de 20 imágenes cada 60 segundos
- ✅ 3 modelos ML independientes en paralelo

### 🏗️ Arquitectura de Microservicios
- ✅ 8 servicios independientes y escalables
- ✅ Comunicación asíncrona
- ✅ Alta disponibilidad
- ✅ Fácil mantenimiento y actualización

---

### Flujo de Datos

#### Flujo 1: Datos de Sensores (Tiempo Real)
```
Wokwi → Ingestion API → ThingsBoard → WebSocket → Dashboard
                     ↓
              [Validación y transformación]
```

#### Flujo 2: Predicciones ML (Cada 60 segundos)
```
Scheduler → Selecciona 20 imágenes aleatorias
          ↓
Orchestrator → Llama a 3 ML Services en paralelo
             ↓
    ┌────────┼────────┐
    ▼        ▼        ▼
 ML Color  Texture  Size
    │        │        │
    └────────┼────────┘
             ▼
    Agrega resultados
             ▼
    ThingsBoard (3 dispositivos separados)
             ▼
    WebSocket → Dashboard
```

---

## 🛠️ Tecnologías

### Backend
- **Python 3.11** - Lenguaje principal
- **FastAPI** - Framework web asíncrono
- **Uvicorn** - Servidor ASGI
- **APScheduler** - Tareas programadas

### Machine Learning
- **TensorFlow 2.13** - Framework ML
- **Keras** - API de alto nivel
- **OpenCV** - Procesamiento de imágenes
- **NumPy** - Computación numérica
- **Scikit-learn** - Preprocesamiento

### IoT & Cloud
- **ThingsBoard Cloud** - Plataforma IoT
- **WebSockets** - Comunicación en tiempo real
- **Wokwi** - Simulación de sensores IoT

### DevOps
- **Docker** - Contenedores
- **Docker Compose** - Orquestación
- **Git** - Control de versiones

### Frontend
- **React** - Framework UI
- **Socket.IO** - Cliente WebSocket

---

## 📋 Requisitos Previos

### Software Necesario

- ✅ **Docker Desktop** (20.10+)
  - [Descargar para Windows](https://www.docker.com/products/docker-desktop)
  - [Descargar para Mac](https://www.docker.com/products/docker-desktop)
  - [Descargar para Linux](https://docs.docker.com/engine/install/)

- ✅ **Python 3.11** (solo para desarrollo)
  - [Descargar](https://www.python.org/downloads/)

- ✅ **Git**
  - [Descargar](https://git-scm.com/downloads)

### Cuentas Necesarias

- ✅ **ThingsBoard Cloud** (gratuita)
  - [Registrarse](https://thingsboard.cloud/signup)

### Recursos del Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Disco | 10 GB | 20 GB |
| Red | 10 Mbps | 100 Mbps |

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/iot-ml-pan.git
cd iot-ml-pan
```

### 3. Preparar Modelos y Datasets

1. Descargar los [datasets](https://drive.google.com/drive/folders/1hFguW8BkhPn2aKXaPtJwKgR1yASpYMvY?usp=sharing)
2. Copiar el contenido en `ml/datasets/`

---

## ⚙️ Configuración

### 1. Configurar ThingsBoard

**Crear 5 dispositivos en ThingsBoard:**

1. Ir a [https://thingsboard.cloud](https://thingsboard.cloud)
2. Navegar a **Devices** → **"+" (Add Device)**
3. Crear los siguientes dispositivos:

| Device Name | Descripción | Variable .env |
|-------------|-------------|---------------|
| `Amasado` | Proceso de amasado | `TB_AMASADO_TOKEN` |
| `Fermentacion` | Proceso de fermentación | `TB_FERMENTACION_TOKEN` |
| `Prediccion_Color` | ML - Color | `TB_PREDICTIONS_COLOR_TOKEN` |
| `Prediccion_Texture` | ML - Textura | `TB_PREDICTIONS_TEXTURE_TOKEN` |
| `Prediccion_Size` | ML - Tamaño | `TB_PREDICTIONS_SIZE_TOKEN` |

4. Para cada dispositivo:
   - Click en el dispositivo
   - Ir a **"Details"**
   - Copiar el **Access Token**

📖 [Ver guía detallada de ThingsBoard](docs/thingsboard-setup.md)

### 2. Configurar Variables de Entorno

```bash
cd services
cp .env.example .env
nano .env  # o notepad .env en Windows
```

Editar `.env`:

```bash
# ThingsBoard Configuration
THINGSBOARD_URL=https://thingsboard.cloud

# ThingsBoard Access Tokens - Procesos
TB_AMASADO_TOKEN=tu_token_amasado_aqui
TB_FERMENTACION_TOKEN=tu_token_fermentacion_aqui

# ThingsBoard Access Tokens - ML Models
TB_PREDICTIONS_COLOR_TOKEN=tu_token_color_aqui
TB_PREDICTIONS_TEXTURE_TOKEN=tu_token_texture_aqui
TB_PREDICTIONS_SIZE_TOKEN=tu_token_size_aqui

# Scheduler Configuration
SCHEDULE_INTERVAL=60
NUM_IMAGES=20
```

⚠️ **Importante:** Reemplazar todos los `tu_token_*` con los tokens reales de ThingsBoard.

### 3. Verificar Configuración

```bash
# Verificar que Docker está corriendo
docker info
```

---

## 🎯 Uso

### Iniciar el Sistema

```bash
cd services

# Iniciar todos los servicios
docker-compose up --build

# O en segundo plano
docker-compose up -d --build
```

### Verificar Estado

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f ingestion-api

# Ver estado de contenedores
docker-compose ps
```

Deberías ver todos los servicios como **"Up"**:

```
NAME                      STATUS
ingestion-api             Up
scheduler-service         Up
predictor-orchestrator    Up
ml-service-color          Up
ml-service-texture        Up
ml-service-size           Up
websocket-gateway         Up
dashboard                 Up
```

### Health Checks

```bash
# Verificar APIs
curl http://localhost:8001/health  # Ingestion API
curl http://localhost:8002/health  # Orchestrator
curl http://localhost:8101/health  # ML Color
curl http://localhost:8102/health  # ML Texture
curl http://localhost:8103/health  # ML Size
curl http://localhost:8003/health  # WebSocket Gateway
```

Todos deben devolver: `{"status":"healthy"}`

### Acceder al Dashboard

Abrir en el navegador: [http://localhost:3000](http://localhost:3000)

Deberías ver:
- 📊 Datos de amasado en tiempo real
- 📊 Datos de fermentación en tiempo real
- 🤖 Predicciones ML cada 60 segundos

### Enviar Datos de Prueba

#### Amasado (desde Wokwi o manualmente):

```bash
curl -X POST http://localhost:8001/amasado \
  -H "Content-Type: application/json" \
  -d '{
    "proceso": "amasado",
    "sensor_id": "amasado_1",
    "temperature": 25.5,
    "humidity": 65.0,
    "estado": "normal",
    "alerta": null,
    "timestamp": 1700000000
  }'
```

#### Fermentación:

```bash
curl -X POST http://localhost:8001/fermentacion \
  -H "Content-Type: application/json" \
  -d '{
    "proceso": "fermentacion",
    "sensor_id": "ferment_1",
    "temperatura": 28.0,
    "humedad": 70.0,
    "co": 5.0,
    "co2": 400.0,
    "alerta": null,
    "nivel_alerta": null,
    "timestamp": 1700000000
  }'
```

### Detener el Sistema

```bash
# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Eliminar también volúmenes
docker-compose down -v
```

---

## 📚 API Reference

### Ingestion API (Puerto 8001)

#### POST /amasado
Recibe datos del proceso de amasado.

**Request:**
```json
{
  "proceso": "amasado",
  "sensor_id": "amasado_1",
  "temperature": 25.5,
  "humidity": 65.0,
  "estado": "normal",
  "alerta": null,
  "timestamp": 1700000000
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data received and forwarded to ThingsBoard",
  "proceso": "amasado"
}
```

#### POST /fermentacion
Recibe datos del proceso de fermentación.

**Request:**
```json
{
  "proceso": "fermentacion",
  "sensor_id": "ferment_1",
  "temperatura": 28.0,
  "humedad": 70.0,
  "co": 5.0,
  "co2": 400.0,
  "alerta": null,
  "nivel_alerta": null,
  "timestamp": 1700000000
}
```

### Predictor Orchestrator (Puerto 8002)

#### POST /predict-batch
Procesa un lote de imágenes con los 3 modelos ML.

**Request:**
```json
{
  "color_images": ["/datasets/color/pan_001.jpg", "..."],
  "texture_images": ["/datasets/texture/tex_001.jpg", "..."],
  "size_images": ["/datasets/size/size_001.jpg", "..."]
}
```

**Response:**
```json
{
  "total_processed": 60,
  "color_processed": 20,
  "texture_processed": 20,
  "size_processed": 20,
  "success": true,
  "predictions": {
    "color": [...],
    "texture": [...],
    "size": [...]
  },
  "timestamp": 1700000000
}
```

### ML Services (Puertos 8101, 8102, 8103)

#### POST /predict
Predice características de una imagen.

**Request:**
```json
{
  "image_path": "/datasets/color/pan_001.jpg"
}
```

**Response (Color):**
```json
{
  "image": "pan_001.jpg",
  "prediction": 0,
  "probability": 0.15,
  "estado": "Normal",
  "confidence": 0.85,
  "color_oscuro_r": 45.2,
  "color_promedio_r": 120.5,
  "color_claro_r": 200.1,
  "..."
}
```

---

## 📁 Estructura del Proyecto

```
iot-ml-pan/
│
├── ml/                              # Modelos y datasets
│   ├───datasets/
│   │   ├───dataset-color/
│   │   ├───dataset-size/
│   │   └───dataset-texture/
│   └───models/
│       ├───modelo-color/
│       ├───modelo-size/
│       └───modelo-texture/
│   └── README.md
│
├── services/                        # Microservicios
│   ├── docker-compose.yml           # Orquestación
│   ├── .env                         # Variables de entorno
│   ├── .env.example                 # Template
│   │
│   ├── ingestion-api/               # API de ingesta
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── amasado.py
│   │   │   └── fermentacion.py
│   │   └── services/
│   │       ├── thingsboard.py
│   │       └── websocket_client.py
│   │
│   ├── scheduler-service/           # Scheduler de tareas
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── scheduler.py
│   │   └── config.py
│   │
│   ├── predictor-orchestrator/      # Orquestador ML
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── config.py
│   │   └── services/
│   │       ├── ml_client.py
│   │       ├── thingsboard.py
│   │       └── websocket_client.py
│   │
│   ├── ml-service-color/            # Servicio ML Color
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   └── predictor.py
│   │
│   ├── ml-service-texture/          # Servicio ML Textura
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   └── predictor.py
│   │
│   ├── ml-service-size/             # Servicio ML Tamaño
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   └── predictor.py
│   │
│   ├── websocket-gateway/           # Gateway WebSocket
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── server.py
│   │   └── config.py
│   │
│   └── dashboard/                   # Frontend React
│       ├── Dockerfile
│       ├── package.json
│       ├── public/
│       └── src/
│
├── docs/                            # Documentación
│   ├── architecture.md
│   ├── thingsboard-setup.md
│   └── api-reference.md
│
├── .gitignore
└── README.md                        # Este archivo
```

---

## 📚 Referencias

- [Documentación de ThingsBoard](https://thingsboard.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [Docker Documentation](https://docs.docker.com/)