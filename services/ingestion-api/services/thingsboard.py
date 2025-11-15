import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ThingsBoardClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = httpx.Timeout(10.0)
    
    async def send_telemetry(self, access_token: str, data: Dict[str, Any]) -> bool:
        """
        Envía telemetría a ThingsBoard.
        
        Args:
            access_token: Token de acceso del device
            data: Diccionario con los datos a enviar
        
        Returns:
            True si fue exitoso, False en caso contrario
        """
        url = f"{self.base_url}/api/v1/{access_token}/telemetry"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                
                logger.info(f"✅ Data sent to ThingsBoard: {data.get('proceso', 'unknown')}")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error sending to ThingsBoard: {e.response.status_code}")
            logger.error(f"   Response: {e.response.text}")
            return False
        except httpx.RequestError as e:
            logger.error(f"❌ Request error sending to ThingsBoard: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False