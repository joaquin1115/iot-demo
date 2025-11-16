from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import logging
import os
import sys

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from predictor import SizePredictor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
MODEL_PATH = os.getenv("MODEL_PATH", "/models/modelo_size.h5")
CONFIG_PATH = os.getenv("CONFIG_PATH", "/models/config.json")
SCALER_PATH = os.getenv("SCALER_PATH", "/models/output_scaler.pkl")

# Crear app
app = FastAPI(
    title="ML Service - Size",
    description="Servicio de predicción de tamaño de pan",
    version="1.0.0"
)

# Cargar modelo al inicio
try:
    predictor = SizePredictor(MODEL_PATH, CONFIG_PATH, SCALER_PATH)
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    predictor = None

# Modelos Pydantic
class PredictionRequest(BaseModel):
    image_path: str = Field(..., description="Ruta absoluta a la imagen")

class PredictionResponse(BaseModel):
    image: str
    width_mm: float
    height_mm: float
    volume_ml: float
    estado: str
    confidence: float

@app.get("/")
async def root():
    return {
        "service": "ML Service - Size",
        "status": "running" if predictor else "model not loaded",
        "model_path": MODEL_PATH,
        "config_path": CONFIG_PATH,
        "scaler_path": SCALER_PATH
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
    Predice las dimensiones del pan.
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