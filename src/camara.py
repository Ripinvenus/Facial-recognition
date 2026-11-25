"""Captura de video en un hilo para no bloquear la interfaz gráfica."""

from __future__ import annotations

import threading
import time

import cv2
import numpy as np

import config


def detectar_indice(maximo: int = 4, desde: int = 0) -> int | None:
    """Devuelve el primer índice de cámara que funciona, o None."""
    for indice in range(desde, desde + maximo):
        captura = cv2.VideoCapture(indice)
        try:
            if captura.isOpened():
                for _ in range(3):
                    ok, _ = captura.read()
                    if ok:
                        return indice
        finally:
            captura.release()
    return None


class Camara:
    """Cámara simple con lectura del último frame desde cualquier hilo."""

    def __init__(
        self,
        indice: int | None = None,
        ancho: int = config.ANCHO_CAMARA,
        alto: int = config.ALTO_CAMARA,
    ) -> None:
        self.indice = config.CAMARA_INDEX if indice is None else indice
        self.ancho = ancho
        self.alto = alto
        self._captura: cv2.VideoCapture | None = None
        self._frame: np.ndarray | None = None
        self._lock = threading.Lock()
        self._hilo: threading.Thread | None = None
        self.activa = False

    def iniciar(self, intentos: int = 5) -> None:
        if self.activa:
            return
        backend = cv2.CAP_DSHOW if _es_windows() else 0
        ultimo_error = f"No se pudo abrir la cámara índice {self.indice}"
        # Al liberar y volver a abrir la cámara, algunos sistemas tardan un
        # poco en liberar el dispositivo: reintentamos antes de rendirnos.
        for _ in range(intentos):
            captura = cv2.VideoCapture(self.indice, backend)
            if captura.isOpened():
                ok, primer_frame = captura.read()
                if ok and primer_frame is not None:
                    captura.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho)
                    captura.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto)
                    self._captura = captura
                    with self._lock:
                        self._frame = primer_frame
                    self.activa = True
                    self._hilo = threading.Thread(target=self._bucle, daemon=True)
                    self._hilo.start()
                    return
                ultimo_error = "La cámara se abrió pero no devolvió imagen"
            captura.release()
            time.sleep(0.3)
        raise RuntimeError(ultimo_error)

    def _bucle(self) -> None:
        while self.activa and self._captura is not None:
            ok, frame = self._captura.read()
            if ok:
                with self._lock:
                    self._frame = frame
            else:
                time.sleep(0.05)
            time.sleep(0.02)

    def leer(self) -> np.ndarray | None:
        """Devuelve una copia del último frame (o None si aún no hay)."""
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    def detener(self) -> None:
        self.activa = False
        if self._hilo is not None:
            self._hilo.join(timeout=2)
            self._hilo = None
        if self._captura is not None:
            self._captura.release()
            self._captura = None
        with self._lock:
            self._frame = None


def _es_windows() -> bool:
    import sys

    return sys.platform.startswith("win")
