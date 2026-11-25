"""Detección y comparación de rostros en vivo usando face_recognition."""

from __future__ import annotations

import cv2
import numpy as np
import face_recognition

import config
from . import almacenamiento


class Reconocedor:
    """Mantiene en memoria las firmas de las personas autorizadas."""

    def __init__(self) -> None:
        self.nombres: list[str] = []
        self.encodings: list[np.ndarray] = []
        self._modelo = config.MODELO_DETECCION
        self.recargar()

    def recargar(self) -> None:
        """Vuelve a leer los encodings desde disco (tras un alta o baja)."""
        datos = almacenamiento.cargar_datos()
        self.nombres = list(datos["nombres"])
        self.encodings = list(datos["encodings"])

    def _detectar(self, rgb_pequeno: np.ndarray) -> list[tuple[int, int, int, int]]:
        """Detecta rostros; si el modelo configurado falla, usa HOG."""
        try:
            return face_recognition.face_locations(
                rgb_pequeno,
                number_of_times_to_upsample=0,
                model=self._modelo,
            )
        except Exception as exc:  # pragma: no cover - depende del entorno
            print(f"[reconocedor] Modelo {self._modelo!r} no disponible ({exc}); usando HOG")
            self._modelo = "hog"
            return face_recognition.face_locations(
                rgb_pequeno, number_of_times_to_upsample=1, model="hog"
            )

    def procesar_frame(self, frame_bgr: np.ndarray, dibujar: bool = True):
        """Detecta rostros y los compara con los autorizados.

        Devuelve (frame_con_anotaciones, estados), donde estados es una lista
        de dictos: {'nombre', 'autorizado', 'distancia'}.
        Los rostros se marcan incluso cuando no hay nadie dado de alta.
        """
        salida = frame_bgr.copy()
        estados: list[dict] = []

        pequeno = cv2.resize(
            frame_bgr,
            (0, 0),
            fx=config.ESCALA_DETECCION,
            fy=config.ESCALA_DETECCION,
        )
        rgb_pequeno = cv2.cvtColor(pequeno, cv2.COLOR_BGR2RGB)
        ubicaciones_pequenas = self._detectar(rgb_pequeno)
        if not ubicaciones_pequenas:
            return salida, estados

        escala = 1.0 / config.ESCALA_DETECCION
        ubicaciones = [
            tuple(int(v * escala) for v in ubicacion)
            for ubicacion in ubicaciones_pequenas
        ]

        # Calcula la firma sobre la imagen completa para no perder precisión
        rgb_completo = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        for ubicacion in ubicaciones:
            codificaciones = face_recognition.face_encodings(
                rgb_completo, [ubicacion]
            )
            if not codificaciones:
                continue
            codigo = codificaciones[0]

            autorizado = False
            nombre = "Desconocido"
            distancia = None
            if self.encodings:
                distancias = face_recognition.face_distance(self.encodings, codigo)
                indice = int(np.argmin(distancias))
                distancia = float(distancias[indice])
                autorizado = distancia <= config.TOLERANCIA
                if autorizado:
                    nombre = self.nombres[indice]

            estados.append(
                {
                    "nombre": nombre,
                    "autorizado": autorizado,
                    "distancia": distancia,
                }
            )

            if dibujar:
                top, right, bottom, left = ubicacion
                color = (0, 190, 0) if autorizado else (0, 0, 220)
                cv2.rectangle(salida, (left, top), (right, bottom), color, 2)
                if autorizado:
                    texto = f"{nombre} ({distancia:.2f})"
                else:
                    texto = "NO AUTORIZADO"
                alto_texto = 26
                cv2.rectangle(
                    salida,
                    (left, bottom - alto_texto),
                    (right, bottom),
                    color,
                    cv2.FILLED,
                )
                cv2.putText(
                    salida,
                    texto,
                    (left + 5, bottom - 7),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
        return salida, estados
