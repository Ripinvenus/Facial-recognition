"""Pantalla principal: video en vivo con estado de autorización."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import cv2
from PIL import Image, ImageTk

import config
from .. import almacenamiento
from ..camara import Camara, detectar_indice
from ..procesador import ProcesadorEnVivo
from ..reconocedor import Reconocedor
from .panel_personas import PanelPersonas


class AppPrincipal(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Control de Acceso Biométrico")
        self.geometry("820x750")
        self.resizable(False, False)
        self.configure(padx=12, pady=12)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.camara: Camara | None = None
        self.procesador: ProcesadorEnVivo | None = None
        self.reconocedor = Reconocedor()
        self._imagen: ImageTk.PhotoImage | None = None

        self._construir_ui()
        self._iniciar_camara()
        self.after(80, self._actualizar)

    # ------------------------------------------------------------------
    # Interfaz
    # ------------------------------------------------------------------
    def _construir_ui(self) -> None:
        cabecera = ttk.Frame(self)
        cabecera.pack(fill="x", pady=(0, 8))
        ttk.Label(
            cabecera,
            text="Control de Acceso Biométrico",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")
        self.reloj = ttk.Label(cabecera, font=("Segoe UI", 10), foreground="#555555")
        self.reloj.pack(side="right")

        self.video = tk.Label(
            self,
            background="#1a1a1a",
            width=config.ANCHO_CAMARA,
            height=config.ALTO_CAMARA,
            relief="sunken",
            bd=2,
        )
        self.video.pack(pady=4)

        self.estado = tk.Label(
            self,
            text="INICIANDO...",
            font=("Segoe UI", 20, "bold"),
            background="#dddddd",
            foreground="#333333",
            pady=12,
        )
        self.estado.pack(fill="x", pady=(10, 2))

        self.detalle = ttk.Label(
            self, text="Acerca tu rostro a la cámara para verificar tu identidad."
        )
        self.detalle.pack()

        botones = ttk.Frame(self)
        botones.pack(fill="x", pady=12)
        ttk.Button(
            botones,
            text="Gestionar acceso",
            command=self._abrir_panel,
            width=20,
        ).pack(side="left", padx=6)
        ttk.Button(
            botones, text="Salir", command=self.cerrar, width=12
        ).pack(side="right", padx=6)

    # ------------------------------------------------------------------
    # Cámara / procesamiento
    # ------------------------------------------------------------------
    def _elegir_indice(self) -> int:
        indice = config.CAMARA_INDEX
        if detectar_indice(1, indice) == indice:
            return indice
        encontrado = detectar_indice()
        return encontrado if encontrado is not None else indice

    def _iniciar_camara(self) -> None:
        try:
            self.camara = Camara(self._elegir_indice())
            self.camara.iniciar()
            self.procesador = ProcesadorEnVivo(self.camara, self.reconocedor)
            self.procesador.iniciar()
        except Exception as exc:
            self.camara = None
            self.procesador = None
            self._hay_camara = False
            self.estado.config(text="SIN CÁMARA", background="#555555", foreground="white")
            messagebox.showwarning(
                "Cámara no disponible",
                f"No se pudo iniciar la cámara: {exc}\n\n"
                "Puedes gestionar las personas autorizadas desde el panel.",
                parent=self,
            )
            return
        self._hay_camara = True

    def pausar_camara(self) -> None:
        """Libera la cámara mientras se capturan fotos en el panel."""
        if self.procesador is not None:
            self.procesador.detener()
            self.procesador = None
        if self.camara is not None:
            self.camara.detener()
            self.camara = None

    def reanudar_camara(self) -> None:
        if getattr(self, "_hay_camara", False):
            self._iniciar_camara()

    def _actualizar(self) -> None:
        self.reloj.config(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))

        if self.procesador is not None:
            frame, estados = self.procesador.obtener()
            if frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imagen = Image.fromarray(rgb)
                imagen.thumbnail((config.ANCHO_CAMARA, config.ALTO_CAMARA))
                self._imagen = ImageTk.PhotoImage(imagen)
                self.video.config(image=self._imagen)
            self._actualizar_estado(estados)

        self.after(80, self._actualizar)

    def _actualizar_estado(self, estados: list[dict]) -> None:
        autorizados = [e for e in estados if e["autorizado"]]
        if autorizados:
            texto = f"AUTORIZADO: {autorizados[0]['nombre']}"
            color, fondo = "#ffffff", "#1f8b3e"
            detalle = f"Distancia de coincidencia: {autorizados[0]['distancia']:.3f}"
        elif estados:
            texto = "NO AUTORIZADO"
            color, fondo = "#ffffff", "#c0392b"
            detalle = "Rostro no reconocido. Acceso denegado."
        else:
            texto = "ACERQUE SU ROSTRO A LA CÁMARA"
            color, fondo = "#333333", "#e8e8e8"
            detalle = "Esperando para verificar la identidad..."

        self.estado.config(text=texto, foreground=color, background=fondo)
        self.detalle.config(text=detalle)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _abrir_panel(self) -> None:
        PanelPersonas(self, al_cambiar=self.reconocedor.recargar).mostrar()

    def cerrar(self) -> None:
        self.pausar_camara()
        self.destroy()
