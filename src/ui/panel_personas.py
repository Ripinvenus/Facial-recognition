"""Panel de gestión de personas autorizadas, protegido por contraseña."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import cv2
import face_recognition
from PIL import Image, ImageTk

import config
from .. import almacenamiento, registro
from ..camara import Camara


class PanelPersonas:
    """Ventana de administración: altas, bajas y registro de accesos."""

    def __init__(self, app, al_cambiar=None) -> None:
        self.app = app
        self.al_cambiar = al_cambiar
        self.ventana: tk.Toplevel | None = None
        self.lista: tk.Listbox | None = None

    def mostrar(self) -> None:
        if not self._pedir_password():
            return
        self._construir()

    # ------------------------------------------------------------------
    # Contraseña
    # ------------------------------------------------------------------
    def _pedir_password(self) -> bool:
        dialogo = tk.Toplevel(self.app)
        dialogo.title("Acceso restringido")
        dialogo.transient(self.app)
        dialogo.resizable(False, False)

        marco = ttk.Frame(dialogo, padding=18)
        marco.grid()
        ttk.Label(
            marco, text="Introduce la contraseña del panel", font=("Segoe UI", 11, "bold")
        ).grid(column=0, row=0, columnspan=2, sticky="w", pady=(0, 12))
        ttk.Label(marco, text="Contraseña:").grid(column=0, row=1, sticky="w", pady=4)

        entrada = ttk.Entry(marco, show="*", width=22)
        entrada.grid(column=1, row=1, sticky="w", pady=4)
        entrada.focus_set()

        resultado = {"ok": False}

        def aceptar(_evento=None) -> None:
            if config.verificar_password(entrada.get()):
                resultado["ok"] = True
                dialogo.destroy()
            else:
                messagebox.showerror(
                    "Contraseña incorrecta",
                    "La contraseña no es válida. Inténtalo de nuevo.",
                    parent=dialogo,
                )
                entrada.delete(0, "end")
                entrada.focus_set()

        def cancelar() -> None:
            dialogo.destroy()

        botones = ttk.Frame(marco)
        botones.grid(column=0, row=2, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(botones, text="Cancelar", command=cancelar).pack(side="right", padx=5)
        ttk.Button(botones, text="Aceptar", command=aceptar).pack(side="right")

        dialogo.bind("<Return>", aceptar)
        dialogo.bind("<Escape>", lambda _e: cancelar())
        dialogo.grab_set()
        self.app.wait_window(dialogo)
        return resultado["ok"]

    # ------------------------------------------------------------------
    # Ventana principal del panel
    # ------------------------------------------------------------------
    def _construir(self) -> None:
        self.ventana = tk.Toplevel(self.app)
        self.ventana.title("Gestión de personas autorizadas")
        self.ventana.geometry("520x470")
        self.ventana.resizable(False, False)
        self.ventana.transient(self.app)

        ttk.Label(
            self.ventana,
            text="Personas con acceso autorizado",
            font=("Segoe UI", 13, "bold"),
        ).pack(pady=(16, 8))

        marco_lista = ttk.Frame(self.ventana, padding=(12, 0))
        marco_lista.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(marco_lista, orient="vertical")
        self.lista = tk.Listbox(
            marco_lista,
            height=11,
            font=("Segoe UI", 11),
            yscrollcommand=scroll.set,
        )
        scroll.config(command=self.lista.yview)
        scroll.pack(side="right", fill="y")
        self.lista.pack(side="left", fill="both", expand=True)
        self._actualizar_lista()

        marco_botones = ttk.Frame(self.ventana, padding=12)
        marco_botones.pack(fill="x")
        ttk.Button(
            marco_botones, text="Dar de alta", command=self._dar_de_alta, width=16
        ).pack(side="left", padx=4)
        ttk.Button(
            marco_botones, text="Dar de baja", command=self._dar_de_baja, width=16
        ).pack(side="left", padx=4)
        ttk.Button(
            marco_botones,
            text="Ver registro",
            command=self._ver_registro,
            width=16,
        ).pack(side="left", padx=4)
        ttk.Button(
            marco_botones, text="Cerrar", command=self.ventana.destroy, width=10
        ).pack(side="right", padx=4)

    def _actualizar_lista(self) -> None:
        if self.lista is None or not self.lista.winfo_exists():
            return
        self.lista.delete(0, "end")
        for nombre in almacenamiento.listar_personas():
            self.lista.insert("end", nombre)

    def _notificar_cambio(self) -> None:
        self._actualizar_lista()
        if self.al_cambiar:
            self.al_cambiar()

    # ------------------------------------------------------------------
    # Alta
    # ------------------------------------------------------------------
    def _dar_de_alta(self) -> None:
        # Reutiliza el índice que ya funcionó en la pantalla principal
        indice = getattr(self.app.camara, "indice", config.CAMARA_INDEX)
        self.app.pausar_camara()

        def al_cerrar() -> None:
            self._notificar_cambio()
            self.app.reanudar_camara()

        AltaDialog(self.ventana, al_cerrar, indice=indice)

    # ------------------------------------------------------------------
    # Baja
    # ------------------------------------------------------------------
    def _dar_de_baja(self) -> None:
        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showwarning(
                "Sin selección", "Selecciona una persona de la lista.", parent=self.ventana
            )
            return
        nombre = self.lista.get(seleccion[0])
        if not messagebox.askyesno(
            "Confirmar baja",
            f"¿Quieres revocar el acceso a '{nombre}'?",
            parent=self.ventana,
        ):
            return
        almacenamiento.eliminar_persona(nombre)
        self._notificar_cambio()
        messagebox.showinfo(
            "Acceso revocado", f"'{nombre}' ya no tiene autorización.", parent=self.ventana
        )

    # ------------------------------------------------------------------
    # Registro de accesos
    # ------------------------------------------------------------------
    def _ver_registro(self) -> None:
        RegistroDialog(self.ventana)


class AltaDialog(tk.Toplevel):
    """Captura varias fotos del rostro y guarda la firma facial."""

    def __init__(self, parent, al_cerrar, indice: int | None = None) -> None:
        super().__init__(parent)
        self.title("Dar de alta una persona")
        self.geometry("660x610")
        self.resizable(False, False)
        self.transient(parent)
        self.al_cerrar = al_cerrar
        self._cerrado = False
        self.encodings: list = []
        self.fotos: list = []
        self.camara: Camara | None = None
        self._imagen: ImageTk.PhotoImage | None = None

        ttk.Label(
            self,
            text="Coloca el rostro frente a la cámara y pulsa 'Capturar rostro' varias veces.",
            font=("Segoe UI", 10),
            wraplength=620,
        ).pack(pady=(12, 6))

        self.video = tk.Label(self, background="black", width=620, height=440)
        self.video.pack(padx=12, pady=4)

        marco_datos = ttk.Frame(self, padding=(12, 4))
        marco_datos.pack(fill="x")
        ttk.Label(marco_datos, text="Nombre:").pack(side="left")
        self.entry_nombre = ttk.Entry(marco_datos, width=26)
        self.entry_nombre.pack(side="left", padx=6)
        self.contador = tk.StringVar(value=f"0/{config.N_FOTOS_ALTA}")
        ttk.Label(marco_datos, textvariable=self.contador).pack(side="left", padx=10)

        marco_botones = ttk.Frame(self, padding=12)
        marco_botones.pack(fill="x")
        self.btn_capturar = ttk.Button(
            marco_botones, text="Capturar rostro", command=self._capturar, width=18
        )
        self.btn_capturar.pack(side="left", padx=4)
        self.btn_guardar = ttk.Button(
            marco_botones,
            text="Guardar persona",
            command=self._guardar,
            width=18,
            state="disabled",
        )
        self.btn_guardar.pack(side="left", padx=4)
        ttk.Button(marco_botones, text="Cancelar", command=self.cerrar, width=12).pack(
            side="right", padx=4
        )

        self.protocol("WM_DELETE_WINDOW", self.cerrar)

        try:
            self.camara = Camara(indice)
            self.camara.iniciar()
        except Exception as exc:
            messagebox.showerror(
                "Cámara no disponible", str(exc), parent=self
            )
            self.cerrar()
            return

        self._actualizar_video()
        self.grab_set()

    def _actualizar_video(self) -> None:
        if self._cerrado or self.camara is None:
            return
        frame = self.camara.leer()
        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = Image.fromarray(rgb)
            imagen.thumbnail((620, 440))
            self._imagen = ImageTk.PhotoImage(imagen)
            self.video.config(image=self._imagen)
        self.after(80, self._actualizar_video)

    def _capturar(self) -> None:
        if self.camara is None:
            return
        frame = self.camara.leer()
        if frame is None:
            messagebox.showwarning("Sin imagen", "Espera un momento e inténtalo de nuevo.", parent=self)
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones = face_recognition.face_locations(rgb)
        if len(ubicaciones) != 1:
            messagebox.showwarning(
                "Rostro no detectado",
                "Coloca un solo rostro bien iluminado frente a la cámara.",
                parent=self,
            )
            return
        codificaciones = face_recognition.face_encodings(rgb, ubicaciones)
        if not codificaciones:
            messagebox.showwarning("Sin rostro", "No se pudo leer el rostro. Inténtalo de nuevo.", parent=self)
            return

        self.encodings.append(codificaciones[0])
        top, right, bottom, left = ubicaciones[0]
        self.fotos.append(rgb[top:bottom, left:right])

        total = len(self.encodings)
        self.contador.set(f"{total}/{config.N_FOTOS_ALTA}")
        self.btn_guardar.config(state="normal")
        if total >= config.N_FOTOS_ALTA:
            self.btn_capturar.config(state="disabled")

    def _guardar(self) -> None:
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta el nombre", "Escribe el nombre de la persona.", parent=self)
            return
        almacenamiento.guardar_persona(
            nombre, self.encodings, self.fotos[-1] if self.fotos else None
        )
        messagebox.showinfo(
            "Persona dada de alta",
            f"'{nombre}' ahora tiene acceso autorizado.",
            parent=self,
        )
        self.cerrar()

    def cerrar(self) -> None:
        if self._cerrado:
            return
        self._cerrado = True
        if self.camara is not None:
            self.camara.detener()
        try:
            self.al_cerrar()
        finally:
            self.destroy()


class RegistroDialog(tk.Toplevel):
    """Muestra las últimas entradas del registro de accesos."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.title("Registro de accesos")
        self.geometry("720x420")
        self.transient(parent)

        marco = ttk.Frame(self, padding=10)
        marco.pack(fill="both", expand=True)
        self.texto = tk.Text(marco, height=18, font=("Consolas", 10), wrap="none")
        scroll = ttk.Scrollbar(marco, orient="vertical", command=self.texto.yview)
        self.texto.config(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.texto.pack(side="left", fill="both", expand=True)

        botones = ttk.Frame(self, padding=(10, 0, 10, 10))
        botones.pack(fill="x")
        ttk.Button(botones, text="Actualizar", command=self._cargar).pack(side="left")
        ttk.Button(botones, text="Cerrar", command=self.destroy).pack(side="right")

        self._cargar()

    def _cargar(self) -> None:
        lineas = registro.leer_ultimas(100)
        contenido = "\n".join(lineas) if lineas else "Todavía no hay registros de acceso."
        self.texto.config(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", contenido)
        self.texto.config(state="disabled")
