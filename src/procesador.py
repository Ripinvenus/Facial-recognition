"""Analiza los frames de la cámara en segundo plano y registra los accesos."""

from __future__ import annotations

import threading
import time

import numpy as np

import config
from . import registro
from .camara import Camara
from .reconocedor import Reconocedor


class ProcesadorEnVivo:
    """Mantiene el último frame anotado y su resultado de reconocimiento."""

    def __init__(self, camara: Camara, reconocedor: Reconocedor) -> None:
        self.camara = camara
        self.reconocedor = reconocedor
        self.activo = False
        self._hilo: threading.Thread | None = None
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._estados: list[dict] = []
        self._contador = 0
        self._ultimo_estado: str | None = None
        self._ultimo_registro = 0.0

    def iniciar(self) -> None:
        if self.activo:
            return
        self.activo = True
        self._hilo = threading.Thread(target=self._bucle, daemon=True)
        self._hilo.start()

    def _bucle(self) -> None:
        while self.activo:
            frame = self.camara.leer()
            if frame is None:
                time.sleep(0.05)
                continue

            self._contador += 1
            if self._contador % config.CADA_N_FRAMES == 0 or self._frame is None:
                anotado, estados = self.reconocedor.procesar_frame(frame)
                with self._lock:
                    self._frame = anotado
                    self._estados = estados
                self._registrar(estados)
            time.sleep(0.02)

    def _registrar(self, estados: list[dict]) -> None:
        """Escribe en el log solo cambios de estado (con anti-repetición)."""
        autorizados = [e for e in estados if e["autorizado"]]
        if autorizados:
            estado = "AUTORIZADO"
            nombre = autorizados[0]["nombre"]
            distancia = autorizados[0]["distancia"]
        elif estados:
            estado = "NO AUTORIZADO"
            nombre = ""
            distancia = estados[0]["distancia"]
        else:
            return  # sin rostro: no se registra

        ahora = time.time()
        if estado == self._ultimo_estado and ahora - self._ultimo_registro < 3:
            return
        registro.registrar(estado, nombre, distancia)
        self._ultimo_estado = estado
        self._ultimo_registro = ahora

    def obtener(self):
        """Devuelve (frame, estados) para dibujar en la interfaz."""
        with self._lock:
            frame = self._frame
            estados = list(self._estados)
        if frame is None:
            return None, estados
        return frame.copy(), estados

    def detener(self) -> None:
        self.activo = False
        if self._hilo is not None:
            self._hilo.join(timeout=3)
            self._hilo = None
