import sys
import os

# Add the backend directory to sys.path so we can import from it
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks import tarea_envio_alertas

if __name__ == "__main__":
    print("Iniciando prueba de envio de alertas...")
    tarea_envio_alertas()
    print("Prueba finalizada.")
