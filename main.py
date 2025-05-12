import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QObject, Signal, Slot, QThread

from ui.form import MainWindow
from automation.typer import WebTyper
from utils.excel_exporter import ExcelExporter
from config import DEFAULT_CHECK_INTERVAL, DEFAULT_TYPING_DELAY

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_typer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AutomationWorker(QObject):
    finished = Signal()
    error = Signal(str)
    status_changed = Signal(str, str)  # input_id, status

    def __init__(self, typer, configs, code):
        super().__init__()
        self.typer = typer
        self.configs = configs
        self.code = code

    @Slot()
    def run(self):
        try:
            # Inicializar drivers para cada configuración
            for config in self.configs:
                window_id = f"window_{config['input_id']}"
                if config['new_window']:
                    if not self.typer.initialize_driver(config['url'], window_id):
                        self.error.emit(f"Error al abrir la ventana para {config['input_id']}")
                        return
                else:
                    # Reutilizar la primera ventana si no es nueva
                    if not self.typer.drivers:
                        if not self.typer.initialize_driver(config['url'], window_id):
                            self.error.emit(f"Error al abrir la ventana para {config['input_id']}")
                            return
                    # No recargar la página aquí
                self.status_changed.emit(config['input_id'], "Listo")

            # Tipear el código en cada input
            for config in self.configs:
                window_id = f"window_{config['input_id']}"
                if not config['new_window']:
                    window_id = list(self.typer.drivers.keys())[0]

                if self.typer.type_text(window_id, config['input_id'], self.code, DEFAULT_TYPING_DELAY):
                    self.status_changed.emit(config['input_id'], "Tipeado")
                else:
                    self.error.emit(f"Error al tipear en {config['input_id']}")
                    return

            self.finished.emit()

        except Exception as e:
            logger.error(f"Error en el proceso de automatización: {str(e)}")
            self.error.emit(str(e))

class InputVerifierWorker(QObject):
    finished = Signal(bool)
    status_changed = Signal(str, str)  # input_id, status
    error = Signal(str)

    def __init__(self, typer, configs, check_interval):
        super().__init__()
        self.typer = typer
        self.configs = configs
        self.check_interval = check_interval

    @Slot()
    def run(self):
        all_ok = True
        for config in self.configs:
            input_id = config['input_id']
            window_id = f"window_{input_id}"
            self.status_changed.emit(input_id, "Esperando")
            ok = self.typer.initialize_driver(config['url'], window_id)
            if not ok:
                self.status_changed.emit(input_id, "Error")
                all_ok = False
                continue
            # Esperar a que el input esté disponible
            for _ in range(20):  # Máximo 20 intentos
                element = self.typer.wait_for_input(window_id, input_id, timeout=self.check_interval)
                if element:
                    self.status_changed.emit(input_id, "Listo")
                    break
                else:
                    self.status_changed.emit(input_id, "Esperando")
            else:
                self.status_changed.emit(input_id, "Error")
                all_ok = False
        self.finished.emit(all_ok)

class WebTyperApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.typer = WebTyper(DEFAULT_CHECK_INTERVAL)
        self.exporter = ExcelExporter()
        
        # Conectar señales
        self.window.code_entered.connect(self.on_code_entered)
        self.window.start_btn.clicked.connect(self.start_process)
        self.window.export_btn.clicked.connect(self.export_excel)

    def start_process(self):
        configs = self.window.get_input_configs()
        if not configs:
            QMessageBox.warning(self.window, "Error", "Debe configurar al menos un input")
            return
        self.window.start_btn.setEnabled(False)
        self.window.set_code_input_enabled(False)
        self.window.progress_bar.setVisible(True)
        self.window.progress_bar.setRange(0, 0)
        self.window.set_all_inputs_status("Esperando")

        # Lanzar verificación en un hilo
        self.verifier_worker = InputVerifierWorker(self.typer, configs, self.window.check_interval.value())
        self.verifier_thread = QThread()
        self.verifier_worker.moveToThread(self.verifier_thread)
        self.verifier_thread.started.connect(self.verifier_worker.run)
        self.verifier_worker.status_changed.connect(self.window.set_input_status)
        self.verifier_worker.finished.connect(self.on_verification_finished)
        self.verifier_worker.error.connect(self.on_error)
        self.verifier_worker.finished.connect(self.verifier_thread.quit)
        self.verifier_worker.finished.connect(self.verifier_worker.deleteLater)
        self.verifier_thread.finished.connect(self.verifier_thread.deleteLater)
        self.verifier_thread.start()

    def on_verification_finished(self, all_ok):
        self.window.progress_bar.setVisible(False)
        if all_ok:
            self.window.set_code_input_enabled(True)
            self.window.start_btn.setEnabled(False)
        else:
            self.window.set_code_input_enabled(False)
            self.window.start_btn.setEnabled(True)
            QMessageBox.critical(self.window, "Error", "Uno o más inputs no están listos. Corrija y reintente.")

    def on_code_entered(self, code):
        if not self.window.code_input.isEnabled():
            return

        configs = self.window.get_input_configs()
        if not configs:
            return

        # Crear y configurar el worker
        self.worker = AutomationWorker(self.typer, configs, code)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Conectar señales
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.on_error)
        self.worker.status_changed.connect(self.on_status_changed)

        # Iniciar el proceso
        self.thread.start()
        self.exporter.add_code(code)

    def on_error(self, error_msg):
        QMessageBox.critical(self.window, "Error", error_msg)
        self.window.start_btn.setEnabled(True)

    def on_status_changed(self, input_id, status):
        logger.info(f"Input {input_id}: {status}")

    def export_excel(self):
        if not self.exporter.codes:
            QMessageBox.warning(self.window, "Error", "No hay códigos para exportar")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self.window,
            "Guardar archivo Excel",
            str(Path.home() / "REPORTE.xlsx"),
            "Archivos Excel (*.xlsx)"
        )

        if filename:
            if self.exporter.export(filename):
                QMessageBox.information(self.window, "Éxito", "Archivo exportado correctamente")
            else:
                QMessageBox.critical(self.window, "Error", "Error al exportar el archivo")

    def run(self):
        self.window.show()
        return self.app.exec()

if __name__ == "__main__":
    app = WebTyperApp()
    sys.exit(app.run()) 