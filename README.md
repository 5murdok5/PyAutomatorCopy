# Automatizador de Códigos

Aplicación para automatizar la entrada de códigos en múltiples navegadores.

## Requisitos del Sistema

- Windows 10/11, macOS 10.15+ o Linux
- Python 3.8 o superior
- Navegador Chrome o Chromium instalado

## Instalación

### Método 1: Ejecutable (Recomendado)

1. Descarga el último release desde la sección de releases
2. Extrae el archivo ZIP
3. Ejecuta `AutomatizadorCodigos.exe` (Windows) o `AutomatizadorCodigos` (macOS/Linux)

### Método 2: Desde el código fuente

1. Clona este repositorio
2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
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

## Estructura de Archivos

- `config.json`: Configuración de URLs y selectores
- `sounds/`: Archivos de sonido para notificaciones
  - `notification.aiff`: Sonido para macOS
  - `notification.oga`: Sonido para Linux

## Configuración

1. Abre la aplicación
2. Configura las URLs y selectores en la tabla
3. Haz clic en "Preparar Navegadores"
4. Verifica que los inputs estén correctos
5. Comienza a ingresar códigos

## Solución de Problemas

- Si los navegadores no se abren, asegúrate de tener Chrome o Chromium instalado
- Si los sonidos no funcionan, verifica que los archivos de sonido estén en la carpeta correcta
- Para problemas con los selectores, usa las herramientas de desarrollo del navegador para verificar los IDs y clases

## Licencia

Este proyecto está bajo la Licencia MIT.
