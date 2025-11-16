import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ORCHESTRATOR_URL = os.getenv('ORCHESTRATOR_URL', 'http://predictor-orchestrator:8000')
    
    # Rutas a los diferentes datasets
    DATASET_COLOR_PATH = os.getenv('DATASET_COLOR_PATH', '/datasets/color')
    DATASET_TEXTURE_PATH = os.getenv('DATASET_TEXTURE_PATH', '/datasets/texture')
    DATASET_SIZE_PATH = os.getenv('DATASET_SIZE_PATH', '/datasets/size')
    
    SCHEDULE_INTERVAL = int(os.getenv('SCHEDULE_INTERVAL', '60'))  # segundos
    NUM_IMAGES = int(os.getenv('NUM_IMAGES', '20'))

settings = Settings()