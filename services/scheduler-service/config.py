import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ORCHESTRATOR_URL = os.getenv('ORCHESTRATOR_URL', 'http://predictor-orchestrator:8000')
    DATASET_PATH = os.getenv('DATASET_PATH', '/dataset/images')
    SCHEDULE_INTERVAL = int(os.getenv('SCHEDULE_INTERVAL', '60'))  # segundos
    NUM_IMAGES = int(os.getenv('NUM_IMAGES', '20'))

settings = Settings()

