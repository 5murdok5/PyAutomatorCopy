from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QSpinBox,
    QCheckBox, QScrollArea, QFileDialog, QMessageBox,
    QProgressBar, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon
import json
from pathlib import Path
import platform
import os

# Importar winsound solo en Windows
if platform.system() == 'Windows':
    import winsound

class InputConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Input ID
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("ID del input")
        self.input_id.setMinimumWidth(150)
        layout.addWidget(QLabel("ID:"))
        layout.addWidget(self.input_id)
        
        # URL
        self.url = QLineEdit()
        self.url.setPlaceholderText("URL de la página")
        self.url.setMinimumWidth(300)
        layout.addWidget(QLabel("URL:"))
        layout.addWidget(self.url)
        
        # Nueva ventana
        self.new_window = QCheckBox("Nueva ventana")
        layout.addWidget(self.new_window)
        
        # Estado visual
        self.status_label = QLabel("Esperando")
        self.set_status("Esperando")
        self.status_label.setMinimumWidth(90)
        layout.addWidget(self.status_label)
        
        # Botón eliminar
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        layout.addWidget(self.delete_btn)
        
        self.setLayout(layout)

    def get_config(self):
        return {
            "input_id": self.input_id.text(),
            "url": self.url.text(),
            "new_window": self.new_window.isChecked()
        }

    def set_status(self, status):
        """Actualiza el estado visual del input"""
        color = {
            "Esperando": "#FFC107",  # Amarillo
            "Listo": "#4CAF50",      # Verde
            "Tipeado": "#2196F3",   # Azul
            "Error": "#F44336"      # Rojo
        }.get(status, "#BDBDBD")
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px; padding: 2px 8px;")

class MainWindow(QMainWindow):
    code_entered = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automatización Web")
        self.setMinimumWidth(800)  # Duplicar el ancho mínimo
        self.setup_ui()
        self.load_config()
        self.setup_sound()

    def setup_sound(self):
        """Configura el sonido según el sistema operativo"""
        self.sound_enabled = True
        if platform.system() == 'Windows':
            self.play_sound = lambda: winsound.Beep(1000, 100)
        else:
            # Para macOS y Linux, usaremos un archivo de sonido
            self.sound_file = str(Path(__file__).parent.parent / "assets" / "beep.wav")
            if not Path(self.sound_file).exists():
                self.sound_enabled = False

    def play_success_sound(self):
        """Reproduce el sonido de éxito"""
        if not self.sound_enabled:
            return
            
        if platform.system() == 'Windows':
            self.play_sound()
        else:
            try:
                os.system(f"afplay {self.sound_file} &" if platform.system() == 'Darwin' 
                         else f"aplay {self.sound_file} &")
            except:
                pass

    def setup_ui(self):
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("Automatización Web")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Configuración de inputs
        config_group = QFrame()
        config_group.setFrameStyle(QFrame.StyledPanel)
        config_layout = QVBoxLayout(config_group)
        
        # Título de configuración
        config_title = QLabel("Configuración de Inputs")
        config_title.setFont(QFont('Arial', 12))
        config_layout.addWidget(config_title)
        
        # Área scrolleable para inputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.inputs_container = QWidget()
        self.inputs_layout = QVBoxLayout(self.inputs_container)
        scroll.setWidget(self.inputs_container)
        config_layout.addWidget(scroll)
        
        # Botón para agregar input
        add_input_btn = QPushButton("Agregar Input")
        add_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_input_btn.clicked.connect(self.add_input_config)
        config_layout.addWidget(add_input_btn)
        
        layout.addWidget(config_group)

        # Configuración de tiempo
        time_group = QFrame()
        time_group.setFrameStyle(QFrame.StyledPanel)
        time_layout = QHBoxLayout(time_group)
        time_layout.addWidget(QLabel("Intervalo de verificación (segundos):"))
        self.check_interval = QSpinBox()
        self.check_interval.setRange(1, 60)
        self.check_interval.setValue(3)
        time_layout.addWidget(self.check_interval)
        layout.addWidget(time_group)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Input principal
        input_group = QFrame()
        input_group.setFrameStyle(QFrame.StyledPanel)
        input_layout = QVBoxLayout(input_group)
        input_layout.addWidget(QLabel("Ingrese el código:"))
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Escriba el código y presione Enter")
        self.code_input.returnPressed.connect(self.on_code_entered)
        input_layout.addWidget(self.code_input)
        layout.addWidget(input_group)

        # Botones de acción
        action_group = QWidget()
        action_layout = QHBoxLayout(action_group)
        
        self.start_btn = QPushButton("Iniciar Proceso")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.start_btn.clicked.connect(self.start_process)
        action_layout.addWidget(self.start_btn)
        
        self.export_btn = QPushButton("Exportar Excel")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.export_btn.clicked.connect(self.export_excel)
        action_layout.addWidget(self.export_btn)
        
        layout.addWidget(action_group)

    def add_input_config(self):
        widget = InputConfigWidget()
        widget.delete_btn.clicked.connect(lambda: self.remove_input_config(widget))
        self.inputs_layout.addWidget(widget)

    def remove_input_config(self, widget):
        self.inputs_layout.removeWidget(widget)
        widget.deleteLater()

    def get_input_configs(self):
        configs = []
        for i in range(self.inputs_layout.count()):
            widget = self.inputs_layout.itemAt(i).widget()
            if isinstance(widget, InputConfigWidget):
                config = widget.get_config()
                if config["input_id"] and config["url"]:
                    configs.append(config)
        return configs

    def get_input_widgets(self):
        """Devuelve la lista de widgets de input"""
        widgets = []
        for i in range(self.inputs_layout.count()):
            widget = self.inputs_layout.itemAt(i).widget()
            if isinstance(widget, InputConfigWidget):
                widgets.append(widget)
        return widgets

    def set_input_status(self, input_id, status):
        """Actualiza el estado visual de un input por su ID"""
        for widget in self.get_input_widgets():
            if widget.input_id.text() == input_id:
                widget.set_status(status)

    def set_all_inputs_status(self, status):
        for widget in self.get_input_widgets():
            widget.set_status(status)

    def set_code_input_enabled(self, enabled):
        self.code_input.setEnabled(enabled)
        if enabled:
            self.code_input.setFocus()

    def on_code_entered(self):
        code = self.code_input.text().strip()
        if code:
            self.code_entered.emit(code)
            self.code_input.clear()
            self.play_success_sound()

    def start_process(self):
        configs = self.get_input_configs()
        if not configs:
            QMessageBox.warning(self, "Error", "Debe configurar al menos un input")
            return
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.set_code_input_enabled(False)
        self.set_all_inputs_status("Esperando")

    def show_loading(self, show=True):
        """Muestra u oculta el indicador de carga"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

    def export_excel(self):
        # La lógica de exportación se manejará en main.py
        pass

    def save_config(self):
        config = {
            "check_interval": self.check_interval.value(),
            "inputs": self.get_input_configs()
        }
        config_path = Path.home() / ".web_typer_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

    def load_config(self):
        config_path = Path.home() / ".web_typer_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                self.check_interval.setValue(config.get("check_interval", 3))
                for input_config in config.get("inputs", []):
                    widget = InputConfigWidget()
                    widget.input_id.setText(input_config.get("input_id", ""))
                    widget.url.setText(input_config.get("url", ""))
                    widget.new_window.setChecked(input_config.get("new_window", False))
                    self.inputs_layout.addWidget(widget)
            except Exception as e:
                print(f"Error al cargar la configuración: {e}") 