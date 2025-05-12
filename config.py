from pathlib import Path
from datetime import datetime

# Configuración por defecto
DEFAULT_CHECK_INTERVAL = 3  # segundos
DEFAULT_TYPING_DELAY = 1    # segundos

# Configuración de archivos
BASE_DIR = Path(__file__).parent
EXPORT_DIR = BASE_DIR / "exports"

# Formato del nombre del archivo Excel
def get_default_filename(num_codes: int) -> str:
    date_str = datetime.now().strftime("%d%m%Y")
    return f"REPORTE_{date_str}_NUM_{num_codes:02d}.xlsx"

# Configuración del navegador
BROWSER_OPTIONS = {
    "headless": False,
    "window_size": (1024, 768)
}

# Estados de los inputs
class InputStatus:
    WAITING = "Esperando"
    READY = "Listo"
    TYPED = "Tipeado"
    ERROR = "Error" 