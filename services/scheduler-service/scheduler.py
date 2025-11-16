import os
import random
import logging
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import requests
from config import settings

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_random_images(dataset_path: str, num_images: int) -> list:
    """
    Selecciona aleatoriamente N imágenes del dataset.
    
    Args:
        dataset_path: Ruta al directorio con imágenes
        num_images: Número de imágenes a seleccionar
    
    Returns:
        Lista de rutas absolutas a las imágenes
    """
    try:
        dataset_dir = Path(dataset_path)
        
        if not dataset_dir.exists():
            logger.error(f"Dataset path not found: {dataset_path}")
            return []
        
        # Obtener todas las imágenes
        image_extensions = ['.jpg', '.jpeg', '.png']
        all_images = [
            str(img.absolute()) for img in dataset_dir.iterdir()
            if img.suffix.lower() in image_extensions and img.is_file()
        ]
        
        if not all_images:
            logger.warning(f"No images found in {dataset_path}")
            return []
        
        if len(all_images) < num_images:
            logger.warning(
                f"Only {len(all_images)} images available, "
                f"requested {num_images}. Using all available."
            )
            return all_images
        
        # Seleccionar aleatoriamente
        selected = random.sample(all_images, num_images)
        logger.info(f"✅ Selected {len(selected)} random images")
        return selected
        
    except Exception as e:
        logger.error(f"❌ Error selecting images: {e}", exc_info=True)
        return []


def trigger_predictions():
    """
    Tarea que se ejecuta cada minuto.
    Selecciona imágenes aleatorias de cada dataset y dispara el orquestador.
    """
    logger.info("")
    logger.info("=" * 70)
    logger.info("⏰ SCHEDULER TASK TRIGGERED")
    logger.info("=" * 70)
    
    try:
        # Seleccionar imágenes de cada dataset
        logger.info(f"📁 Scanning datasets...")
        
        color_images = get_random_images(settings.DATASET_COLOR_PATH, settings.NUM_IMAGES)
        texture_images = get_random_images(settings.DATASET_TEXTURE_PATH, settings.NUM_IMAGES)
        size_images = get_random_images(settings.DATASET_SIZE_PATH, settings.NUM_IMAGES)
        
        # Verificar que al menos tenemos imágenes de color
        if not color_images:
            logger.warning("⚠️  No color images found, skipping task")
            return
        
        logger.info(f"🖼️  Selected images:")
        logger.info(f"   Color: {len(color_images)} images")
        logger.info(f"   Texture: {len(texture_images)} images")
        logger.info(f"   Size: {len(size_images)} images")
        
        # Mostrar primeras 3 imágenes de color
        for i, img in enumerate(color_images[:3], 1):
            logger.info(f"     {i}. {Path(img).name}")
        if len(color_images) > 3:
            logger.info(f"     ... and {len(color_images) - 3} more")
        
        # Preparar payload con las 3 listas de imágenes
        payload = {
            "color_images": color_images,
            "texture_images": texture_images,
            "size_images": size_images
        }
        
        # Llamar al orchestrator
        url = f"{settings.ORCHESTRATOR_URL}/predict-batch"
        logger.info(f"📡 Calling orchestrator: {url}")
        
        response = requests.post(
            url,
            json=payload,
            timeout=300  # 5 minutos
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Log resultado
        logger.info("")
        logger.info("✅ PREDICTIONS COMPLETED SUCCESSFULLY")
        logger.info(f"   📊 Total images processed: {result.get('total_processed', 0)}")
        logger.info(f"   ✔️  Color: {result.get('color_processed', 0)}")
        logger.info(f"   ✔️  Texture: {result.get('texture_processed', 0)}")
        logger.info(f"   ✔️  Size: {result.get('size_processed', 0)}")
        logger.info(f"   📤 Sent to ThingsBoard: {result.get('success', False)}")
        
    except requests.exceptions.Timeout:
        logger.error("❌ TIMEOUT calling orchestrator (>5min)")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ CONNECTION ERROR: {e}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP ERROR: {e.response.status_code}")
        logger.error(f"   Response: {e.response.text[:200]}")
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: {e}", exc_info=True)
    
    logger.info("=" * 70)
    logger.info("")


def main():
    """
    Inicializa el scheduler y mantiene el proceso corriendo.
    """
    logger.info("=" * 70)
    logger.info("🚀 SCHEDULER SERVICE STARTING")
    logger.info("=" * 70)
    logger.info(f"⚙️  Configuration:")
    logger.info(f"   📍 Orchestrator URL: {settings.ORCHESTRATOR_URL}")
    logger.info(f"   📁 Color dataset: {settings.DATASET_COLOR_PATH}")
    logger.info(f"   📁 Texture dataset: {settings.DATASET_TEXTURE_PATH}")
    logger.info(f"   📁 Size dataset: {settings.DATASET_SIZE_PATH}")
    logger.info(f"   ⏱️  Interval: {settings.SCHEDULE_INTERVAL} seconds")
    logger.info(f"   🖼️  Images per batch: {settings.NUM_IMAGES}")
    logger.info("=" * 70)
    logger.info("")
    
    # Verificar que al menos el dataset de color existe
    if not Path(settings.DATASET_COLOR_PATH).exists():
        logger.error(f"❌ Color dataset path does not exist: {settings.DATASET_COLOR_PATH}")
        logger.error("   Please mount the dataset volume correctly")
        return
    
    logger.info(f"✅ Color dataset found: {settings.DATASET_COLOR_PATH}")
    
    # Verificar datasets opcionales
    if not Path(settings.DATASET_TEXTURE_PATH).exists():
        logger.warning(f"⚠️  Texture dataset not found: {settings.DATASET_TEXTURE_PATH}")
        logger.warning("   Texture predictions will be skipped")
    else:
        logger.info(f"✅ Texture dataset found: {settings.DATASET_TEXTURE_PATH}")
    
    if not Path(settings.DATASET_SIZE_PATH).exists():
        logger.warning(f"⚠️  Size dataset not found: {settings.DATASET_SIZE_PATH}")
        logger.warning("   Size predictions will be skipped")
    else:
        logger.info(f"✅ Size dataset found: {settings.DATASET_SIZE_PATH}")
    
    logger.info("")
    
    # Crear scheduler
    scheduler = BlockingScheduler()
    
    # Agregar job
    scheduler.add_job(
        func=trigger_predictions,
        trigger=IntervalTrigger(seconds=settings.SCHEDULE_INTERVAL),
        id='prediction_task',
        name='Trigger ML predictions',
        replace_existing=True
    )
    
    logger.info("✅ Scheduler configured successfully")
    logger.info(f"⏰ First execution will be in {settings.SCHEDULE_INTERVAL} seconds")
    logger.info("   Press Ctrl+C to stop")
    logger.info("")
    
    # Opcional: ejecutar inmediatamente la primera vez
    # Descomentar si quieres que corra al inicio
    # logger.info("🏃 Running first task immediately...")
    # trigger_predictions()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("")
        logger.info("🛑 Scheduler stopped by user")


if __name__ == '__main__':
    main()