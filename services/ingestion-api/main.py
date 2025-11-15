from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .config import settings
from .services.thingsboard import ThingsBoardClient
from .services.websocket_client import WebSocketEmitter
from .routers import amasado, fermentacion

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app
app = FastAPI(
    title="Ingestion API",
    description="API para recibir datos de Wokwi y enviar a ThingsBoard",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clientes globales
tb_client = ThingsBoardClient(settings.THINGSBOARD_URL)
ws_emitter = WebSocketEmitter(settings.WEBSOCKET_URL)

# Registrar routers
app.include_router(amasado.router)
app.include_router(fermentacion.router)

@app.get("/")
async def root():
    return {
        "service": "Ingestion API",
        "status": "running",
        "endpoints": ["/amasado", "/fermentacion"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)