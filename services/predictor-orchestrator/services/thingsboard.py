import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ThingsBoardClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = httpx.Timeout(10.0)
    
    async def send_predictions(self, access_token: str, predictions: List[Dict[str, Any]]) -> bool:
        """
        Envía múltiples predicciones a ThingsBoard.
        """
        url = f"{self.base_url}/api/v1/{access_token}/telemetry"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Enviar cada predicción
                for pred in predictions:
                    response = await client.post(url, json=pred)
                    response.raise_for_status()
                
                logger.info(f"✅ {len(predictions)} predictions sent to ThingsBoard")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error sending predictions to ThingsBoard: {e}")
            return False

