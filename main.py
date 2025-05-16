import sys
import json
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QProgressBar, QHeaderView, QComboBox, QFileDialog)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QColor
from playwright.sync_api import sync_playwright
import platform
from datetime import datetime
from openpyxl import Workbook

class BrowserWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    error = Signal(str)
    finished = Signal()
    input_verified = Signal(int, bool, str)

    def __init__(self, urls, selectors):
        super().__init__()
        self.urls = urls
        self.selectors = selectors
        self.browsers = []
        self.pages = []
        self.playwright = None
        self.browser = None
        self.historial_codigos = []

    def run(self):
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            for i, (url, selector) in enumerate(zip(self.urls, self.selectors)):
                page = self.browser.new_page()
                page.goto(url)
                self.pages.append(page)
                self.progress.emit(int((i + 1) / len(self.urls) * 100))
                self.status.emit(f"Abriendo navegador {i + 1} de {len(self.urls)}")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def close_browsers(self):
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            self.error.emit(f"Error al cerrar navegadores: {str(e)}")

    def verify_inputs(self):
        for i, (page, selector) in enumerate(zip(self.pages, self.selectors)):
            try:
                print(f"Verificando selector: {selector}")
                html = page.content()
                print(f"HTML actual de la página:\n{html[:1000]}")  # Imprime los primeros 1000 caracteres para no saturar la consola
                page.wait_for_selector(selector, timeout=5000)
                element = page.locator(selector).first
                exists = element.count() > 0
                self.input_verified.emit(i, exists, "✅" if exists else "❌")
            except Exception as e:
                print(f"Error al buscar el selector {selector}: {e}")
                self.input_verified.emit(i, False, f"❌ ({str(e)})")

    def type_code(self, code):
        for page, selector in zip(self.pages, self.selectors):
            try:
                element = page.locator(selector)
                element.fill(code)
                element.press("Enter")
            except Exception as e:
                self.error.emit(f"Error al escribir en {selector}: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automatizador de Códigos")
        self.setMinimumSize(900, 600)
        
        # Obtener la ruta del ejecutable o del script
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys._MEIPASS)
        else:
            self.base_path = Path(__file__).parent
            
        self.config_file = self.base_path / "config.json"
        self.load_config()
        self.historial_codigos = []
        self.init_ui()
        self.worker = None
        self.input_results = []

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {"inputs": []}
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Cambia a QHBoxLayout para dividir en dos secciones

        # --- Sección izquierda: Configuración de inputs ---
        left_layout = QVBoxLayout()
        # Tabla de inputs configurados
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["URL", "Tipo", "Valor", "Estado"])
        self.table.setStyleSheet("QTableWidget, QHeaderView::section { border: 1px solid #888; } QTableWidget::item { border: 1px solid #888; }")
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.update_table()
        left_layout.addWidget(self.table)

        # Hacer la tabla editable y conectar la señal de edición
        self.table.itemChanged.connect(self.on_table_item_changed)
        self.table.cellWidgetChanged = False
        self.table.currentCellChanged.connect(self.on_current_cell_changed)

        # Botones de control
        control_layout = QHBoxLayout()
        self.prepare_btn = QPushButton("Preparar Navegadores")
        self.verify_btn = QPushButton("Verificar Inputs")
        self.download_btn = QPushButton("Exportar a Excel")
        self.prepare_btn.clicked.connect(self.prepare_browsers)
        self.verify_btn.clicked.connect(self.verificar_inputs_en_principal)
        self.verify_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.descargar_reporte_excel)
        control_layout.addWidget(self.prepare_btn)
        control_layout.addWidget(self.verify_btn)
        control_layout.addWidget(self.download_btn)
        left_layout.addLayout(control_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)

        # Input para código
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ingrese el código aquí...")
        self.code_input.setEnabled(False)
        self.code_input.returnPressed.connect(self.process_code)
        left_layout.addWidget(self.code_input)

        # Estado
        self.status_label = QLabel("Listo")
        left_layout.addWidget(self.status_label)

        # --- Sección derecha: Tabla de códigos ingresados y contador ---
        right_layout = QVBoxLayout()
        self.contador_label = QLabel("Códigos ingresados: 0")
        self.contador_label.setAlignment(Qt.AlignCenter)
        font = self.contador_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.contador_label.setFont(font)
        right_layout.addWidget(self.contador_label)

        self.codigos_table = QTableWidget()
        self.codigos_table.setColumnCount(1)
        self.codigos_table.setHorizontalHeaderLabels(["Códigos ingresados"])
        self.codigos_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.codigos_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.codigos_table.setSelectionMode(QTableWidget.SingleSelection)
        self.codigos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.codigos_table)

        # Agrega los layouts al principal
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)

    def update_table(self):
        self.table.setRowCount(len(self.config["inputs"]))
        for i, input_data in enumerate(self.config["inputs"]):
            self.table.setItem(i, 0, QTableWidgetItem(input_data["url"]))
            # ComboBox para tipo
            combo = QComboBox()
            combo.addItems(["ID", "Clase", "Nombre", "CSS"])
            tipo = input_data.get("tipo", "ID")
            combo.setCurrentText(tipo)
            combo.currentTextChanged.connect(lambda _, row=i: self.on_combo_changed(row))
            self.table.setCellWidget(i, 1, combo)
            # Valor
            self.table.setItem(i, 2, QTableWidgetItem(input_data.get("valor", "")))
            # Estado
            self.table.setItem(i, 3, QTableWidgetItem(""))

    def prepare_browsers(self):
        if not self.config["inputs"]:
            QMessageBox.warning(self, "Advertencia", "No hay inputs configurados")
            return

        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.pages = []
        urls = [input_data["url"] for input_data in self.config["inputs"]]
        for url in urls:
            page = self.browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            self.pages.append(page)

        self.prepare_btn.setEnabled(False)
        self.status_label.setText("Navegadores listos")
        self.verify_btn.setEnabled(True)

    def verify_inputs(self):
        if self.worker:
            self.input_results = [None] * len(self.config["inputs"])
            self.worker.input_verified.connect(self.collect_input_status)
            # Generar selectores automáticos
            selectors = [self.generate_selector(input_data) for input_data in self.config["inputs"]]
            self.worker.selectors = selectors
            self.worker.verify_inputs()
            self.status_label.setText("Verificando inputs...")

    def collect_input_status(self, index, success, status):
        self.update_input_status(index, success, status)
        self.input_results[index] = (success, status)
        # Si ya se recibieron todos los resultados, mostrar el mensaje
        if all(result is not None for result in self.input_results):
            # Usar generate_selector para mostrar el selector en el mensaje de error
            errores = [
                f"Fila {i+1}: {self.generate_selector(self.config['inputs'][i])}"
                for i, (ok, _) in enumerate(self.input_results) if not ok
            ]
            if not errores:
                QMessageBox.information(self, "Verificación exitosa", "¡Todos los inputs fueron encontrados correctamente!")
            else:
                QMessageBox.warning(self, "Inputs no encontrados", "No se encontraron los siguientes inputs:\n" + "\n".join(errores))
            self.status_label.setText("Verificación finalizada")

    def update_input_status(self, index, success, status):
        pass  # No modificar la tabla visualmente

    def process_code(self):
        code = self.code_input.text()
        if not code:
            return

        selectors = [self.generate_selector(input_data) for input_data in self.config["inputs"]]
        for input_data, page, selector in zip(self.config["inputs"], self.pages, selectors):
            try:
                element = page.locator(selector)
                element.fill(code)
                element.press("Enter")
            except Exception as e:
                self.show_error(f"Error al escribir en {selector}: {str(e)}")
        # Solo agrega UNA VEZ el código al historial
        self.historial_codigos.insert(0, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), code))
        self.code_input.clear()
        self.play_sound()
        self.actualizar_tabla_codigos()

    def play_sound(self):
        try:
            sound_path = self.base_path / "sounds" / "notification.mp3"
            if sound_path.exists():
                if platform.system() == "Windows":
                    import winsound
                    winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f'afplay "{sound_path}"')
                else:  # Linux
                    os.system(f'paplay "{sound_path}"')
            else:
                # Fallback a sonidos del sistema
                if platform.system() == "Windows":
                    import winsound
                    winsound.Beep(1000, 100)
                elif platform.system() == "Darwin":  # macOS
                    os.system('afplay /System/Library/Sounds/Tink.aiff')
                else:  # Linux
                    os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')
        except Exception as e:
            print(f"Error al reproducir sonido: {e}")
            # No mostrar error al usuario, solo registrar en consola

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def on_browsers_ready(self):
        self.status_label.setText("Navegadores listos")
        self.verify_btn.setEnabled(True)

    def on_combo_changed(self, row):
        tipo = self.table.cellWidget(row, 1).currentText()
        while len(self.config["inputs"]) <= row:
            self.config["inputs"].append({"url": "", "tipo": "ID", "valor": ""})
        self.config["inputs"][row]["tipo"] = tipo
        self.save_config()

    def on_table_item_changed(self, item):
        row = item.row()
        col = item.column()
        if col in [0, 2]:  # Solo actualizar si se edita URL o Valor
            while len(self.config["inputs"]) <= row:
                self.config["inputs"].append({"url": "", "tipo": "ID", "valor": ""})
            if col == 0:
                self.config["inputs"][row]["url"] = item.text()
            elif col == 2:
                self.config["inputs"][row]["valor"] = item.text()
            self.save_config()

    def on_current_cell_changed(self, currentRow, currentColumn, previousRow, previousColumn):
        # Dummy para evitar errores con la señal
        pass

    def generate_selector(self, input_data):
        tipo = input_data.get("tipo", "ID")
        valor = input_data.get("valor", "")
        if tipo == "ID":
            # Escapar dos puntos y otros caracteres especiales
            valor_escapado = valor.replace(":", "\\:")
            return f"#{valor_escapado}"
        elif tipo == "Clase":
            return f".{valor}"
        elif tipo == "Nombre":
            return f"[name='{valor}']"
        elif tipo == "CSS":
            return valor
        else:
            return valor

    def verificar_inputs_en_principal(self):
        selectors = [self.generate_selector(input_data) for input_data in self.config["inputs"]]
        resultados = []
        for i, (page, selector) in enumerate(zip(self.pages, selectors)):
            print(f"Verificando selector: {selector}")
            try:
                page.wait_for_selector(selector, timeout=5000)
                element = page.locator(selector)
                exists = element.count() > 0
                resultados.append((i, exists, "✅" if exists else "❌"))
                print(f"Fila {i+1}: {'✅' if exists else '❌'}")
                self.table.setItem(i, 3, QTableWidgetItem("✅" if exists else "❌"))  # Actualiza la tabla
            except Exception as e:
                resultados.append((i, False, f"❌ ({str(e)})"))
                print(f"Error al buscar el selector {selector}: {e}")
                self.table.setItem(i, 3, QTableWidgetItem("❌"))  # Actualiza la tabla
        # Muestra los resultados en la interfaz
        errores = [
            f"Fila {i+1}: {self.generate_selector(self.config['inputs'][i])}"
            for i, ok, _ in resultados if not ok
        ]
        if not errores:
            QMessageBox.information(self, "Verificación exitosa", "¡Todos los inputs fueron encontrados correctamente!")
            self.code_input.setEnabled(True)  # Habilita el input de código
        else:
            QMessageBox.warning(self, "Inputs no encontrados", "No se encontraron los siguientes inputs:\n" + "\n".join(errores))
            self.code_input.setEnabled(False)  # Deshabilita el input de código si hay errores
        self.status_label.setText("Verificación finalizada")

    def closeEvent(self, event):
        try:
            if hasattr(self, "browser") and self.browser:
                self.browser.close()
            if hasattr(self, "playwright") and self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        event.accept()

    def descargar_reporte_excel(self):
        if not self.historial_codigos:
            QMessageBox.information(self, "Sin datos", "No hay códigos para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", "reporte_codigos.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "Códigos Ingresados"
        ws.append(["#", "Fecha", "Código"])
        for idx, (fecha, codigo) in enumerate(self.historial_codigos, 1):
            ws.append([idx, fecha, codigo])
        wb.save(path)
        QMessageBox.information(self, "Reporte guardado", f"Reporte guardado en:\n{path}")

    def actualizar_tabla_codigos(self):
        # Muestra todos los códigos ingresados, el más reciente arriba
        self.codigos_table.setRowCount(len(self.historial_codigos))
        for i, (fecha, codigo) in enumerate(self.historial_codigos):
            item = QTableWidgetItem(codigo)
            self.codigos_table.setItem(i, 0, item)
            # Ajusta la numeración: el más reciente es 1, el siguiente 2, etc.
            self.codigos_table.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
        self.contador_label.setText(f"Códigos ingresados: {len(self.historial_codigos)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 