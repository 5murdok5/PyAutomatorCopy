import logging
import os
import platform
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebTyper:
    def __init__(self, check_interval=3):
        self.check_interval = check_interval
        self.drivers = {}
        self.initialized = False
        self.setup_logging()

    def setup_logging(self):
        """Configura el logging para la clase"""
        self.logger = logging.getLogger(__name__)

    def initialize_driver(self, url, window_id):
        """Inicializa un nuevo driver de Chrome para una ventana específica"""
        try:
            if window_id in self.drivers:
                # Si el driver ya existe, solo navega a la URL
                self.drivers[window_id].get(url)
                return True

            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            
            # Configuraciones específicas para macOS
            if platform.system() == 'Darwin':
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                
                # Configurar el servicio con opciones específicas para macOS
                service = Service(
                    ChromeDriverManager().install(),
                    log_path=os.devnull  # Redirigir logs a null para evitar problemas
                )
            else:
                service = Service(ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)  # Timeout de 30 segundos para cargar páginas
            driver.get(url)
            
            self.drivers[window_id] = driver
            return True
        except Exception as e:
            self.logger.error(f"Error al inicializar el driver: {str(e)}")
            return False

    def wait_for_input(self, window_id, input_id, timeout=30):
        """Espera a que un input esté disponible en la página"""
        try:
            driver = self.drivers.get(window_id)
            if not driver:
                return False

            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, input_id))
            )
            return element
        except TimeoutException:
            self.logger.error(f"Timeout esperando el input {input_id} en la ventana {window_id}")
            return False
        except Exception as e:
            self.logger.error(f"Error al esperar el input: {str(e)}")
            return False

    def type_text(self, window_id, input_id, text, delay=3):
        """Tipea texto en un input específico y presiona Enter"""
        try:
            element = self.wait_for_input(window_id, input_id)
            if not element:
                return False

            element.clear()
            time.sleep(delay)  # Espera antes de tipear
            element.send_keys(text)
            element.send_keys(Keys.RETURN)  # Presiona Enter
            return True
        except Exception as e:
            self.logger.error(f"Error al tipear texto: {str(e)}")
            return False

    def close_all(self):
        """Cierra todos los drivers abiertos"""
        for driver in self.drivers.values():
            try:
                driver.quit()
            except Exception as e:
                self.logger.error(f"Error al cerrar el driver: {str(e)}")
        self.drivers.clear()
        self.initialized = False 