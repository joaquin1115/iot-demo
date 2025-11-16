from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
import logging
import time
from .config import settings
from .services.ml_client import MLOrchestrator
from .services.thingsboard import ThingsBoardClient
from .services.websocket_client import WebSocketEmitter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app
app = FastAPI(
    title="Predictor Orchestrator",
    description="Orquestador de predicciones ML",
    version="1.0.0"
)

# Clientes globales
ml_orchestrator = MLOrchestrator(
    settings.ML_COLOR_URL,
    settings.ML_TEXTURE_URL,
    settings.ML_SIZE_URL,
    settings.ML_TIMEOUT
)
tb_client = ThingsBoardClient(settings.THINGSBOARD_URL)
ws_emitter = WebSocketEmitter(settings.WEBSOCKET_URL)

# Modelos Pydantic
class PredictBatchRequest(BaseModel):
    color_images: List[str] = Field(default=[], description="Lista de rutas a imágenes para análisis de color")
    texture_images: List[str] = Field(default=[], description="Lista de rutas a imágenes para análisis de textura")
    size_images: List[str] = Field(default=[], description="Lista de rutas a imágenes para análisis de tamaño")

class PredictBatchResponse(BaseModel):
    total_processed: int
    color_processed: int
    texture_processed: int
    size_processed: int
    success: bool
    predictions: dict
    timestamp: float

@app.get("/")
async def root():
    return {
        "service": "Predictor Orchestrator",
        "status": "running",
        "ml_services": {
            "color": settings.ML_COLOR_URL,
            "texture": settings.ML_TEXTURE_URL,
            "size": settings.ML_SIZE_URL
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/predict-batch", response_model=PredictBatchResponse)
async def predict_batch(request: PredictBatchRequest):
    """
    Procesa un lote de imágenes con los 3 modelos ML.
    Envía resultados a ThingsBoard y emite eventos al dashboard.
    """
    logger.info("=" * 60)
    logger.info(f"📦 Processing batch of {len(request.images)} images")
    logger.info("=" * 60)
    
    start_time = time.time()
    predictions = []
    
    # Procesar cada imagen
    for image_path in request.images:
        try:
            prediction = await ml_orchestrator.predict_all(image_path)
            predictions.append(prediction)
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            predictions.append({
                "image": image_path,
                "error": str(e),
                "success": {"color": False, "texture": False, "size": False}
            })
    
    # Preparar datos para ThingsBoard
    tb_data = []
    for pred in predictions:
        # Solo enviar predicciones exitosas
        if pred.get("color") and pred["success"]["color"]:
            tb_record = {
                "proceso": "prediccion",
                "image": pred["image"],
                "timestamp": time.time(),
                **pred["color"]  # Incluir todos los campos de color
            }
            tb_data.append(tb_record)
    
    # Enviar a ThingsBoard
    if tb_data:
        success = await tb_client.send_predictions(
            settings.TB_PREDICTIONS_TOKEN,
            tb_data
        )
    else:
        success = False
        logger.warning("No valid predictions to send to ThingsBoard")
    
    # Emitir evento al dashboard
    await ws_emitter.emit_event("predictions", {
        "total": len(predictions),
        "timestamp": time.time(),
        "predictions": predictions[:5]  # Solo primeras 5 para no saturar
    })
    
    elapsed = time.time() - start_time
    logger.info(f"✅ Batch processed in {elapsed:.2f}s")
    logger.info("=" * 60)
    
    return PredictBatchResponse(
        total_images=len(request.images),
        total_processed=len([p for p in predictions if p.get("success", {}).get("color")]),
        success=success,
        predictions=predictions,
        timestamp=time.time()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)