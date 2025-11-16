from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import os
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Service - Size", version="1.0.0")

class PredictionRequest(BaseModel):
    image_path: str

class PredictionResponse(BaseModel):
    image: str
    prediction: int
    estado: str
    confidence: float
    size_cm: float
    volume_ml: float

@app.get("/")
async def root():
    return {
        "service": "ML Service - Size",
        "status": "running (placeholder)",
        "note": "This is a placeholder. Implement your size model here."
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Placeholder: retorna predicción simulada.
    TODO: Implementar modelo real de tamaño.
    """
    logger.info(f"Size prediction (simulated) for {request.image_path}")
    
    # Simulación
    prediction = random.choice([0, 1])
    confidence = random.uniform(0.7, 0.95)
    size_cm = random.uniform(8.0, 15.0)
    
    return PredictionResponse(
        image=os.path.basename(request.image_path),
        prediction=prediction,
        estado="Tamaño correcto" if prediction == 0 else "Tamaño incorrecto",
        confidence=confidence,
        size_cm=round(size_cm, 2),
        volume_ml=round(size_cm ** 3 * 0.5, 2)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)