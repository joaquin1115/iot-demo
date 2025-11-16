import tensorflow as tf
import numpy as np
import cv2
import json
import pickle
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SizePredictor:
    def __init__(self, model_path: str, config_path: str, scaler_path: Optional[str] = None):
        """
        Inicializa el predictor de tamaño de pan.
        
        Args:
            model_path: Ruta al archivo modelo_medidor.h5
            config_path: Ruta al archivo config.json
            scaler_path: Ruta al archivo output_scaler.pkl (opcional)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config not found: {config_path}")
        
        logger.info(f"Loading size model from {model_path}")
        
        try:
            # Cargar modelo
            self.model = tf.keras.models.load_model(model_path, compile=False)
            logger.info("✅ Size model loaded successfully")
            
            # Cargar configuración
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"✅ Config loaded: {config_path}")
            
            # Cargar scaler (opcional)
            self.scaler = None
            if scaler_path and os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("✅ Scaler loaded")
            else:
                logger.warning("⚠️  Scaler not found, predictions will be in normalized scale")
            
        except Exception as e:
            logger.error(f"Failed to load size model: {e}")
            raise
    
    def predict(self, image_path: str) -> Dict:
        """
        Predice las dimensiones del pan.
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con las dimensiones predichas
        """
        try:
            # Leer imagen con OpenCV
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convertir BGR a RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Aplicar crop según configuración
            crop_percent = self.config['preprocessing']['crop_left_percent']
            h, w = img.shape[:2]
            img = img[:, :int(w * crop_percent)]
            
            # Resize según configuración del modelo
            img_size = tuple(self.config['model']['img_size'])
            img = cv2.resize(img, img_size)
            
            # Normalizar [0, 255] -> [0, 1]
            img = img / 255.0
            
            # Agregar dimensión batch
            img = np.expand_dims(img, axis=0)
            
            # Predecir
            pred = self.model.predict(img, verbose=0)[0]
            
            # Desnormalizar si hay scaler
            if self.scaler is not None:
                pred = self.scaler.inverse_transform(pred.reshape(1, -1))[0]
            
            # Extraer dimensiones
            width_mm = float(pred[0])
            height_mm = float(pred[1])
            
            # Calcular volumen aproximado (cilindro)
            # V = π * r² * h, donde r = width/2
            radius_mm = width_mm / 2
            volume_ml = (np.pi * (radius_mm ** 2) * height_mm) / 1000  # mm³ a ml
            
            # Clasificar tamaño (ajustar umbrales según tu modelo)
            # Ejemplo: pan correcto entre 80-120mm de ancho
            is_correct_size = 80 <= width_mm <= 120
            prediction = 0 if is_correct_size else 1
            
            logger.info(f"Size prediction for {os.path.basename(image_path)}: "
                       f"width={width_mm:.2f}mm, height={height_mm:.2f}mm")
            
            return {
                "image": os.path.basename(image_path),
                "prediction": prediction,
                "width_mm": round(width_mm, 2),
                "height_mm": round(height_mm, 2),
                "volume_ml": round(volume_ml, 2),
                "estado": "Tamaño correcto" if prediction == 0 else "Tamaño incorrecto",
                "confidence": 0.85  # Puedes calcular confianza basada en distancia a rangos
            }
            
        except Exception as e:
            logger.error(f"Error predicting size for {image_path}: {e}")
            raise
