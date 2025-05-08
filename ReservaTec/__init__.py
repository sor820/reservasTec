"""
Sistema de Reservaciones TEC
---------------------------
Sistema para la gestión de reservaciones de espacios del Tecnológico de Costa Rica.

Este módulo inicializa la aplicación y sus componentes principales.
"""

import os
import sys
from datetime import datetime

# Información de la aplicación
__version__ = '1.0.0'
__author__ = 'TEC'
__license__ = 'Propietary'

# Configurar las rutas de los módulos
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# Configuración global
APP_NAME = "Sistema ReservaTec"
APP_CONFIG = {
    'data_dir': os.path.join(ROOT_DIR, 'datos'),
    'log_dir': os.path.join(ROOT_DIR, 'logs'),
    'config_file': os.path.join(ROOT_DIR, 'config.json')
}

# Asegurar que existan los directorios necesarios
for directory in [APP_CONFIG['data_dir'], APP_CONFIG['log_dir']]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Configuración de logging
import logging

logging.basicConfig(
    filename=os.path.join(APP_CONFIG['log_dir'], f'app_{datetime.now().strftime("%Y%m%d")}.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar los componentes principales
from .modelo import *
from .vista import VentanaPrincipal
from .controlador import ControladorTec


def iniciar_aplicacion():
    """
    Función principal para iniciar la aplicación.
    Crea una instancia del controlador y la ventana principal.
    """
    try:
        # Crear el controlador
        controlador = ControladorTec()

        # Crear y mostrar la ventana principal
        ventana = VentanaPrincipal()
        ventana.run()

    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {str(e)}")
        raise


# Si se ejecuta este archivo directamente
if __name__ == "__main__":
    iniciar_aplicacion()