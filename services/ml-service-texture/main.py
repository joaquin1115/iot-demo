from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import os
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Service - Texture", version="1.0.0")

class PredictionRequest(BaseModel):
    image_path: str

class PredictionResponse(BaseModel):
    image: str
    prediction: int
    estado: str
    confidence: float
    texture_score: float

@app.get("/")
async def root():
    return {
        "service": "ML Service - Texture",
        "status": "running (placeholder)",
        "note": "This is a placeholder. Implement your texture model here."
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Placeholder: retorna predicción simulada.
    TODO: Implementar modelo real de textura.
    """
    logger.info(f"Texture prediction (simulated) for {request.image_path}")
    
    # Simulación
    prediction = random.choice([0, 1])
    confidence = random.uniform(0.7, 0.95)
    
    return PredictionResponse(
        image=os.path.basename(request.image_path),
        prediction=prediction,
        estado="Buena textura" if prediction == 0 else "Mala textura",
        confidence=confidence,
        texture_score=random.uniform(0.5, 1.0)
    )
