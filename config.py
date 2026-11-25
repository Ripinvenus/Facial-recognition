"""Configuración central del sistema de control de acceso biométrico.

Todas las rutas son relativas a la carpeta del proyecto, de forma que la
aplicación funcione igual en Windows, Linux o macOS sin cambiar nada.
"""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas (relativas al proyecto)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PERSONAS_DIR = DATA_DIR / "personas"
ENCODINGS_FILE = DATA_DIR / "encodings.pickle"
REGISTRO_FILE = DATA_DIR / "accesos.log"

# ---------------------------------------------------------------------------
# Cámara y reconocimiento
# ---------------------------------------------------------------------------
CAMARA_INDEX = 0          # Si falla, se busca automáticamente otra cámara
ANCHO_CAMARA = 640
ALTO_CAMARA = 480

TOLERANCIA = 0.55         # Menor = más estricto. Recomendado: 0.5 - 0.6
ESCALA_DETECCION = 0.25   # Reduce el frame para detectar más rápido
CADA_N_FRAMES = 3         # Se analiza 1 de cada N frames (más fluidez)
N_FOTOS_ALTA = 5          # Fotos capturadas al dar de alta una persona

# "cnn" detecta mejor rostros de lado o con poca luz (recomendado).
# "hog" es más rápido pero falla con ángulos y sombras.
MODELO_DETECCION = "cnn"

# ---------------------------------------------------------------------------
# Seguridad del panel de gestión
# ---------------------------------------------------------------------------
# NOTA: la contraseña por defecto es "123" (valor de prueba).
# En un entorno real, cambia PASSWORD_SALT y la contraseña aquí.
PASSWORD_SALT = "biometria-proyecto-salt"
_PASSWORD_HASH = hashlib.sha256(
    (PASSWORD_SALT + "123").encode("utf-8")
).hexdigest()


def verificar_password(valor: str) -> bool:
    """Compara la contraseña introducida con el hash guardado."""
    candidato = hashlib.sha256(
        (PASSWORD_SALT + str(valor)).encode("utf-8")
    ).hexdigest()
    return hmac.compare_digest(candidato, _PASSWORD_HASH)
