import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebSocketEmitter:
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url.rstrip('/')
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """
        Emite un evento al WebSocket Gateway.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{self.websocket_url}/emit",
                    json={
                        "event_type": event_type,
                        "data": data
                    }
                )
                logger.debug(f"Event emitted: {event_type}")
        except Exception as e:
            logger.warning(f"Could not emit event to WebSocket: {e}")
