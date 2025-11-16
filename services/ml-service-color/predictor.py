import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer
import logging
from typing import Dict, Tuple
import os

logger = logging.getLogger(__name__)


class ThresholdLayer(Layer):
    def __init__(self, threshold=0.8, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

    def call(self, inputs):
        return tf.cast(inputs >= self.threshold, tf.float32)

    def get_config(self):
        config = super().get_config()
        config.update({"threshold": self.threshold})
        return config


class ColorPredictor:
    def __init__(self, model_path: str):
        """
        Inicializa el predictor de color de pan.

        Args:
            model_path: Ruta al archivo modelo_pan.h5
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        logger.info(f"Loading model from {model_path}")
        self.model = load_model(
            model_path, custom_objects={"ThresholdLayer": ThresholdLayer}
        )
        logger.info("✅ Model loaded successfully")

    def dividir_en_9(self, img: np.ndarray) -> list:
        """
        Divide la imagen en 9 partes (grid 3x3).
        """
        h, w, _ = img.shape
        h_step = h // 3
        w_step = w // 3

        partes = []
        for i in range(3):
            for j in range(3):
                crop = img[i * h_step : (i + 1) * h_step, j * w_step : (j + 1) * w_step]
                partes.append(crop)
        return partes

    def color_promedio(self, img: np.ndarray) -> np.ndarray:
        """
        Calcula el color promedio de una imagen.
        Retorna BGR invertido a RGB.
        """
        avg = img.mean(axis=(0, 1))
        return avg[::-1]  # BGR -> RGB

    def extract_features(self, img: np.ndarray) -> np.ndarray:
        """
        Extrae características de color de la imagen.
        Divide en 9 partes y calcula color promedio de cada una.

        Returns:
            Array de 27 features (9 partes x 3 canales RGB)
        """
        h, w, _ = img.shape
        h_step = h // 3
        w_step = w // 3

        features = []

        for i in range(3):
            for j in range(3):
                crop = img[i * h_step : (i + 1) * h_step, j * w_step : (j + 1) * w_step]
                avg = crop.mean(axis=(0, 1))
                avg = avg[::-1]  # BGR -> RGB
                features.extend(avg.tolist())

        return np.array(features).reshape(1, -1)

    def extract_color_analysis(self, img: np.ndarray, estado: int) -> Dict:
        """
        Extrae análisis detallado de colores de la imagen.

        Args:
            img: Imagen en formato RGB
            estado: 0 = Normal, 1 = Malo (quemado)

        Returns:
            Diccionario con análisis de colores
        """
        partes = self.dividir_en_9(img)
        colores = [self.color_promedio(p) for p in partes]
        colores_arr = np.array(colores)

        # Calcular intensidades
        intensidades = colores_arr.mean(axis=1)

        # Color más oscuro
        idx_oscuro = np.argmin(intensidades)
        color_oscuro = colores_arr[idx_oscuro]

        # Color más claro
        idx_claro = np.argmax(intensidades)
        color_claro = colores_arr[idx_claro]

        # Color promedio
        color_prom = colores_arr.mean(axis=0)

        estado_texto = "Normal" if estado == 0 else "Quemado"

        return {
            "color_oscuro_r": float(color_oscuro[0]),
            "color_oscuro_g": float(color_oscuro[1]),
            "color_oscuro_b": float(color_oscuro[2]),
            "color_promedio_r": float(color_prom[0]),
            "color_promedio_g": float(color_prom[1]),
            "color_promedio_b": float(color_prom[2]),
            "color_claro_r": float(color_claro[0]),
            "color_claro_g": float(color_claro[1]),
            "color_claro_b": float(color_claro[2]),
            "estado": estado_texto,
            "intensidad_promedio": float(intensidades.mean()),
        }

    def predict(self, image_path: str) -> Dict:
        """
        Predice si el pan está quemado o normal.

        Args:
            image_path: Ruta a la imagen

        Returns:
            Diccionario con predicción y análisis
        """
        try:
            # Leer imagen
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")

            # Convertir BGR a RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Extraer features
            X = self.extract_features(img_rgb)

            # Predecir
            salida_final = float(self.model.predict(X, verbose=0)[0][0])
            clase = int(salida_final)

            try:
                penultima = tf.keras.Model(
                    inputs=self.model.input, outputs=self.model.layers[-2].output
                )
                prob_real = float(penultima.predict(X, verbose=0)[0][0])
            except Exception:
                prob_real = salida_final

            # Análisis de colores
            color_analysis = self.extract_color_analysis(img_rgb, clase)

            logger.info(
                f"Prediction for {os.path.basename(image_path)}: "
                f"clase={clase}, prob_real={prob_real:.4f}, salida_final={salida_final}"
            )

            return {
                "image": os.path.basename(image_path),
                "prediction": clase,
                "probability": salida_final,
                "estado": "Quemado" if clase == 1 else "Normal",
                **color_analysis,
            }

        except Exception as e:
            logger.error(f"Error predicting {image_path}: {e}")
            raise
