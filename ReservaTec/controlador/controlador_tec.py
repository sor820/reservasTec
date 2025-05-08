import os
import json
from datetime import datetime
from modelo.Usuarios import Usuario, Estudiante, Profesor, Administrativo, ResponsableArea
from modelo.Espacios import Salon, Laboratorio, SalaJuntas, Auditorio
from modelo.Horarios import Horario
from modelo.Reservaciones import Reservacion
from modelo.GestorReservaciones1 import GestorReservaciones

class ControladorTec:
    def __init__(self, ruta_reservaciones="datos/reservas.json"):
        """
        Inicializa el controlador del sistema
        Args:
            ruta_reservaciones: Ruta al archivo JSON de reservaciones
        """
        # Obtener la ruta absoluta del directorio actual del script
        directorio_base = os.path.dirname(os.path.abspath(__file__))

        # Construir las rutas absolutas para los archivos
        self.directorio_datos = os.path.join(directorio_base, "..", "datos")
        self.ruta_usuarios = os.path.join(self.directorio_datos, "usuarios.json")
        self.ruta_espacios = os.path.join(self.directorio_datos, "espacios.json")
        ruta_reservaciones = os.path.join(self.directorio_datos, "reservas.json")

        print(f"Rutas de archivos:")
        print(f"Usuarios: {self.ruta_usuarios}")
        print(f"Espacios: {self.ruta_espacios}")
        print(f"Reservaciones: {ruta_reservaciones}")

        # Verificar que los archivos existen
        if not os.path.exists(self.ruta_usuarios):
            raise FileNotFoundError(f"No se encontró el archivo de usuarios en: {self.ruta_usuarios}")
        if not os.path.exists(self.ruta_espacios):
            raise FileNotFoundError(f"No se encontró el archivo de espacios en: {self.ruta_espacios}")
        if not os.path.exists(ruta_reservaciones):
            raise FileNotFoundError(f"No se encontró el archivo de reservaciones en: {ruta_reservaciones}")

        self.gestor = GestorReservaciones(ruta_reservaciones)
        self.usuario_actual = None
        self.espacios = self._cargar_espacios()
        self.usuarios = self._cargar_usuarios()

    def _cargar_usuarios(self):
        """
        Carga los usuarios desde el archivo JSON
        Returns:
            list: Lista de usuarios
        """
        try:
            with open(self.ruta_usuarios, 'r', encoding='utf-8') as f:
                datos_usuarios = json.load(f)

            usuarios = []
            for datos in datos_usuarios:
                rol = datos.get('rol')
                usuario = None

                if rol == "estudiante":
                    usuario = Estudiante(
                        datos['nombre'],
                        datos.get('unidad_academica'),
                        datos.get('email'),
                        datos.get('carrera'),
                        datos.get('semestre')
                    )
                elif rol == "profesor":
                    usuario = Profesor(
                        datos['nombre'],
                        datos.get('unidad_academica'),
                        datos.get('email'),
                        datos.get('departamento')
                    )
                elif rol == "administrativo":
                    usuario = Administrativo(
                        datos['nombre'],
                        datos.get('unidad_academica'),
                        datos.get('email'),
                        datos.get('cargo'),
                        datos.get('departamento')
                    )
                elif rol == "responsable_area":
                    usuario = ResponsableArea(
                        datos['nombre'],
                        datos.get('unidad_academica'),
                        datos.get('email'),
                        datos.get('areas_responsable', [])
                    )

                if usuario:
                    usuario.id = datos['id']
                    usuarios.append(usuario)

            return usuarios
        except Exception as e:
            print(f"Error al cargar usuarios: {str(e)}")
            return []

    def _cargar_espacios(self):
        """
        Carga los espacios desde el archivo JSON
        Returns:
            dict: Diccionario de espacios
        """
        try:
            with open(self.ruta_espacios, 'r', encoding='utf-8') as f:
                datos_espacios = json.load(f)

            espacios = {}
            for datos in datos_espacios:
                nombre = datos['nombre']
                tipo = datos['tipo'].lower()
                capacidad = datos['capacidad']
                responsable = datos.get('responsable', {})

                if tipo == "salon":
                    espacio = Salon(nombre, capacidad)
                elif tipo == "laboratorio":
                    espacio = Laboratorio(nombre, capacidad)
                elif tipo == "salajuntas":
                    espacio = SalaJuntas(nombre, capacidad)
                elif tipo == "auditorio":
                    espacio = Auditorio(nombre, capacidad)
                else:
                    continue

                espacios[nombre] = espacio

            return espacios
        except Exception as e:
            print(f"Error al cargar espacios: {str(e)}")
            return {}

    def obtener_usuarios(self):
        """
        Obtiene todos los usuarios del sistema
        Returns:
            list: Lista de usuarios
        """
        return self.usuarios

    def obtener_espacios(self):
        """
        Obtiene todos los espacios disponibles
        Returns:
            list: Lista de espacios
        """
        return list(self.espacios.values())

    def obtener_reservaciones(self):
        """
        Obtiene todas las reservaciones del sistema
        Returns:
            list: Lista de reservaciones
        """
        return self.gestor.reservaciones

    def iniciar_sesion(self, id_usuario: str, tipo_usuario: str = None) -> tuple:
        """
        Inicia sesión de un usuario en el sistema
        Args:
            id_usuario: Identificador del usuario
            tipo_usuario: Tipo de usuario (opcional)
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            usuario = next((u for u in self.usuarios if u.id == id_usuario), None)

            if usuario:
                if tipo_usuario and usuario.rol != tipo_usuario:
                    return False, "El tipo de usuario no coincide"
                self.usuario_actual = usuario
                return True, f"Sesión iniciada como {usuario.rol}: {usuario.nombre}"
            return False, "Usuario no encontrado"
        except Exception as e:
            return False, f"Error al iniciar sesión: {str(e)}"

    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        self.usuario_actual = None

    def crear_usuario(self, id, nombre, tipo, **kwargs):
        """
        Crea un nuevo usuario y lo guarda en el archivo JSON
        Args:
            id: Identificador del usuario
            nombre: Nombre del usuario
            tipo: Tipo de usuario (estudiante, profesor, administrativo, responsable_area)
            **kwargs: Atributos adicionales según el tipo
        Returns:
            Usuario: Objeto usuario creado o None si hay error
        """
        # Verificar si el ID ya existe
        if any(u.id == id for u in self.usuarios):
            print("Error: ID de usuario ya existe")
            return None

        nuevo_usuario = None
        datos_usuario = {
            "id": id,
            "nombre": nombre,
            "rol": tipo,
            "unidad_academica": kwargs.get('unidad_academica'),
            "email": kwargs.get('email')
        }

        try:
            if tipo == "estudiante":
                nuevo_usuario = Estudiante(
                    nombre,
                    kwargs.get('unidad_academica'),
                    kwargs.get('email'),
                    kwargs.get('carrera'),
                    kwargs.get('semestre')
                )
                datos_usuario.update({
                    "carrera": kwargs.get('carrera'),
                    "semestre": kwargs.get('semestre')
                })
            elif tipo == "profesor":
                nuevo_usuario = Profesor(
                    nombre,
                    kwargs.get('unidad_academica'),
                    kwargs.get('email'),
                    kwargs.get('departamento')
                )
                datos_usuario["departamento"] = kwargs.get('departamento')
            elif tipo == "administrativo":
                nuevo_usuario = Administrativo(
                    nombre,
                    kwargs.get('unidad_academica'),
                    kwargs.get('email'),
                    kwargs.get('cargo'),
                    kwargs.get('departamento')
                )
                datos_usuario.update({
                    "cargo": kwargs.get('cargo'),
                    "departamento": kwargs.get('departamento')
                })
            elif tipo == "responsable_area":
                nuevo_usuario = ResponsableArea(
                    nombre,
                    kwargs.get('unidad_academica'),
                    kwargs.get('email'),
                    kwargs.get('areas_responsable', [])
                )
                datos_usuario["areas_responsable"] = kwargs.get('areas_responsable', [])

            if nuevo_usuario:
                nuevo_usuario.id = id
                self.usuarios.append(nuevo_usuario)

                # Actualizar archivo JSON
                with open(self.ruta_usuarios, 'r', encoding='utf-8') as f:
                    usuarios_actuales = json.load(f)
                usuarios_actuales.append(datos_usuario)
                with open(self.ruta_usuarios, 'w', encoding='utf-8') as f:
                    json.dump(usuarios_actuales, f, indent=4, ensure_ascii=False)
                return nuevo_usuario

        except Exception as e:
            print(f"Error al crear usuario: {e}")
        return None

    def crear_espacio(self, nombre, tipo, capacidad, responsable_id):
        """
        Crea un nuevo espacio y lo guarda en el archivo JSON
        Args:
            nombre: Nombre del espacio
            tipo: Tipo de espacio (salon, laboratorio, salajuntas, auditorio)
            capacidad: Capacidad del espacio
            responsable_id: ID del responsable del espacio
        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        try:
            # Verificar si el espacio ya existe
            if nombre in self.espacios:
                return False

            # Buscar al responsable
            responsable = next((u for u in self.usuarios if u.id == responsable_id), None)
            if not responsable:
                return False

            # Crear el espacio según el tipo
            nuevo_espacio = None
            if tipo.lower() == "salon":
                nuevo_espacio = Salon(nombre, capacidad)
            elif tipo.lower() == "laboratorio":
                nuevo_espacio = Laboratorio(nombre, capacidad)
            elif tipo.lower() == "salajuntas":
                nuevo_espacio = SalaJuntas(nombre, capacidad)
            elif tipo.lower() == "auditorio":
                nuevo_espacio = Auditorio(nombre, capacidad)

            if nuevo_espacio:
                # Agregar a la lista en memoria
                self.espacios[nombre] = nuevo_espacio

                # Actualizar archivo JSON
                with open(self.ruta_espacios, 'r', encoding='utf-8') as f:
                    espacios_actuales = json.load(f)

                espacios_actuales.append({
                    "nombre": nombre,
                    "tipo": tipo.lower(),
                    "capacidad": capacidad,
                    "responsable": {
                        "id": responsable.id,
                        "nombre": responsable.nombre
                    }
                })

                with open(self.ruta_espacios, 'w', encoding='utf-8') as f:
                    json.dump(espacios_actuales, f, indent=4, ensure_ascii=False)

                return True

        except Exception as e:
            print(f"Error al crear espacio: {e}")
        return False

    def eliminar_usuario(self, id_usuario):
        """
        Elimina un usuario del sistema y actualiza el archivo JSON
        Args:
            id_usuario: ID del usuario a eliminar
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            # Verificar si hay reservaciones activas
            reservaciones_activas = [r for r in self.gestor.obtener_reservaciones_por_usuario(id_usuario)
                                     if r.estado in ["pendiente", "aprobada"]]
            if reservaciones_activas:
                # Cancelar reservaciones del usuario
                for reservacion in reservaciones_activas:
                    reservacion.cancelar()
                self.gestor._guardar_reservaciones()

            # Eliminar de la lista en memoria
            self.usuarios = [u for u in self.usuarios if u.id != id_usuario]

            # Actualizar archivo JSON
            with open(self.ruta_usuarios, 'r', encoding='utf-8') as f:
                usuarios_json = json.load(f)
            usuarios_json = [u for u in usuarios_json if u['id'] != id_usuario]
            with open(self.ruta_usuarios, 'w', encoding='utf-8') as f:
                json.dump(usuarios_json, f, indent=4, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False

    def eliminar_espacio(self, nombre_espacio):
        """
        Elimina un espacio del sistema
        Args:
            nombre_espacio: Nombre del espacio a eliminar
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if nombre_espacio in self.espacios:
                # Cancelar reservaciones futuras del espacio
                for reservacion in self.gestor.reservaciones:
                    if (reservacion.espacio.nombre == nombre_espacio and
                            reservacion.estado in ["pendiente", "aprobada"]):
                        reservacion.cancelar()

                # Eliminar de la lista en memoria
                del self.espacios[nombre_espacio]

                # Actualizar archivo JSON
                with open(self.ruta_espacios, 'r', encoding='utf-8') as f:
                    espacios_json = json.load(f)
                espacios_json = [e for e in espacios_json if e['nombre'] != nombre_espacio]
                with open(self.ruta_espacios, 'w', encoding='utf-8') as f:
                    json.dump(espacios_json, f, indent=4, ensure_ascii=False)

                self.gestor._guardar_reservaciones()
                return True
        except Exception as e:
            print(f"Error al eliminar espacio: {e}")
        return False

    def agregar_reservacion_directa(self, nombre_espacio, fecha, hora_inicio, hora_fin, tipo_evento, descripcion):
        try:
            # Buscar el espacio
            espacio = next((esp for esp in self.espacios if esp.nombre == nombre_espacio), None)
            if not espacio:
                return False

            # Crear un ID único para la reservación
            id_reservacion = f"RES_{len(self.obtener_reservaciones()) + 1}"

            # Crear nueva reservación
            nueva_reservacion = {
                "id": id_reservacion,
                "espacio": nombre_espacio,
                "fecha": fecha,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "tipo_evento": tipo_evento,
                "descripcion": descripcion,
                "estado": "activa"
            }

            # Guardar la reservación
            try:
                with open(os.path.join(self.directorio_datos, "reservaciones.json"), "r+") as f:
                    try:
                        reservaciones = json.load(f)
                    except json.JSONDecodeError:
                        reservaciones = []

                    reservaciones.append(nueva_reservacion)
                    f.seek(0)
                    json.dump(reservaciones, f, indent=4)
                    f.truncate()
                return True
            except FileNotFoundError:
                with open(os.path.join(self.directorio_datos, "reservaciones.json"), "w") as f:
                    json.dump([nueva_reservacion], f, indent=4)
                return True

        except Exception as e:
            print(f"Error al crear reservación: {str(e)}")
            return False

    def crear_reservacion(self, nombre_espacio: str, fecha: str,
                          hora_inicio: str, hora_fin: str,
                          tipo_evento: str, descripcion: str = "") -> tuple:
        """
        Crea una nueva reservación
        Args:
            nombre_espacio: Nombre del espacio a reservar
            fecha: Fecha de la reservación (YYYY-MM-DD)
            hora_inicio: Hora de inicio (HH:MM)
            hora_fin: Hora de fin (HH:MM)
            tipo_evento: Tipo de evento
            descripcion: Descripción del evento
        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.usuario_actual:
            return False, "No hay usuario con sesión iniciada"

        if nombre_espacio not in self.espacios:
            return False, "Espacio no encontrado"

        try:
            espacio = self.espacios[nombre_espacio]
            horario = Horario(fecha, hora_inicio, hora_fin)

            # Crear la reservación
            reservacion = Reservacion(
                self.usuario_actual,
                espacio,
                horario,
                tipo_evento,
                descripcion
            )

            # Intentar agregar la reservación
            if self.gestor.agregar_reservacion(reservacion):
                return True, "Reservación creada exitosamente"
            return False, "No se pudo crear la reservación (posible conflicto de horario)"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error al crear la reservación: {str(e)}"

    def eliminar_reservacion(self, id_reservacion):
        """
        Elimina una reservación del sistema
        Args:
            id_reservacion: ID de la reservación a eliminar
        Returns:
            bool: True si se eliminó exitosamente
        """
        return self.gestor.eliminar_reservacion(id_reservacion)

    def obtener_reservaciones_usuario(self):
        """
        Obtiene las reservaciones del usuario actual
        Returns:
            list: Lista de reservaciones del usuario
        """
        if not self.usuario_actual:
            return []
        return self.gestor.obtener_reservaciones_por_usuario(self.usuario_actual.id)

    def obtener_espacios_disponibles(self, fecha=None):
        """
        Obtiene los espacios disponibles para una fecha específica
        Args:
            fecha: Fecha para verificar disponibilidad (opcional)
        Returns:
            list: Lista de espacios disponibles
        """
        espacios_info = []
        for espacio in self.espacios.values():
            info = espacio.to_dict()
            if fecha:
                info['horarios_disponibles'] = self.gestor.obtener_disponibilidad(espacio, fecha)
            espacios_info.append(info)
        return espacios_info


if __name__ == "__main__":
    # Código de prueba
    controlador = ControladorTec()
    print("Sistema iniciado correctamente")