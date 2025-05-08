
from uuid import uuid4
from datetime import datetime
from typing import Optional


class Reservacion:
    ESTADOS_VALIDOS = ["pendiente", "aprobada", "rechazada", "cancelada", "finalizada"]
    TIPOS_EVENTO = ["clase", "conferencia", "reunión", "práctica", "otro"]

    def __init__(self, usuario, espacio, horario, tipo_evento, descripcion=""):
        self.__id = str(uuid4())
        self.__usuario = usuario
        self.__espacio = espacio
        self.__horario = horario
        self.__fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__estado = "pendiente"
        self.__tipo_evento = self.__validar_tipo_evento(tipo_evento)
        self.__descripcion = descripcion
        self.__unidad_academica = usuario.unidad_academica
        self.__aprobada_por = None
        self.__motivo_rechazo = None
        self.__fecha_actualizacion = None

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value: str):
        self.__id = value


    @property
    def usuario(self):
        return self.__usuario

    @property
    def espacio(self):
        return self.__espacio

    @property
    def horario(self):
        return self.__horario

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, valor):
        self.__estado = valor

    @property
    def tipo_evento(self):
        return self.__tipo_evento

    @property
    def descripcion(self):
        return self.__descripcion

    @property
    def unidad_academica(self):
        return self.__unidad_academica

    @property
    def aprobada_por(self):
        return self.__aprobada_por

    @property
    def motivo_rechazo(self):
        return self.__motivo_rechazo

    def __validar_tipo_evento(self, tipo_evento: str) -> str:
        tipo = tipo_evento.lower()
        if tipo not in self.TIPOS_EVENTO:
            raise ValueError(f"Tipo de evento no válido. Tipos permitidos: {', '.join(self.TIPOS_EVENTO)}")
        return tipo

    def aprobar(self, responsable_area) -> bool:
        if self.__estado != "pendiente":
            return False
        self.__estado = "aprobada"
        self.__aprobada_por = responsable_area
        self.__fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def rechazar(self, responsable_area, motivo: str) -> bool:
        if self.__estado != "pendiente":
            return False
        self.__estado = "rechazada"
        self.__aprobada_por = responsable_area
        self.__motivo_rechazo = motivo
        self.__fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def cancelar(self) -> bool:
        if self.__estado not in ["pendiente", "aprobada"]:
            return False
        self.__estado = "cancelada"
        self.__fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def finalizar(self) -> bool:
        if self.__estado != "aprobada":
            return False
        self.__estado = "finalizada"
        self.__fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def to_dict(self) -> dict:
        """
            Convierte la reservación a un diccionario
            """
        return {
            "id": self.id,
            "usuario": {
                "id": self.usuario.id,  # Aseguramos que se incluya el ID del usuario
                "nombre": self.usuario.nombre,
                "rol": self.usuario.__class__.__name__.lower(),
                "unidad_academica": getattr(self.usuario, 'unidad_academica', None),
                "departamento": getattr(self.usuario, 'departamento', None),  # Para profesores
                "carrera": getattr(self.usuario, 'carrera', None)  # Para estudiantes
            },
            "espacio": {
                "nombre": self.espacio.nombre,
                "tipo": self.espacio.__class__.__name__.lower(),
                "capacidad": self.espacio.capacidad
            },
            "horario": {
                "fecha": self.horario.fecha,
                "hora_inicio": self.horario.hora_inicio,
                "hora_fin": self.horario.hora_fin
            },
            "tipo_evento": self.tipo_evento,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "fecha_creacion": self._Reservacion__fecha_creacion,
            "fecha_actualizacion": self._Reservacion__fecha_actualizacion,
            "aprobada_por": {
                "nombre": self._Reservacion__aprobada_por.nombre,
                "unidad_academica": self._Reservacion__aprobada_por.unidad_academica,
                "areas_responsable": self._Reservacion__aprobada_por.areas_responsable
            } if self._Reservacion__aprobada_por else None,
            "motivo_rechazo": self._Reservacion__motivo_rechazo
        }

    def __str__(self):
        return (f"Reservación {self.__id}: {self.__espacio.nombre} - "
                f"{self.__horario.fecha} ({self.__horario.hora_inicio}-{self.__horario.hora_fin})")

    def es_valida(self) -> bool:
        """Verifica si la reservación es válida según el tipo de usuario y evento"""
        # Verificar que el horario sea válido
        if not self.__horario.es_valido():
            return False

        # Verificar el rol del usuario y los tipos de eventos permitidos
        rol_usuario = self.__usuario.rol
        tipo_evento = self.__tipo_evento

        # Definir permisos por rol
        if rol_usuario == "estudiante":
            return tipo_evento in ["práctica", "reunión"]
        elif rol_usuario == "profesor":
            return tipo_evento in ["clase", "práctica", "reunión", "conferencia"]
        elif rol_usuario == "administrativo":
            return tipo_evento in ["reunión", "conferencia"]
        elif rol_usuario == "responsable_area":
            return True  # El responsable de área puede crear cualquier tipo de evento
        
        return False