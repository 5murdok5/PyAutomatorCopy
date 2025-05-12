# Automatización Web Multiventana

Aplicación de escritorio para automatizar el tipeo de códigos en múltiples formularios web con exportación a Excel.

## Características

- Interfaz gráfica intuitiva con PySide6
- Soporte para múltiples inputs en diferentes ventanas
- Automatización web con Selenium
- Exportación de códigos tipeados a Excel
- Configuración persistente
- Logging para depuración

## Requisitos

- Python 3.10 o superior
- Chrome o Chromium instalado
- Dependencias listadas en `requirements.txt`

## Instalación

### 1. Crear y activar el entorno virtual

Es **MUY IMPORTANTE** usar un entorno virtual para evitar conflictos con otras instalaciones de Python:

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

Verificar que el entorno virtual está activado:

```bash
# Debería mostrar la ruta al Python del entorno virtual
which python  # En macOS/Linux
where python  # En Windows
```

### 2. Instalar dependencias

Con el entorno virtual activado, instalar las dependencias:

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Verificar la instalación

```bash
# Verificar que las dependencias se instalaron correctamente
pip list
```

## Uso

1. Ejecutar la aplicación:

```bash
python main.py
```

2. Configurar los inputs:

   - Agregar inputs usando el botón "Agregar Input"
   - Para cada input, especificar:
     - ID del input HTML
     - URL de la página
     - Marcar si se debe abrir en nueva ventana

3. Configurar el intervalo de verificación (en segundos)

4. Hacer clic en "Iniciar Proceso"

5. Ingresar códigos en el campo principal y presionar Enter

6. Exportar los códigos tipeados a Excel usando el botón "Exportar Excel"

## Solución de Problemas Comunes

### Problemas con el Entorno Virtual

1. **Error al activar el entorno virtual**

   ```bash
   # En Windows, si hay problemas con los scripts:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Dependencias no encontradas**

   ```bash
   # Asegurarse de que el entorno virtual está activado
   # El prompt debería mostrar (venv) al inicio

   # Reinstalar dependencias
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

3. **Conflictos de versiones**

   ```bash
   # Limpiar la caché de pip
   pip cache purge

   # Reinstalar con --no-cache-dir
   pip install --no-cache-dir -r requirements.txt
   ```

### Problemas con Selenium

1. **Error al iniciar Chrome**

   - Verificar que Chrome está instalado
   - Asegurarse de que la versión de Chrome es compatible con webdriver-manager

2. **Error de permisos en macOS/Linux**
   ```bash
   # Dar permisos de ejecución al chromedriver
   chmod +x venv/lib/python3.x/site-packages/selenium/webdriver/chrome/chromedriver
   ```

### Problemas con PySide6

1. **Error de importación**

   ```bash
   # Reinstalar PySide6
   pip uninstall PySide6
   pip install PySide6
   ```

2. **Problemas de visualización**
   - Verificar que los drivers de gráficos están actualizados
   - En Linux, asegurarse de tener instaladas las dependencias de Qt

## Empaquetado

Para crear un ejecutable:

```bash
# Windows
pyinstaller --onefile --windowed main.py

# macOS
pyinstaller --onefile --windowed main.py
```

## Estructura del Proyecto

```
project/
├── main.py              # Punto de entrada de la aplicación
├── ui/
│   └── form.py         # Interfaz gráfica
├── automation/
│   └── typer.py        # Lógica de automatización web
├── utils/
│   └── excel_exporter.py # Exportación a Excel
├── config.py           # Configuración
├── requirements.txt    # Dependencias
└── README.md          # Documentación
```

## Logging

La aplicación genera logs en el archivo `web_typer.log` para facilitar la depuración.

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

# Desactivar el entorno virtual actual

deactivate

# Eliminar el entorno virtual

rm -rf venv # En macOS/Linux
rmdir /s /q venv # En Windows

# Crear un nuevo entorno virtual

python -m venv venv
