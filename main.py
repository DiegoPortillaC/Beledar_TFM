import subprocess
import sys

# Lista de librerías necesarias
librerias = ["matplotlib", "PIL", "numpy"]  # tkinter viene con Python, no hace falta

for lib in librerias:
    try:
        if lib == "PIL":
            import PIL
        else:
            __import__(lib)
    except ImportError:
        print(f"Instalando {lib}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# Luego importamos nuestra interfaz
from functions import crear_interfaz

if __name__ == "__main__":
    crear_interfaz()
