# Control de Acceso Biométrico (reconocimiento facial)

## URL del repositorio: https://github.com/Ripinvenus/Facial-recognition 


Aplicación de escritorio con interfaz gráfica que verifica en tiempo real si una
persona está autorizada usando reconocimiento facial, y permite dar de alta o
baja a las personas desde un panel protegido con contraseña. Incluye un registro
histórico de todos los intentos de acceso.

Todo funciona **localmente**: las fotos y firmas faciales nunca salen de la máquina.

## Funcionalidades

- Video en vivo con detección de rostros y recuadro verde/rojo.
- Estado bien visible: **AUTORIZADO** (con nombre) o **NO AUTORIZADO**.
- Botón **Gestionar acceso** → panel protegido con contraseña (`123` por defecto).
  - **Dar de alta**: captura 5 fotos del rostro y guarda su firma facial.
  - **Dar de baja**: revoca el acceso y elimina los datos de la persona.
  - **Ver registro**: consulta los últimos accesos.
- Registro automático en `data/accesos.log` (fecha, hora, resultado, nombre,
  distancia de coincidencia) con anti-repetición para no llenar el archivo.
- Multiplataforma: rutas relativas, sin configuración específica por sistema.

## Estructura

```
Proyecto/
├── main.py                    Punto de entrada
├── config.py                  Configuración (rutas, cámara, tolerancia, contraseña)
├── requirements.txt           Dependencias
├── src/
│   ├── almacenamiento.py      Altas/bajas y archivo de firmas faciales
│   ├── reconocedor.py         Detección y comparación de rostros
│   ├── camara.py              Captura de video en hilo
│   ├── procesador.py          Análisis en segundo plano + registro de accesos
│   ├── registro.py            Escritura/lectura del log
│   └── ui/
│       ├── app_principal.py   Pantalla principal
│       └── panel_personas.py  Panel de gestión y diálogos
├── data/                      (se crea automáticamente)
│   ├── personas/              Fotos de referencia
│   ├── encodings.pickle       Firmas faciales
│   └── accesos.log            Registro de accesos
└── tests/                     Pruebas automáticas
```

## Instalación

### 1. Crear el entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

> **Nota sobre `dlib` / `face_recognition`:** en algunos sistemas no hay binario
> preconstruido y `pip` necesita compilarlos.
> - **Linux:** `sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev python3-tk`
> - **macOS:** `brew install cmake`, y asegúrate de tener las Command Line Tools de Xcode.
> - **Windows:** normalmente basta con `pip install` (hay wheels). Si falla,
>   instala primero `cmake` y un compilador (Visual Studio Build Tools).

`tkinter` viene incluido con Python en la mayoría de los sistemas. En Linux, si
falta, instala el paquete `python3-tk` del sistema (no se instala con `pip`).

### 3. Ejecutar

```bash
python main.py
```

Si el índice de cámara configurado no funciona, la aplicación busca
automáticamente otra cámara disponible. Si no hay ninguna, muestra un aviso y
permite seguir usando el panel de gestión.

## Uso

1. Al iniciar, la pantalla muestra **ACERQUE SU ROSTRO A LA CÁMARA**.
2. Pulsa **Gestionar acceso** y escribe la contraseña (`123`).
3. **Dar de alta**: escribe el nombre, coloca el rostro frente a la cámara y
   pulsa **Capturar rostro** hasta completar las 5 fotos desde distintos ángulos
   y con buena iluminación. Después **Guardar persona**.
4. Cierra el panel; la cámara se reactiva automáticamente.
5. Al acercarte, verás **AUTORIZADO: tu nombre**; a una persona desconocida,
   **NO AUTORIZADO**.
6. **Ver registro** muestra el historial de intentos.

## Configuración (`config.py`)

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| `CAMARA_INDEX` | Índice de cámara (0 = primera) | `0` |
| `TOLERANCIA` | Umbral de coincidencia (menor = más estricto) | `0.55` |
| `N_FOTOS_ALTA` | Fotos capturadas al dar de alta | `5` |
| `ESCALA_DETECCION` | Escala del frame para detectar más rápido | `0.25` |
| `CADA_N_FRAMES` | Se analiza 1 de cada N frames | `3` |
| `MODELO_DETECCION` | `cnn` detecta mejor (inclinados/poca luz); `hog` es más rápido | `cnn` |

### Cambiar la contraseña

La contraseña se guarda como hash SHA-256 con *salt* (nunca en texto plano).
Para cambiarla, edita en `config.py` las líneas:

```python
PASSWORD_SALT = "biometria-proyecto-salt"
_PASSWORD_HASH = hashlib.sha256((PASSWORD_SALT + "123").encode("utf-8")).hexdigest()
```

Reemplaza `"123"` por la nueva contraseña (y, idealmente, el *salt*).

> **Seguridad:** `123` es un valor de prueba. Cámbialo antes de usar la
> aplicación en un entorno real.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Consideraciones

- La precisión depende de la iluminación y de capturar varias fotos por persona.
  Se dibuja un recuadro **rojo (NO AUTORIZADO)** sobre cualquier rostro detectado
  e **verde con el nombre** cuando coincide con una persona dada de alta.
- El reconocimiento se ejecuta en segundo plano para que la interfaz no se
  congele. La cámara se libera al abrir la captura de fotos y al cerrar la app.
- Los datos se guardan en `data/`. Para empezar de cero, elimina esa carpeta.
