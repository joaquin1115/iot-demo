import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ML Services
    ML_COLOR_URL = os.getenv("ML_SERVICE_COLOR_URL", "http://ml-service-color:8000")
    ML_TEXTURE_URL = os.getenv("ML_SERVICE_TEXTURE_URL", "http://ml-service-texture:8000")
    ML_SIZE_URL = os.getenv("ML_SERVICE_SIZE_URL", "http://ml-service-size:8000")
    
    # ThingsBoard - Un token por cada modelo
    THINGSBOARD_URL = os.getenv("THINGSBOARD_URL", "https://thingsboard.cloud")
    TB_PREDICTIONS_COLOR_TOKEN = os.getenv("TB_PREDICTIONS_COLOR_TOKEN")
    TB_PREDICTIONS_TEXTURE_TOKEN = os.getenv("TB_PREDICTIONS_TEXTURE_TOKEN")
    TB_PREDICTIONS_SIZE_TOKEN = os.getenv("TB_PREDICTIONS_SIZE_TOKEN")
    
    # WebSocket Gateway
    WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "http://websocket-gateway:8000")
    
    # API
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Timeout para ML services (pueden tardar)
    ML_TIMEOUT = 120.0

settings = Settings()