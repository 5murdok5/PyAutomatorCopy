import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExcelExporter:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "exports"
        self.base_dir.mkdir(exist_ok=True)
        self.codes = []

    def add_code(self, code, status="Tipeado"):
        """Agrega un código a la lista de códigos tipeados"""
        self.codes.append({
            "código": code,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": status
        })

    def export(self, filename=None):
        """Exporta los códigos a un archivo Excel"""
        if not self.codes:
            logger.warning("No hay códigos para exportar")
            return False

        try:
            if not filename:
                date_str = datetime.now().strftime("%d%m%Y")
                filename = f"REPORTE_{date_str}_NUM_{len(self.codes):02d}.xlsx"

            filepath = self.base_dir / filename
            
            df = pd.DataFrame(self.codes)
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"Archivo exportado exitosamente: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error al exportar a Excel: {str(e)}")
            return False

    def clear(self):
        """Limpia la lista de códigos"""
        self.codes = [] 