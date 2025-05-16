import os
import sys
import shutil
from pathlib import Path

def build_executable():
    print("Iniciando construcción del ejecutable...")
    
    # Verificar que estamos en un entorno virtual
    if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix'):
        print("Error: Debes estar en un entorno virtual")
        sys.exit(1)
    
    # Instalar dependencias si no están instaladas
    os.system("pip install -r requirements.txt")
    
    # Instalar navegadores de Playwright
    os.system("playwright install chromium")
    
    # Crear directorio de sonidos si no existe
    sounds_dir = Path("sounds")
    sounds_dir.mkdir(exist_ok=True)
    
    # Verificar si existe el archivo de sonido MP3
    if not (sounds_dir / "notification.mp3").exists():
        print("AVISO: No se encontró el archivo notification.mp3 en la carpeta sounds/")
        print("Por favor, agrega un archivo MP3 de notificación en la carpeta sounds/")
        print("El archivo debe llamarse 'notification.mp3'")
        sys.exit(1)
    
    # Construir el ejecutable
    os.system("pyinstaller build.spec")
    
    print("\nConstrucción completada!")
    print("El ejecutable se encuentra en la carpeta 'dist'")

if __name__ == "__main__":
    build_executable() 