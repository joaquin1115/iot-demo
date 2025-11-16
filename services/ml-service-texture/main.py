from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import logging
import os
import sys

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from predictor import TexturePredictor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
MODEL_PATH = os.getenv("MODEL_PATH", "/models/modelo_texture.h5")
IMG_SIZE = int(os.getenv("IMG_SIZE", "224"))

# Crear app
app = FastAPI(
    title="ML Service - Texture",
    description="Servicio de predicción de textura de pan",
    version="1.0.0"
)

# Cargar modelo al inicio
try:
    predictor = TexturePredictor(MODEL_PATH, IMG_SIZE)
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    predictor = None

# Modelos Pydantic
class PredictionRequest(BaseModel):
    image_path: str = Field(..., description="Ruta absoluta a la imagen")

class PredictionResponse(BaseModel):
    image: str
    texture_score: float

@app.get("/")
async def root():
    return {
        "service": "ML Service - Texture",
        "status": "running" if predictor else "model not loaded",
        "model_path": MODEL_PATH,
        "img_size": IMG_SIZE
    }

@app.get("/health")
async def health():
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    return {"status": "healthy", "model": "loaded"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predice la textura del pan.
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    if not os.path.exists(request.image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image not found: {request.image_path}"
        )
    
    try:
        result = predictor.predict(request.image_path)
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)