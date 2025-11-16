import tensorflow as tf
import numpy as np
import logging
import os
import cv2
from typing import Dict

logger = logging.getLogger(__name__)

# === Función detect_and_crop integrada === #
def detect_and_crop(img_path):
    try:
        img = cv2.imread(img_path)
        if img is None:
            return None

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)

        mask_L = cv2.inRange(L, 140, 255)
        mask_A = cv2.inRange(A, 110, 150)
        mask_B = cv2.inRange(B, 120, 170)

        mask = cv2.bitwise_and(mask_L, cv2.bitwise_and(mask_A, mask_B))

        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)
        crop = img_rgb[y:y+h, x:x+w]

        return crop

    except Exception as e:
        logger.error(f"Error in detect_and_crop: {e}")
        return None



# === Clase de producción === #
class TexturePredictor:
    def __init__(self, model_path: str, img_size: int = 224):
        """
        Inicializa el predictor de textura de pan.
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
        Predice la textura del pan usando recorte real detect_and_crop().
        """
        try:
            # === Recorte usando tu lógica === #
            crop = detect_and_crop(image_path)

            if crop is None:
                logger.warning(f"No bread detected in image: {image_path}")
                return {
                    "image": os.path.basename(image_path),
                    "texture_score": None,
                    "message": "No se pudo detectar pan en la imagen"
                }

            # === Resize y normalización === #
            crop = cv2.resize(crop, (self.img_size, self.img_size))
            crop = crop.astype("float32") / 255.0
            crop = np.expand_dims(crop, axis=0)

            # === Predicción === #
            pred = self.model.predict(crop, verbose=0)[0][0]
            texture_score = float(pred)

            logger.info(
                f"Texture prediction for {os.path.basename(image_path)}: score={texture_score:.4f}"
            )

            return {
                "image": os.path.basename(image_path),
                "texture_score": round(texture_score, 2)
            }

        except Exception as e:
            logger.error(f"Error predicting texture for {image_path}: {e}")
            raise
