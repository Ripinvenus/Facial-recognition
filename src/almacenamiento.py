"""Persistencia de personas autorizadas.

Cada persona se guarda como:
  - una o varias firmas faciales (encodings) en data/encodings.pickle
  - una foto de referencia en data/personas/<nombre>.jpg
"""

from __future__ import annotations

import pickle
import re
from pathlib import Path

import numpy as np
from PIL import Image

import config


def asegurar_directorios() -> None:
    """Crea la estructura de carpetas necesaria si no existe."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.PERSONAS_DIR.mkdir(parents=True, exist_ok=True)


def _slug(nombre: str) -> str:
    """Convierte un nombre en un nombre de archivo seguro."""
    limpio = re.sub(r"[^A-Za-z0-9ÁÉÍÓÚÑáéíóúñ_-]+", "_", nombre.strip())
    return limpio.strip("_") or "persona"


def cargar_datos() -> dict:
    """Devuelve {'nombres': [...], 'encodings': [...]}."""
    asegurar_directorios()
    ruta: Path = config.ENCODINGS_FILE
    if not ruta.exists():
        return {"nombres": [], "encodings": []}
    try:
        with ruta.open("rb") as archivo:
            datos = pickle.load(archivo)
        if (
            isinstance(datos, dict)
            and isinstance(datos.get("nombres"), list)
            and isinstance(datos.get("encodings"), list)
        ):
            # Descarta entradas desparejadas (archivo corrupto o incompleto)
            pares = [
                (n, e)
                for n, e in zip(datos["nombres"], datos["encodings"])
                if isinstance(n, str) and e is not None
            ]
            if pares:
                return {
                    "nombres": [n for n, _ in pares],
                    "encodings": [e for _, e in pares],
                }
    except Exception as exc:  # pragma: no cover - ruta de error
        print(f"[almacenamiento] No se pudo leer {ruta}: {exc}")
    return {"nombres": [], "encodings": []}


def guardar_datos(datos: dict) -> None:
    """Escribe el archivo de firmas faciales."""
    asegurar_directorios()
    with config.ENCODINGS_FILE.open("wb") as archivo:
        pickle.dump(
            {"nombres": list(datos["nombres"]), "encodings": list(datos["encodings"])},
            archivo,
        )


def listar_personas() -> list[str]:
    """Nombres de las personas dadas de alta (sin repetir, ordenados)."""
    return sorted(set(cargar_datos()["nombres"]))


def guardar_persona(
    nombre: str, encodings: list, foto_rgb: np.ndarray | None = None
) -> None:
    """Añade (o reemplaza) a una persona con sus firmas faciales."""
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre no puede estar vacío")

    datos = cargar_datos()
    pares = [
        (n, e)
        for n, e in zip(datos["nombres"], datos["encodings"])
        if n != nombre
    ]
    for encoding in encodings:
        pares.append((nombre, np.asarray(encoding)))
    guardar_datos({"nombres": [n for n, _ in pares], "encodings": [e for _, e in pares]})

    if foto_rgb is not None:
        ruta_foto = config.PERSONAS_DIR / f"{_slug(nombre)}.jpg"
        Image.fromarray(foto_rgb).convert("RGB").save(ruta_foto, quality=90)


def eliminar_persona(nombre: str) -> int:
    """Elimina una persona y su foto. Devuelve el número de firmas borradas."""
    datos = cargar_datos()
    pares = [
        (n, e)
        for n, e in zip(datos["nombres"], datos["encodings"])
        if n != nombre
    ]
    eliminadas = len(datos["nombres"]) - len(pares)
    guardar_datos({"nombres": [n for n, _ in pares], "encodings": [e for _, e in pares]})

    slug = _slug(nombre)
    for archivo in config.PERSONAS_DIR.iterdir():
        if archivo.is_file() and archivo.stem == slug:
            archivo.unlink()
    return eliminadas


def ruta_foto(nombre: str) -> Path:
    return config.PERSONAS_DIR / f"{_slug(nombre)}.jpg"
