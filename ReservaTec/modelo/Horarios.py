from datetime import datetime, time

class Horario:
    def __init__(self, fecha, hora_inicio, hora_fin):
        """
        Inicializa un horario
        Args:
            fecha: Fecha en formato YYYY-MM-DD
            hora_inicio: Hora de inicio en formato HH:MM
            hora_fin: Hora de fin en formato HH:MM
        """
        # Validar y convertir la fecha
        try:
            if isinstance(fecha, str):
                self._fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
            else:
                self._fecha = fecha

            # Validar y convertir las horas
            if isinstance(hora_inicio, str):
                self._hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
            else:
                self._hora_inicio = hora_inicio

            if isinstance(hora_fin, str):
                self._hora_fin = datetime.strptime(hora_fin, "%H:%M").time()
            else:
                self._hora_fin = hora_fin

            # Validar que la hora de fin sea posterior a la hora de inicio
            if self._hora_fin <= self._hora_inicio:
                raise ValueError("La hora de fin debe ser posterior a la hora de inicio")

        except ValueError as e:
            raise ValueError(f"El horario no es válido: {str(e)}")

    @property
    def fecha(self):
        return self._fecha

    @property
    def hora_inicio(self):
        return self._hora_inicio

    @property
    def hora_fin(self):
        return self._hora_fin

    def __str__(self):
        return f"Fecha: {self._fecha}, Hora inicio: {self._hora_inicio}, Hora fin: {self._hora_fin}"

    def to_dict(self):
        """Convierte el horario a un diccionario"""
        return {
            'fecha': self._fecha.strftime("%Y-%m-%d"),
            'hora_inicio': self._hora_inicio.strftime("%H:%M"),
            'hora_fin': self._hora_fin.strftime("%H:%M")
        }

    @classmethod
    def from_dict(cls, data):
        """
        Crea un horario desde un diccionario
        Args:
            data: Diccionario con los datos del horario
        Returns:
            Horario: Nueva instancia de Horario
        """
        return cls(
            fecha=data['fecha'],
            hora_inicio=data['hora_inicio'],
            hora_fin=data['hora_fin']
        )