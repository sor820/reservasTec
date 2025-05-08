import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from modelo.Espacios import Salon, Laboratorio, SalaJuntas, Auditorio
from modelo.Horarios import Horario
from modelo.Usuarios import Usuario, Estudiante, Profesor, Administrativo, ResponsableArea
from modelo.Reservaciones import Reservacion


class GestorReservaciones:
    def __init__(self, archivo_reservaciones: str):
        self.archivo_reservaciones = archivo_reservaciones
        self.reservaciones = self._cargar_reservaciones()

    def agregar_reservacion(self, reservacion) -> bool:
        """
        Agrega una nueva reservación al sistema
        """
        # Verificar si la reservación es válida
        if not reservacion.es_valida():
            print("La reservación no es válida")
            return False

        # Verificar si hay conflictos
        if self._hay_conflicto(reservacion):
            print("Hay conflicto de horario")
            return False

        # Agregar la reservación
        self.reservaciones.append(reservacion)
        self._guardar_reservaciones()
        return True

    def aprobar_reservacion(self, id_reservacion: str, responsable) -> tuple[bool, str]:
        """
        Aprueba una reservación pendiente
        
        Args:
            id_reservacion: ID de la reservación
            responsable: Objeto ResponsableArea que aprueba
            
        Returns:
            tuple: (éxito, mensaje)
        """
        reservacion = self._buscar_reservacion(id_reservacion)
        if not reservacion:
            return False, "Reservación no encontrada"
            
        if not responsable.puede_autorizar(reservacion.espacio):
            return False, "No tiene autorización para aprobar reservaciones en este espacio"
            
        if reservacion.aprobar(responsable):
            self._guardar_reservaciones()
            return True, "Reservación aprobada exitosamente"
        return False, "No se pudo aprobar la reservación"

    def rechazar_reservacion(self, id_reservacion: str, responsable, motivo: str) -> tuple[bool, str]:
        """
        Rechaza una reservación pendiente
        
        Args:
            id_reservacion: ID de la reservación
            responsable: Objeto ResponsableArea que rechaza
            motivo: Motivo del rechazo
            
        Returns:
            tuple: (éxito, mensaje)
        """
        reservacion = self._buscar_reservacion(id_reservacion)
        if not reservacion:
            return False, "Reservación no encontrada"
            
        if not responsable.puede_autorizar(reservacion.espacio):
            return False, "No tiene autorización para rechazar reservaciones en este espacio"
            
        if reservacion.rechazar(responsable, motivo):
            self._guardar_reservaciones()
            return True, "Reservación rechazada exitosamente"
        return False, "No se pudo rechazar la reservación"

    def cancelar_reservacion(self, id_reservacion: str, usuario) -> tuple[bool, str]:
        """
        Cancela una reservación existente
        
        Args:
            id_reservacion: ID de la reservación
            usuario: Usuario que solicita la cancelación
            
        Returns:
            tuple: (éxito, mensaje)
        """
        reservacion = self._buscar_reservacion(id_reservacion)
        if not reservacion:
            return False, "Reservación no encontrada"
            
        # Verificar que sea el propietario o un responsable de área
        if reservacion.usuario.id != usuario.id and usuario.rol != "responsable_area":
            return False, "No tiene autorización para cancelar esta reservación"
            
        if reservacion.cancelar():
            self._guardar_reservaciones()
            return True, "Reservación cancelada exitosamente"
        return False, "No se pudo cancelar la reservación"

    def finalizar_reservacion(self, id_reservacion: str) -> tuple[bool, str]:
        """
        Marca una reservación como finalizada
        
        Args:
            id_reservacion: ID de la reservación
            
        Returns:
            tuple: (éxito, mensaje)
        """
        reservacion = self._buscar_reservacion(id_reservacion)
        if not reservacion:
            return False, "Reservación no encontrada"
            
        if reservacion.finalizar():
            self._guardar_reservaciones()
            return True, "Reservación finalizada exitosamente"
        return False, "No se pudo finalizar la reservación"


    def obtener_reservaciones_por_usuario(self, id_usuario: str) -> List:
        """
        Obtiene todas las reservaciones de un usuario específico
        """
        # Añadir log para depuración
        print(f"Buscando reservaciones para usuario: {id_usuario}")
        print(f"Total de reservaciones en el sistema: {len(self.reservaciones)}")
        reservaciones_usuario = [r for r in self.reservaciones
                               if hasattr(r.usuario, 'id') and r.usuario.id == id_usuario]
        print(f"Reservaciones encontradas: {len(reservaciones_usuario)}")
        return reservaciones_usuario

    def obtener_reservaciones_activas_por_espacio(self, nombre_espacio: str) -> List:
        """
        Obtiene las reservaciones activas para un espacio específico
        """
        return [r for r in self.reservaciones 
                if r.espacio.nombre.lower() == nombre_espacio.lower() 
                and r.estado in ["pendiente", "aprobada"]]

    def obtener_disponibilidad(self, espacio, fecha: str) -> List[dict]:
        """
        Obtiene los horarios disponibles para un espacio en una fecha específica
        
        Args:
            espacio: Objeto Espacio
            fecha: Fecha en formato YYYY-MM-DD
            
        Returns:
            List[dict]: Lista de franjas horarias disponibles
        """
        horarios_ocupados = [(r.horario.hora_inicio, r.horario.hora_fin) 
                            for r in self.reservaciones 
                            if r.espacio.nombre == espacio.nombre 
                            and r.horario.fecha == fecha 
                            and r.estado in ["pendiente", "aprobada"]]
        
        # Horario laboral: 7:00 - 22:00
        hora_inicio = datetime.strptime("07:00", "%H:%M")
        hora_fin = datetime.strptime("22:00", "%H:%M")
        intervalo = timedelta(minutes=30)  # Bloques de 30 minutos
        
        horarios_disponibles = []
        hora_actual = hora_inicio
        
        while hora_actual < hora_fin:
            hora_sig = hora_actual + intervalo
            franja = (hora_actual.strftime("%H:%M"), hora_sig.strftime("%H:%M"))
            
            # Verificar si la franja está ocupada
            ocupada = False
            for inicio, fin in horarios_ocupados:
                if (datetime.strptime(inicio, "%H:%M") < hora_sig and 
                    datetime.strptime(fin, "%H:%M") > hora_actual):
                    ocupada = True
                    break
            
            if not ocupada:
                horarios_disponibles.append({
                    "inicio": franja[0],
                    "fin": franja[1]
                })
            
            hora_actual = hora_sig
        
        return horarios_disponibles

    def _buscar_reservacion(self, id_reservacion: str):
        """Busca una reservación por su ID"""
        for reservacion in self.reservaciones:
            if reservacion.id == id_reservacion:
                return reservacion
        return None

    def _hay_conflicto(self, nueva_reservacion) -> bool:
        """
            Verifica si hay conflicto con otras reservaciones
            """
        print(f"Verificando conflictos para el espacio: {nueva_reservacion.espacio.nombre}")
        print(f"Fecha: {nueva_reservacion.horario.fecha}")
        print(f"Horario: {nueva_reservacion.horario.hora_inicio} - {nueva_reservacion.horario.hora_fin}")

        reservaciones_espacio = self.obtener_reservaciones_activas_por_espacio(
            nueva_reservacion.espacio.nombre
        )

        print(f"Reservaciones activas encontradas: {len(reservaciones_espacio)}")
        for r in reservaciones_espacio:
            if r.horario.hay_conflicto(nueva_reservacion.horario):
                print(f"Conflicto encontrado con reservación: {r.id}")
                print(f"Horario en conflicto: {r.horario.fecha} {r.horario.hora_inicio}-{r.horario.hora_fin}")
                return True
        return False

    def _cargar_reservaciones(self) -> List:
        """Carga las reservaciones desde el archivo JSON"""
        try:
            with open(self.archivo_reservaciones, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                return [self._deserializar_reservacion(r) for r in datos]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON")
            return []

    def _guardar_reservaciones(self) -> None:
        """Guarda las reservaciones en el archivo JSON"""
        try:
            with open(self.archivo_reservaciones, 'w', encoding='utf-8') as f:
                json.dump([r.to_dict() for r in self.reservaciones], 
                         f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar las reservaciones: {str(e)}")

    def _deserializar_reservacion(self, datos):
        """
        Convierte un diccionario en un objeto Reservacion
        """
        try:
            # Validar que los datos necesarios existan
            datos_usuario = datos.get("usuario")
            datos_espacio = datos.get("espacio")
            datos_horario = datos.get("horario")
            
            if not all([datos_usuario, datos_espacio, datos_horario]):
                raise ValueError("Faltan datos obligatorios en la reservación")

            # Crear el usuario según su tipo
            tipo_usuario = datos_usuario.get("rol", "").lower()
            nombre_usuario = datos_usuario.get("nombre", "")
            id_usuario = datos_usuario.get("id", "")

            if tipo_usuario == "estudiante":
                usuario = Estudiante(nombre_usuario)
                usuario.carrera = datos_usuario.get("carrera", "")
            elif tipo_usuario == "profesor":
                usuario = Profesor(nombre_usuario)
                usuario.departamento = datos_usuario.get("departamento", "")
            elif tipo_usuario == "administrativo":
                usuario = Administrativo(nombre_usuario)
            elif tipo_usuario == "responsable_area":
                usuario = ResponsableArea(
                    nombre_usuario,
                    datos_usuario.get("unidad_academica", ""),
                    datos_usuario.get("areas_responsable", [])
                )
            else:
                usuario = Usuario(nombre_usuario)
            
            usuario.id = id_usuario

            # Crear el espacio según su tipo
            tipo_espacio = datos_espacio.get("tipo", "").lower()
            nombre_espacio = datos_espacio.get("nombre", "")
            capacidad = datos_espacio.get("capacidad", 0)

            if tipo_espacio == "salon":
                espacio = Salon(nombre_espacio, capacidad)
            elif tipo_espacio == "laboratorio":
                espacio = Laboratorio(nombre_espacio, capacidad)
            elif tipo_espacio == "salajuntas":
                espacio = SalaJuntas(nombre_espacio, capacidad)
            elif tipo_espacio == "auditorio":
                espacio = Auditorio(nombre_espacio, capacidad)
            else:
                espacio = Salon(nombre_espacio, capacidad)  # Espacio por defecto

            # Crear el horario
            horario = Horario(
                datos_horario.get("fecha", ""),
                datos_horario.get("hora_inicio", ""),
                datos_horario.get("hora_fin", "")
            )

            # Crear la reservación
            reservacion = Reservacion(
                usuario,
                espacio,
                horario,
                datos.get("tipo_evento", ""),
                datos.get("descripcion", "")
            )

            # Establecer estado
            reservacion.estado = datos.get("estado", "pendiente")

            return reservacion
        except Exception as e:
            print(f"Error al deserializar reservación: {e}")
            print(f"Datos problemáticos: {datos}")
            return None