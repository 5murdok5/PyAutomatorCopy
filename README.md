# Automatizador de Códigos

Aplicación para automatizar la entrada de códigos en múltiples navegadores de forma simultánea.

## Características

- Interfaz gráfica intuitiva con PySide6
- Automatización de navegadores con Playwright
- Soporte para múltiples URLs y selectores
- Verificación automática de campos
- Exportación de reportes a Excel
- Notificaciones sonoras
- Ejecutable portable

## Requisitos del Sistema

### Windows

- Windows 10/11
- Python 3.8 o superior
- Chrome o Chromium instalado
- 4GB RAM mínimo

### macOS

- macOS 10.15 o superior
- Python 3.8 o superior
- Chrome o Chromium instalado
- 4GB RAM mínimo

### Linux

- Ubuntu 20.04+ / Debian 10+ / Fedora 33+
- Python 3.8 o superior
- Chrome o Chromium instalado
- 4GB RAM mínimo
- Paquetes adicionales:
  ```bash
  sudo apt-get install libgl1-mesa-glx  # Para Ubuntu/Debian
  sudo dnf install mesa-libGL  # Para Fedora
  ```

## Instalación

### Método 1: Ejecutable (Recomendado)

1. Descarga el último release desde la sección de releases
2. Extrae el archivo ZIP
3. Ejecuta:
   - Windows: `AutomatizadorCodigos.exe`
   - macOS: `AutomatizadorCodigos.app`
   - Linux: `./AutomatizadorCodigos`

### Método 2: Desde el código fuente

1. Clona este repositorio:

   ```bash
   git clone https://github.com/tu-usuario/automatizador-codigos.git
   cd automatizador-codigos
   ```

2. Crea y activa un entorno virtual:

   **Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Instala los navegadores de Playwright:

   ```bash
   playwright install chromium
   ```

5. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

## Configuración

1. Abre la aplicación
2. En la tabla de configuración:
   - Agrega las URLs de las páginas
   - Selecciona el tipo de selector (ID, Clase, Nombre, CSS)
   - Ingresa el valor del selector
3. Haz clic en "Preparar Navegadores"
4. Verifica que los inputs estén correctos (deben aparecer ✅)
5. Comienza a ingresar códigos

## Estructura de Archivos

```
automatizador-codigos/
├── main.py              # Aplicación principal
├── build.py            # Script de construcción
├── requirements.txt    # Dependencias
├── README.md          # Este archivo
├── config.json        # Configuración (se crea automáticamente)
└── sounds/            # Archivos de sonido
    └── notification.mp3
```

## Solución de Problemas

### Windows

- Si el navegador no se abre:
  - Verifica que Chrome esté instalado
  - Ejecuta como administrador
- Si no hay sonido:
  - Verifica el volumen del sistema
  - Asegúrate de que el archivo `notification.mp3` existe

### macOS

- Si la aplicación no se abre:
  - Ejecuta `xattr -cr AutomatizadorCodigos.app`
- Si no hay sonido:
  - Verifica los permisos de audio
  - Asegúrate de que el archivo `notification.mp3` existe

### Linux

- Si hay errores de dependencias:
  ```bash
  sudo apt-get install libgl1-mesa-glx  # Ubuntu/Debian
  sudo dnf install mesa-libGL  # Fedora
  ```
- Si no hay sonido:
  - Instala `paplay`: `sudo apt-get install pulseaudio-utils`
  - Verifica que PulseAudio esté corriendo

## Desarrollo

### Construir el ejecutable

1. Asegúrate de estar en el entorno virtual
2. Ejecuta:
   ```bash
   python build.py
   ```
3. El ejecutable se generará en la carpeta `dist`

### Estructura del código

- `main.py`: Interfaz gráfica y lógica principal
- `build.py`: Script de construcción del ejecutable
- `requirements.txt`: Dependencias del proyecto

## Contribuir

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
