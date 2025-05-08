class Usuario:
    def __init__(self, nombre, unidad_academica=None, email=None):
        self.__nombre = nombre  # Encapsulamiento
        self.__rol = None
        self.__unidad_academica = unidad_academica
        self.__email = email
        self.__id = None  # Identificador único

    @property
    def nombre(self):
        return self.__nombre

    @property
    def rol(self):
        return self.__rol

    @rol.setter
    def rol(self, valor):
        self.__rol = valor

    @property
    def unidad_academica(self):
        return self.__unidad_academica

    @property
    def email(self):
        return self.__email

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, valor):
        if self.__id is None:  # Solo permite establecer el ID una vez
            self.__id = valor

    def __str__(self):
        return f"{self.__nombre} - {self.__rol} ({self.__unidad_academica})"

    def to_dict(self):
        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "rol": self.__rol,
            "unidad_academica": self.__unidad_academica,
            "email": self.__email
        }


class Estudiante(Usuario):
    def __init__(self, nombre, unidad_academica=None, email=None, carrera=None, semestre=None):
        super().__init__(nombre, unidad_academica, email)
        self.rol = "estudiante"
        self.__carrera = carrera
        self.__semestre = semestre

    @property
    def carrera(self):
        return self.__carrera

    @carrera.setter
    def carrera(self, value):
        self._carrera = value

    @property
    def semestre(self):
        return self.__semestre

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "carrera": self.__carrera,
            "semestre": self.__semestre
        })
        return data


class Profesor(Usuario):
    def __init__(self, nombre, unidad_academica=None, email=None, departamento=None, materias=None):
        super().__init__(nombre, unidad_academica, email)
        self.rol = "profesor"
        self.__departamento = departamento
        self.__materias = materias if materias else []

    @property
    def departamento(self):
        return self.__departamento

    @departamento.setter
    def departamento(self, value):
        self.__departamento = value

    @property
    def materias(self):
        return self.__materias

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "departamento": self.__departamento,
            "materias": self.__materias
        })
        return data


class Administrativo(Usuario):
    def __init__(self, nombre, unidad_academica=None, email=None, cargo=None, departamento=None):
        super().__init__(nombre, unidad_academica, email)
        self.rol = "administrativo"
        self.__cargo = cargo
        self.__departamento = departamento

    @property
    def cargo(self):
        return self.__cargo

    @property
    def departamento(self):
        return self.__departamento

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "cargo": self.__cargo,
            "departamento": self.__departamento
        })
        return data


class ResponsableArea(Usuario):
    def __init__(self, nombre, unidad_academica, email=None, areas_responsable=None, nivel_autorizacion=1):
        super().__init__(nombre, unidad_academica, email)
        self.rol = "responsable_area"
        self.__areas_responsable = areas_responsable if areas_responsable else []
        self.__nivel_autorizacion = nivel_autorizacion

    @property
    def areas_responsable(self):
        return self.__areas_responsable

    @property
    def nivel_autorizacion(self):
        return self.__nivel_autorizacion

    def puede_autorizar(self, espacio):
        return espacio.unidad_academica == self.unidad_academica and \
               espacio.nombre in self.__areas_responsable

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "areas_responsable": self.__areas_responsable,
            "nivel_autorizacion": self.__nivel_autorizacion
        })
        return data