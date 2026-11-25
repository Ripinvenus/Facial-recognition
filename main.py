"""Punto de entrada del sistema de control de acceso biométrico."""

from src import almacenamiento
from src.ui.app_principal import AppPrincipal


def main() -> None:
    almacenamiento.asegurar_directorios()
    aplicacion = AppPrincipal()
    aplicacion.mainloop()


if __name__ == "__main__":
    main()
