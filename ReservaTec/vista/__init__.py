
"""
Módulo de Vista
--------------
Contiene todas las clases relacionadas con la interfaz gráfica del sistema.
"""

from .main_window  import VentanaPrincipal
from .tabs.espacios_tab import TabEspacios
from .tabs.reservaciones_tab import TabReservaciones
from .tabs.usuarios_tab import TabUsuarios
from .tabs.reportes_tab import TabReportes

__all__ = [
    'VentanaPrincipal',
    'TabEspacios',
    'TabReservaciones',
    'TabUsuarios',
    'TabReportes'
]
