"""Pruebas básicas de persistencia, contraseña y registro."""

import tempfile
import unittest
from pathlib import Path

import numpy as np

import config
from src import almacenamiento, registro


class TestSistema(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        base = Path(self.temporal.name)
        self._rutas = (
            config.DATA_DIR,
            config.PERSONAS_DIR,
            config.ENCODINGS_FILE,
            config.REGISTRO_FILE,
        )
        config.DATA_DIR = base
        config.PERSONAS_DIR = base / "personas"
        config.ENCODINGS_FILE = base / "encodings.pickle"
        config.REGISTRO_FILE = base / "accesos.log"
        almacenamiento.asegurar_directorios()

    def tearDown(self):
        (
            config.DATA_DIR,
            config.PERSONAS_DIR,
            config.ENCODINGS_FILE,
            config.REGISTRO_FILE,
        ) = self._rutas
        self.temporal.cleanup()

    def test_password(self):
        self.assertTrue(config.verificar_password("123"))
        self.assertFalse(config.verificar_password("124"))

    def test_alta_listado_baja(self):
        self.assertEqual(almacenamiento.listar_personas(), [])
        encode = np.array([0.1, 0.2, 0.3], dtype=np.float64)

        almacenamiento.guardar_persona("Ana", [encode, encode])
        self.assertEqual(almacenamiento.listar_personas(), ["Ana"])
        datos = almacenamiento.cargar_datos()
        self.assertEqual(len(datos["encodings"]), 2)

        # Reemplazar los encodings existentes de Ana
        almacenamiento.guardar_persona("Ana", [encode])
        self.assertEqual(len(almacenamiento.cargar_datos()["encodings"]), 1)

        eliminadas = almacenamiento.eliminar_persona("Ana")
        self.assertEqual(eliminadas, 1)
        self.assertEqual(almacenamiento.listar_personas(), [])
        self.assertEqual(almacenamiento.cargar_datos()["encodings"], [])

    def test_registro(self):
        self.assertEqual(registro.leer_ultimas(), [])
        registro.registrar("AUTORIZADO", "Ana", 0.42)
        registro.registrar("NO AUTORIZADO")
        entradas = registro.leer_ultimas()
        self.assertEqual(len(entradas), 2)
        # El registro devuelve primero la entrada más reciente
        self.assertIn("Desconocido", entradas[0])
        self.assertIn("Ana", entradas[1])
        self.assertIn("AUTORIZADO", entradas[1])


if __name__ == "__main__":
    unittest.main()
