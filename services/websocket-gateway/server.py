from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import json
import asyncio

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app
app = FastAPI(
    title="WebSocket Gateway",
    description="Gateway para comunicación en tiempo real con el dashboard",
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

# Modelo para eventos
class Event(BaseModel):
    event_type: str
    data: Dict[str, Any]

# Gestor de conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"❌ Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """
        Envía un mensaje a todos los clientes conectados.
        """
        if not self.active_connections:
            logger.debug("No clients connected, skipping broadcast")
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones muertas
        for conn in disconnected:
            try:
                self.disconnect(conn)
            except ValueError:
                pass  # Ya fue removida

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "service": "WebSocket Gateway",
        "status": "running",
        "active_connections": len(manager.active_connections)
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "connections": len(manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para que el dashboard se conecte.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Mantener conexión viva
            # El cliente puede enviar pings, pero no es necesario procesar
            data = await websocket.receive_text()
            
            # Opcional: responder a pings
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.post("/emit")
async def emit_event(event: Event):
    """
    Endpoint HTTP para que otros servicios emitan eventos.
    Los eventos se envían a todos los clientes WebSocket conectados.
    """
    logger.info(f"📤 Emitting event: {event.event_type}")
    
    message = {
        "type": event.event_type,
        "data": event.data
    }
    
    await manager.broadcast(message)
    
    return {
        "status": "success",
        "event_type": event.event_type,
        "clients_notified": len(manager.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    from .config import settings
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)