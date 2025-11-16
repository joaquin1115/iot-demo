from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
import logging
import time
from config import settings
from services.ml_client import MLOrchestrator
from services.thingsboard import ThingsBoardClient
from services.websocket_client import WebSocketEmitter

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
    Procesa lotes de imágenes con los 3 modelos ML.
    Cada modelo procesa su conjunto específico de imágenes.
    Envía resultados a ThingsBoard y emite eventos al dashboard.
    """
    total_images = len(request.color_images) + len(request.texture_images) + len(request.size_images)
    
    logger.info("=" * 60)
    logger.info(f"📦 Processing batch: {total_images} total images")
    logger.info(f"   Color: {len(request.color_images)} images")
    logger.info(f"   Texture: {len(request.texture_images)} images")
    logger.info(f"   Size: {len(request.size_images)} images")
    logger.info("=" * 60)
    
    start_time = time.time()
    predictions = {
        "color": [],
        "texture": [],
        "size": []
    }
    
    # Procesar imágenes de COLOR
    if request.color_images:
        logger.info("🎨 Processing COLOR predictions...")
        for image_path in request.color_images:
            try:
                result = await ml_orchestrator.color_client.predict(image_path)
                if result:
                    predictions["color"].append(result)
            except Exception as e:
                logger.error(f"Error processing color {image_path}: {e}")
    
    # Procesar imágenes de TEXTURE
    if request.texture_images:
        logger.info("🔲 Processing TEXTURE predictions...")
        for image_path in request.texture_images:
            try:
                result = await ml_orchestrator.texture_client.predict(image_path)
                if result:
                    predictions["texture"].append(result)
            except Exception as e:
                logger.error(f"Error processing texture {image_path}: {e}")
    
    # Procesar imágenes de SIZE
    if request.size_images:
        logger.info("📏 Processing SIZE predictions...")
        for image_path in request.size_images:
            try:
                result = await ml_orchestrator.size_client.predict(image_path)
                if result:
                    predictions["size"].append(result)
            except Exception as e:
                logger.error(f"Error processing size {image_path}: {e}")
    
    # Preparar datos para ThingsBoard (solo predicciones de color por ahora)
    tb_data = []
    for pred in predictions["color"]:
        tb_record = {
            "proceso": "prediccion_color",
            "timestamp": time.time(),
            **pred  # Incluir todos los campos de la predicción
        }
        tb_data.append(tb_record)
    
    # Enviar a ThingsBoard
    success = False
    if tb_data:
        success = await tb_client.send_predictions(
            settings.TB_PREDICTIONS_TOKEN,
            tb_data
        )
    else:
        logger.warning("No valid predictions to send to ThingsBoard")
    
    # Emitir evento al dashboard
    await ws_emitter.emit_event("predictions", {
        "color_count": len(predictions["color"]),
        "texture_count": len(predictions["texture"]),
        "size_count": len(predictions["size"]),
        "timestamp": time.time(),
        "sample_predictions": {
            "color": predictions["color"][:3] if predictions["color"] else [],
            "texture": predictions["texture"][:3] if predictions["texture"] else [],
            "size": predictions["size"][:3] if predictions["size"] else []
        }
    })
    
    elapsed = time.time() - start_time
    total_processed = len(predictions["color"]) + len(predictions["texture"]) + len(predictions["size"])
    
    logger.info(f"✅ Batch processed in {elapsed:.2f}s")
    logger.info(f"   Total: {total_processed} predictions")
    logger.info("=" * 60)
    
    return PredictBatchResponse(
        total_processed=total_processed,
        color_processed=len(predictions["color"]),
        texture_processed=len(predictions["texture"]),
        size_processed=len(predictions["size"]),
        success=success,
        predictions=predictions,
        timestamp=time.time()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)