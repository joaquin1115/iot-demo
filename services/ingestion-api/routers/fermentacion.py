from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fermentacion", tags=["fermentacion"])

class FermentacionData(BaseModel):
    proceso: str = Field(default="fermentacion")
    sensor_id: str
    temperatura: float
    humedad: float
    co: float
    co2: float
    alerta: Optional[str] = None
    nivel_alerta: Optional[str] = None
    timestamp: float

@router.post("")
async def receive_fermentacion(data: FermentacionData):
    """
    Recibe datos del proceso de fermentación desde Wokwi.
    """
    from main import tb_client, ws_emitter
    from config import settings
    
    logger.info(f"📥 Received fermentacion data: temp={data.temperatura}°C, CO2={data.co2}")
    
    # Enviar a ThingsBoard
    success = await tb_client.send_telemetry(
        settings.TB_FERMENTACION_TOKEN,
        data.model_dump()
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send data to ThingsBoard"
        )
    
    # Emitir evento para el dashboard
    await ws_emitter.emit_event("fermentacion", data.model_dump())
    
    return {
        "status": "success",
        "message": "Data received and forwarded to ThingsBoard",
        "proceso": "fermentacion"
    }
