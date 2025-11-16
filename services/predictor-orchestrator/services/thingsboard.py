import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ThingsBoardClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = httpx.Timeout(10.0)
    
    async def send_telemetry(self, access_token: str, data: Dict[str, Any]) -> bool:
        """
        Envía telemetría a un dispositivo específico de ThingsBoard.
        
        Args:
            access_token: Token del dispositivo
            data: Datos a enviar
        
        Returns:
            True si fue exitoso
        """
        url = f"{self.base_url}/api/v1/{access_token}/telemetry"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                logger.info(f"✅ Telemetry sent to ThingsBoard")
                return True
        except Exception as e:
            logger.error(f"❌ Error sending to ThingsBoard: {e}")
            return False
    
    async def send_predictions_batch(
        self, 
        color_token: str,
        texture_token: str,
        size_token: str,
        color_predictions: List[Dict[str, Any]],
        texture_predictions: List[Dict[str, Any]],
        size_predictions: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """
        Envía predicciones a los 3 dispositivos de ThingsBoard correspondientes.
        
        Returns:
            Diccionario con el estado de envío de cada tipo
        """
        results = {
            "color": False,
            "texture": False,
            "size": False
        }
        
        # Enviar predicciones de COLOR
        if color_predictions and color_token:
            logger.info(f"📤 Sending {len(color_predictions)} color predictions to ThingsBoard")
            for pred in color_predictions:
                data = {
                    "proceso": "prediccion_color",
                    "timestamp": pred.get("timestamp"),
                    **pred
                }
                success = await self.send_telemetry(color_token, data)
                if not success:
                    logger.warning(f"Failed to send color prediction: {pred.get('image')}")
            results["color"] = True
        
        # Enviar predicciones de TEXTURE
        if texture_predictions and texture_token:
            logger.info(f"📤 Sending {len(texture_predictions)} texture predictions to ThingsBoard")
            for pred in texture_predictions:
                data = {
                    "proceso": "prediccion_texture",
                    "timestamp": pred.get("timestamp"),
                    **pred
                }
                success = await self.send_telemetry(texture_token, data)
                if not success:
                    logger.warning(f"Failed to send texture prediction: {pred.get('image')}")
            results["texture"] = True
        
        # Enviar predicciones de SIZE
        if size_predictions and size_token:
            logger.info(f"📤 Sending {len(size_predictions)} size predictions to ThingsBoard")
            for pred in size_predictions:
                data = {
                    "proceso": "prediccion_size",
                    "timestamp": pred.get("timestamp"),
                    **pred
                }
                success = await self.send_telemetry(size_token, data)
                if not success:
                    logger.warning(f"Failed to send size prediction: {pred.get('image')}")
            results["size"] = True
        
        return results
