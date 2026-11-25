"""Registro histórico de intentos de acceso (data/accesos.log)."""

from __future__ import annotations

from datetime import datetime

import config


def registrar(estado: str, nombre: str = "", distancia: float | None = None) -> None:
    """Añade una línea al registro de accesos."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    distancia_txt = f"{distancia:.3f}" if distancia is not None else "-"
    quien = nombre or "Desconocido"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{fecha} | {estado:<13} | {quien:<20} | dist={distancia_txt}\n"
    with config.REGISTRO_FILE.open("a", encoding="utf-8") as archivo:
        archivo.write(linea)


def leer_ultimas(cantidad: int = 100) -> list[str]:
    """Devuelve las últimas entradas, la más reciente primero."""
    if not config.REGISTRO_FILE.exists():
        return []
    with config.REGISTRO_FILE.open("r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()
    return [linea.rstrip("\n") for linea in lineas[-cantidad:]][::-1]
