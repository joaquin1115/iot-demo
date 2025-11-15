import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ThingsBoard
    THINGSBOARD_URL = os.getenv("THINGSBOARD_URL", "https://thingsboard.cloud")
    TB_AMASADO_TOKEN = os.getenv("TB_AMASADO_TOKEN")
    TB_FERMENTACION_TOKEN = os.getenv("TB_FERMENTACION_TOKEN")
    
    # WebSocket Gateway
    WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "http://websocket-gateway:8000")
    
    # API
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

settings = Settings()
