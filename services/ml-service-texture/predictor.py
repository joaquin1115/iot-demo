import tensorflow as tf
import numpy as np
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

class TexturePredictor:
    def __init__(self, model_path: str, img_size: int = 224):
        """
        Inicializa el predictor de textura de pan.
        
        Args:
            model_path: Ruta al archivo modelo_texture.h5
            img_size: Tamaño de la imagen (default: 128x128)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.img_size = img_size
        
        logger.info(f"Loading texture model from {model_path}")
        
        try:
            self.model = tf.keras.models.load_model(model_path, compile=False)
            logger.info("✅ Texture model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load texture model: {e}")
            raise
    
    def predict(self, image_path: str) -> Dict:
        """
        Predice la textura del pan.
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con la predicción de textura
        """
        try:
            # Leer imagen usando TensorFlow
            img = tf.io.read_file(image_path)
            
            # Decodificar (soporta JPG, PNG)
            try:
                img = tf.image.decode_jpeg(img, channels=3)
            except:
                img = tf.image.decode_png(img, channels=3)
            
            # Resize
            img = tf.image.resize(img, (self.img_size, self.img_size))
            
            # Normalizar [0, 255] -> [0, 1]
            img = img / 255.0
            
            # Agregar dimensión batch
            img = tf.expand_dims(img, 0)
            
            # Predecir
            pred = self.model.predict(img, verbose=0)[0][0]
            
            # Convertir a tipos Python nativos
            texture_score = float(pred)
            
            logger.info(f"Texture prediction for {os.path.basename(image_path)}: "
                       f"score={texture_score:.4f}")
            
            return {
                "image": os.path.basename(image_path),
                "texture_score": texture_score
            }
            
        except Exception as e:
            logger.error(f"Error predicting texture for {image_path}: {e}")
            raise
