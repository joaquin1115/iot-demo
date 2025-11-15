import httpx
import logging
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class MLClient:
    def __init__(self, service_name: str, service_url: str, timeout: float = 120.0):
        self.service_name = service_name
        self.service_url = service_url.rstrip('/')
        self.timeout = httpx.Timeout(timeout)
    
    async def predict(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Llama al servicio ML para obtener una predicción.
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con la predicción o None si falla
        """
        url = f"{self.service_url}/predict"
        payload = {"image_path": image_path}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Calling {self.service_name} for {image_path}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ {self.service_name} prediction: {result.get('estado', 'unknown')}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ {self.service_name} HTTP error: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"❌ {self.service_name} request error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ {self.service_name} unexpected error: {e}")
            return None


class MLOrchestrator:
    def __init__(self, color_url: str, texture_url: str, size_url: str, timeout: float):
        self.color_client = MLClient("ML-Color", color_url, timeout)
        self.texture_client = MLClient("ML-Texture", texture_url, timeout)
        self.size_client = MLClient("ML-Size", size_url, timeout)
    
    async def predict_all(self, image_path: str) -> Dict[str, Any]:
        """
        Ejecuta predicciones de los 3 modelos en paralelo.
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con todas las predicciones
        """
        logger.info(f"🔄 Starting predictions for {image_path}")
        
        # Ejecutar en paralelo
        results = await asyncio.gather(
            self.color_client.predict(image_path),
            self.texture_client.predict(image_path),
            self.size_client.predict(image_path),
            return_exceptions=True
        )
        
        color_result, texture_result, size_result = results
        
        # Construir resultado consolidado
        prediction = {
            "image": image_path,
            "color": color_result if not isinstance(color_result, Exception) else None,
            "texture": texture_result if not isinstance(texture_result, Exception) else None,
            "size": size_result if not isinstance(size_result, Exception) else None,
            "success": {
                "color": color_result is not None and not isinstance(color_result, Exception),
                "texture": texture_result is not None and not isinstance(texture_result, Exception),
                "size": size_result is not None and not isinstance(size_result, Exception)
            }
        }
        
        logger.info(f"✅ Predictions completed for {image_path}")
        return prediction
