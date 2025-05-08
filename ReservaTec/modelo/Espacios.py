from typing import Dict

class Espacio:
    """Clase base para representar espacios reservables"""
    def __init__(self, nombre: str, capacidad: int, responsable_id=None):
        self.__nombre = nombre
        self.__capacidad = capacidad
        self.__tipo = None
        self.responsable_id = responsable_id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    @property
    def tipo(self) -> str:
        return self.__tipo

    def to_dict(self) -> Dict:
        """Convierte el espacio a un diccionario"""
        return {
            "nombre": self.__nombre,
            "tipo": self.__tipo,
            "capacidad": self.__capacidad
        }

    def __str__(self) -> str:
        return f"{self.__nombre} ({self.__tipo}) - Capacidad: {self.__capacidad}"


class Salon(Espacio):
    """Clase para representar un salón de clases"""
    def __init__(self, nombre: str, capacidad: int):
        super().__init__(nombre, capacidad)
        self._Espacio__tipo = "salon"


class Laboratorio(Espacio):
    """Clase para representar un laboratorio"""
    def __init__(self, nombre: str, capacidad: int):
        super().__init__(nombre, capacidad)
        self._Espacio__tipo = "laboratorio"


class SalaJuntas(Espacio):
    """Clase para representar una sala de juntas"""
    def __init__(self, nombre: str, capacidad: int):
        super().__init__(nombre, capacidad)
        self._Espacio__tipo = "sala de juntas"


class Auditorio(Espacio):
    """Clase para representar un auditorio"""
    def __init__(self, nombre: str, capacidad: int):
        super().__init__(nombre, capacidad)
        self._Espacio__tipo = "auditorio"