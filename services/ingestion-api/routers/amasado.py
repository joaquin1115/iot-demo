from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/amasado", tags=["amasado"])

class AmasadoData(BaseModel):
    proceso: str = Field(default="amasado")
    sensor_id: str
    temperature: float
    humidity: float
    estado: str
    alerta: Optional[str] = None
    timestamp: float

@router.post("")
async def receive_amasado(data: AmasadoData):
    """
    Recibe datos del proceso de amasado desde Wokwi.
    """
    from main import tb_client, ws_emitter
    from config import settings
    
    logger.info(f"📥 Received amasado data: temp={data.temperature}°C")
    
    # Enviar a ThingsBoard
    success = await tb_client.send_telemetry(
        settings.TB_AMASADO_TOKEN,
        data.model_dump()
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send data to ThingsBoard"
        )
    
    # Emitir evento para el dashboard
    await ws_emitter.emit_event("amasado", data.model_dump())
    
    return {
        "status": "success",
        "message": "Data received and forwarded to ThingsBoard",
        "proceso": "amasado"
    }
