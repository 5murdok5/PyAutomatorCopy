# Carpeta Assets

Esta carpeta contiene recursos necesarios para la aplicación:

## Archivos de Sonido

- `beep.wav`: Archivo de sonido para la confirmación de acciones en sistemas macOS y Linux.

## Notas

- En Windows, se utiliza la función `winsound.Beep()` para generar el sonido.
- En macOS, se utiliza el comando `afplay` con el archivo `beep.wav`.
- En Linux, se utiliza el comando `aplay` con el archivo `beep.wav`.

Si deseas personalizar el sonido de confirmación, puedes reemplazar el archivo `beep.wav` con tu propio archivo de sonido, asegurándote de que:

1. El archivo esté en formato WAV
2. El nombre del archivo sea `beep.wav`
3. El archivo sea de corta duración (menos de 1 segundo)
