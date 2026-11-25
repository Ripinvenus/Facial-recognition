# Manual de usuario
## Sistema de Control de Acceso Biométrico (reconocimiento facial)

**Versión:** 1.0  
**Aplicación:** Control de Acceso Biométrico  
**Compatibilidad:** Windows, Linux y macOS

---

## Índice

1. [Introducción](#1-introducción)
2. [Requisitos e instalación](#2-requisitos-e-instalación)
3. [Iniciar la aplicación](#3-iniciar-la-aplicación)
4. [Pantalla principal](#4-pantalla-principal)
5. [Panel de gestión de acceso](#5-panel-de-gestión-de-acceso)
6. [Dar de alta a una persona](#6-dar-de-alta-a-una-persona)
7. [Dar de baja a una persona](#7-dar-de-baja-a-una-persona)
8. [Registro de accesos](#8-registro-de-accesos)
9. [Configuración avanzada](#9-configuración-avanzada)
10. [Buenas prácticas para un buen reconocimiento](#10-buenas-prácticas-para-un-buen-reconocimiento)
11. [Preguntas frecuentes y solución de problemas](#11-preguntas-frecuentes-y-solución-de-problemas)
12. [Seguridad y privacidad](#12-seguridad-y-privacidad)
13. [Anexo: estructura de archivos](#13-anexo-estructura-de-archivos)

---

## 1. Introducción

Esta aplicación verifica la identidad de las personas mediante **reconocimiento facial** y determina si tienen autorización para acceder. Todo el procesamiento ocurre **en tu propia computadora**: las fotos y firmas faciales no se envían a ningún servidor ni servicio externo.

### ¿Qué hace el sistema?

- Muestra el video de la cámara en tiempo real.
- Detecta rostros y dibuja un recuadro sobre ellos:
  - ✅ **Verde con el nombre**: persona autorizada.
  - 🔴 **Rojo con "NO AUTORIZADO"**: rostro desconocido o sin permiso.
- Permite **dar de alta** (registrar) y **dar de baja** (revocar) personas desde un panel protegido por contraseña.
- Guarda un **registro histórico** de todos los intentos de acceso.

### Contraseña del panel

La contraseña de fábrica es:

```
123
```

> ⚠️ Es un valor de prueba para fines practicos se defino este .

---

## 2. Requisitos e instalación

### 2.1 Requisitos previos

| Requisito | Detalle |
|---|---|
| Python | 3.10 o superior (se probó con 3.12) |
| Cámara | Cualquier webcam compatible (USB o integrada) |
| Sistema operativo | Windows, Linux o macOS |
| Interfaz gráfica | Entorno de escritorio (tkinter, incluido con Python) |

### 2.2 Crear el entorno virtual

**Windows (PowerShell):**
```powershell
cd ruta\a\Proyecto
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS (Terminal):**
```bash
cd ruta/a/Proyecto
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Instalar las dependencias

Dentro del entorno activado:

```bash
pip install -r requirements.txt
```

Esto instala `face-recognition`, `dlib`, `opencv-python`, `numpy` y `Pillow`.

**Notas por sistema operativo:**

- **Linux:** si `dlib` necesita compilarse, instala primero:
  ```bash
  sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev python3-tk
  ```
- **macOS:** instala las Command Line Tools de Xcode y, si hace falta, `brew install cmake`.
- **Windows:** normalmente basta con `pip install`. Si falla, instala *Visual Studio Build Tools* y `cmake`.

> `tkinter` viene incluido con Python en casi todos los sistemas. En Linux, si falta, instala el paquete del sistema `python3-tk` (no se instala con `pip`).

---

## 3. Iniciar la aplicación

Con el entorno virtual activado, desde la carpeta del proyecto:

```bash
python main.py
```

Si usas el entorno ya creado en este proyecto sin activarlo:

```bash
venv/bin/python main.py        # Linux / macOS
venv\Scripts\python main.py    # Windows
```

### ¿Qué sucede al iniciar?

1. Se crea automáticamente la carpeta `data/` (si no existe).
2. Se cargan las personas autorizadas guardadas.
3. Se abre la cámara. Si el índice configurado falla, se busca otra cámara disponible.
4. Aparece la pantalla principal.

---

## 4. Pantalla principal

La ventana muestra, de arriba abajo:

| Elemento | Descripción |
|---|---|
| **Título** | "Control de Acceso Biométrico" |
| **Fecha y hora** | Se actualiza en tiempo real (arriba a la derecha) |
| **Área de video** | Imagen de la cámara con los recuadros de detección |
| **Indicador de estado** | Mensaje grande y coloreado con el resultado |
| **Texto de detalle** | Información adicional (distancia o instrucción) |
| **Gestionar acceso** | Abre el panel de altas/bajas (requiere contraseña) |
| **Salir** | Cierra la aplicación y libera la cámara |

### Estados que puedes ver

| Estado | Color | Significado |
|---|---|---|
| `ACERQUE SU ROSTRO A LA CÁMARA` | Gris | No se detecta ningún rostro |
| `NO AUTORIZADO` | Rojo | Hay un rostro pero no coincide con nadie registrado |
| `AUTORIZADO: Nombre` | Verde | El rostro coincide con una persona dada de alta |

Cuando una persona es autorizada, el recuadro es verde y muestra el nombre junto a la *distancia de coincidencia* (un número menor indica mayor similitud; el umbral por defecto es 0.55).

Cuando no hay nadie dado de alta, **también aparece el recuadro rojo** sobre los rostros detectados.

---

## 5. Panel de gestión de acceso

### Paso a paso

1. En la pantalla principal, pulsa el botón **Gestionar acceso**.
2. Aparecerá la ventana **Acceso restringido**.
3. Escribe la contraseña (`123` por defecto) y pulsa **Aceptar** o la tecla `Enter`.
   - Si es incorrecta, verás un aviso y el campo se limpiará para volver a intentarlo.
   - Pulsa **Cancelar** o `Escape` para cerrar sin entrar.
4. Se abrirá la ventana **Gestión de personas autorizadas**, con:
   - Una **lista** con los nombres registrados.
   - Los botones **Dar de alta**, **Dar de baja**, **Ver registro** y **Cerrar**.

Mientras se usa el panel, la cámara de la pantalla principal se pausa y se libera para que el diálogo de captura pueda usarla. Al cerrar el diálogo, la cámara se reactiva automáticamente.

---

## 6. Dar de alta a una persona

1. En el panel, pulsa **Dar de alta**.
2. Se abre la ventana **Dar de alta una persona** con la vista de la cámara.
3. Escribe el **nombre** de la persona en el campo de texto.
4. Coloca el rostro frente a la cámara, bien iluminado y de frente (consulta la sección [10](#10-buenas-prácticas-para-un-buen-reconocimiento)).
5. Pulsa **Capturar rostro**. Repite hasta completar las **5 capturas** indicadas en el contador `0/5` → `5/5`.
   - Si no se detecta exactamente un rostro, aparecerá un aviso: coloca un solo rostro y vuelve a intentarlo.
   - Al llegar a 5, el botón *Capturar rostro* se desactiva automáticamente.
6. Pulsa **Guardar persona**.
7. Verás la confirmación. La persona aparecerá ahora en la lista del panel y tendrá acceso autorizado.

### ¿Qué se guarda?

- Una foto de referencia del rostro en `data/personas/<nombre>.jpg`.
- Las 5 firmas faciales en `data/encodings.pickle`.

Si das de alta un nombre que ya existía, sus firmas anteriores se **reemplazan** con las nuevas.

> Consejo: si la persona usa lentes, gorra o cambia mucho de apariencia, captura algunas fotos con y sin ellos.

---

## 7. Dar de baja a una persona

1. En el panel, selecciona el nombre en la lista.
2. Pulsa **Dar de baja**.
3. Confirma en el cuadro de diálogo **¿Quieres revocar el acceso a 'nombre'?**.
4. La persona desaparece de la lista, se elimina su foto y sus firmas faciales, y pierde el acceso de inmediato.

---

## 8. Registro de accesos

1. En el panel, pulsa **Ver registro**.
2. Se abre la ventana **Registro de accesos** con las últimas 100 entradas. La más reciente aparece primero.

### Formato de cada línea

```
2026-11-24 18:37:22 | AUTORIZADO    | Ana                 | dist=0.412
2026-11-24 18:38:05 | NO AUTORIZADO | Desconocido         | dist=0.781
```

| Campo | Significado |
|---|---|
| Fecha y hora | Momento del intento |
| Estado | `AUTORIZADO` o `NO AUTORIZADO` |
| Nombre | Persona identificada, o `Desconocido` |
| dist | Distancia de coincidencia (menor = más parecido) |

- Pulsa **Actualizar** para recargar el contenido.
- No se registran los momentos en los que no hay ningún rostro delante de la cámara.
- Para evitar un archivo gigante, el mismo estado solo se registra una vez cada 3 segundos como mínimo.

El archivo se guarda en `data/accesos.log` y puedes abrirlo con cualquier editor de texto.

---

## 9. Configuración avanzada

Todos los parámetros están en el archivo `config.py`, en la raíz del proyecto.

| Parámetro | Qué hace | Valor por defecto |
|---|---|---|
| `CAMARA_INDEX` | Índice de cámara (0 = primera). Si falla, se busca otra automáticamente | `0` |
| `ANCHO_CAMARA` / `ALTO_CAMARA` | Resolución solicitada a la cámara | `640` x `480` |
| `TOLERANCIA` | Umbral de coincidencia; menor = más estricto | `0.55` |
| `N_FOTOS_ALTA` | Cantidad de fotos al dar de alta | `5` |
| `ESCALA_DETECCION` | Reduce el frame para detectar más rápido | `0.25` |
| `CADA_N_FRAMES` | Se analiza 1 de cada N frames | `3` |
| `MODELO_DETECCION` | `cnn` (recomendado, más preciso) u `hog` (más rápido) | `cnn` |

### Cambiar la contraseña

La contraseña se guarda como un **hash SHA-256 con salt**, nunca en texto plano. En `config.py` modifica:

```python
PASSWORD_SALT = "biometria-proyecto-salt"
_PASSWORD_HASH = hashlib.sha256(
    (PASSWORD_SALT + "123").encode("utf-8")
).hexdigest()
```

Reemplaza `"123"` por tu nueva contraseña (y, preferiblemente, cambia también el *salt*). Guarda el archivo y reinicia la aplicación.

### Ajustar la sensibilidad

- Si personas **no autorizadas** son aceptadas → baja `TOLERANCIA` (p. ej. `0.50`).
- Si personas **autorizadas** son rechazadas → sube `TOLERANCIA` (p. ej. `0.60`) o vuelve a darlas de alta con mejor iluminación.

---

## 10. Buenas prácticas para un buen reconocimiento

- **Iluminación:** usa luz frontal y uniforme; evita contraluz (una ventana detrás de la persona).
- **Distancia:** coloca el rostro a unos 40–60 cm de la cámara, ocupando una parte importante de la imagen.
- **Posición:** mira a la cámara, con el rostro lo más de frente posible.
- **Capturas:** varía ligeramente el ángulo (unos grados a la izquierda y derecha) entre fotos.
- **Un rostro a la vez:** para dar de alta o verificar, asegúrate de que solo aparezca una persona.
- **Cámara limpia:** verifica que el lente no esté sucio o cubierto.
- **Apariencia:** si cambias drásticamente de peinado, barba o usas lentes nuevos, vuelve a darte de alta.

---

## 11. Preguntas frecuentes y solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| No aparece el botón "Gestionar acceso" | Ventana reducida o demasiado pequeña | Maximiza la ventana o reinicia la app (el tamaño correcto es 820x750) |
| Aparece "SIN CÁMARA" | Cámara ocupada por otra app o desconectada | Cierra otras apps que usen la cámara, conéctala y reinicia |
| No se detecta el rostro | Poca luz, rostro de lado o fuera de cuadro | Mejora la iluminación y coloca el rostro de frente |
| Todo aparece como "NO AUTORIZADO" | No hay personas dadas de alta, o mala captura | Da de alta a la persona siguiendo la sección [6](#6-dar-de-alta-a-una-persona) |
| Una persona autorizada no es reconocida | Capturas con poca luz o ángulo muy distinto | Vuelve a darla de alta con 5 fotos bien iluminadas |
| Personas desconocidas son aceptadas | `TOLERANCIA` demasiado alta | Baja el valor a `0.50` o menos |
| La app va lenta | Equipo con poco CPU | Usa `MODELO_DETECCION = "hog"` o aumenta `CADA_N_FRAMES` a `5` |
| Error al instalar `dlib` | Faltan herramientas de compilación | Instala los paquetes del sistema indicados en la sección [2.3](#23-instalar-las-dependencias) |
| La contraseña no funciona | Valor incorrecto o cambiado | Prueba con `123` o revisa `config.py` |

### Reiniciar desde cero

Si quieres borrar todos los datos (personas y registro):

1. Cierra la aplicación.
2. Elimina la carpeta `data/`.
3. Vuelve a iniciar: se creará vacía automáticamente.

---

## 12. Seguridad y privacidad

- **Datos locales:** las fotos, firmas faciales y el registro se guardan solo en `data/`. No hay conexión a internet.
- **Contraseña hasheada:** el panel no almacena la contraseña en texto plano.
- **Cambia la contraseña de prueba:** `123` es solo un valor de demostración.
- **Protege la carpeta `data/`:** contiene datos biométricos. No la compartas ni la subas a repositorios (ya está excluida en `.gitignore`).
- **Uso responsable:** la precisión del reconocimiento facial depende de la iluminación y las capturas. No lo uses como único mecanismo de seguridad en entornos críticos sin medidas adicionales.

---

## 13. Anexo: estructura de archivos

```
Proyecto/
├── main.py                    Al iniciar la aplicación
├── config.py                  Parámetros y contraseña
├── requirements.txt           Dependencias
├── Manual de usuario.md       Este documento
├── README.md                  Resumen técnico
├── src/
│   ├── almacenamiento.py      Altas, bajas y firmas faciales
│   ├── reconocedor.py         Detección y comparación
│   ├── camara.py              Captura de video
│   ├── procesador.py          Análisis en segundo plano y registro
│   ├── registro.py            Lectura/escritura del log
│   └── ui/
│       ├── app_principal.py   Pantalla principal
│       └── panel_personas.py  Panel de gestión
├── data/                      (se crea automáticamente)
│   ├── personas/              Fotos de referencia
│   ├── encodings.pickle       Firmas faciales
│   └── accesos.log            Registro de accesos
└── tests/                     Pruebas automáticas
```

### Comandos útiles

| Acción | Comando |
|---|---|
| Ejecutar la app | `python main.py` |
| Ejecutar pruebas | `python -m unittest discover -s tests -v` |
| Instalar dependencias | `pip install -r requirements.txt` |

---

**Fin del manual**
