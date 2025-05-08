import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import json
from controlador.controlador_tec import ControladorTec


class SistemaReservaciones(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Reservaciones TEC")
        self.geometry("1200x700")

        # Inicializar el controlador
        self.controlador = ControladorTec()

        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # Crear pestañas
        self.tab_reservaciones = ttk.Frame(self.notebook)
        self.tab_espacios = ttk.Frame(self.notebook)
        self.tab_usuarios = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_reservaciones, text='Reservaciones')
        self.notebook.add(self.tab_espacios, text='Espacios')
        self.notebook.add(self.tab_usuarios, text='Usuarios')

        # Configurar pestañas
        self.configurar_tab_reservaciones()
        self.configurar_tab_espacios()
        self.configurar_tab_usuarios()

    def configurar_tab_reservaciones(self):
        # Frame izquierdo para el formulario
        frame_form = ttk.LabelFrame(self.tab_reservaciones, text="Nueva Reservación", padding="10")
        frame_form.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # Elementos del formulario
        ttk.Label(frame_form, text="Espacio:").grid(row=0, column=0, pady=5)
        espacios_disponibles = [esp.nombre for esp in self.controlador.obtener_espacios()]
        self.espacio = ttk.Combobox(frame_form, values=espacios_disponibles)
        self.espacio.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="Fecha:").grid(row=1, column=0, pady=5)
        self.cal = Calendar(frame_form, selectmode='day', date_pattern='yyyy-mm-dd')
        self.cal.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Hora Inicio:").grid(row=2, column=0, pady=5)
        self.hora_inicio = ttk.Combobox(frame_form, values=[f"{h:02d}:00" for h in range(7, 22)])
        self.hora_inicio.grid(row=2, column=1, pady=5)

        ttk.Label(frame_form, text="Hora Fin:").grid(row=3, column=0, pady=5)
        self.hora_fin = ttk.Combobox(frame_form, values=[f"{h:02d}:00" for h in range(8, 23)])
        self.hora_fin.grid(row=3, column=1, pady=5)

        ttk.Label(frame_form, text="Tipo Evento:").grid(row=4, column=0, pady=5)
        self.tipo_evento = ttk.Combobox(frame_form, values=["clase", "conferencia", "reunión", "práctica", "otro"])
        self.tipo_evento.grid(row=4, column=1, pady=5)

        ttk.Label(frame_form, text="Descripción:").grid(row=5, column=0, pady=5)
        self.descripcion = tk.Text(frame_form, height=4, width=30)
        self.descripcion.grid(row=5, column=1, pady=5)

        ttk.Button(frame_form, text="Crear Reservación",
                   command=self.crear_reservacion).grid(row=6, column=0, columnspan=2, pady=20)

        # Frame derecho para filtros y lista
        frame_derecho = ttk.Frame(self.tab_reservaciones)
        frame_derecho.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Frame para filtros
        frame_filtros = ttk.LabelFrame(frame_derecho, text="Filtros", padding="10")
        frame_filtros.pack(fill="x", padx=5, pady=5)

        # Filtros
        ttk.Label(frame_filtros, text="Espacio:").grid(row=0, column=0, padx=5)
        self.filtro_espacio = ttk.Combobox(frame_filtros, values=["Todos"] + espacios_disponibles)
        self.filtro_espacio.set("Todos")
        self.filtro_espacio.grid(row=0, column=1, padx=5)
        self.filtro_espacio.bind('<<ComboboxSelected>>', lambda e: self.actualizar_lista_reservaciones())

        ttk.Label(frame_filtros, text="Tipo:").grid(row=0, column=2, padx=5)
        self.filtro_tipo = ttk.Combobox(frame_filtros,
                                        values=["Todos", "clase", "conferencia", "reunión", "práctica", "otro"])
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.grid(row=0, column=3, padx=5)
        self.filtro_tipo.bind('<<ComboboxSelected>>', lambda e: self.actualizar_lista_reservaciones())

        # Frame para lista de reservaciones
        frame_lista = ttk.LabelFrame(frame_derecho, text="Reservaciones", padding="10")
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)

        # Crear Treeview
        columns = ("ID", "Espacio", "Fecha", "Horario", "Tipo", "Estado")
        self.tree_reservaciones = ttk.Treeview(frame_lista, columns=columns, show='headings')

        # Configurar columnas
        for col in columns:
            self.tree_reservaciones.heading(col, text=col)
            self.tree_reservaciones.column(col, width=100)

        self.tree_reservaciones.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical",
                                  command=self.tree_reservaciones.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_reservaciones.configure(yscrollcommand=scrollbar.set)

        # Botón eliminar
        ttk.Button(frame_lista, text="Eliminar Reservación",
                   command=self.eliminar_reservacion).pack(pady=10)

        # Actualizar lista inicial
        self.actualizar_lista_reservaciones()

    def actualizar_lista_reservaciones(self):
        """Actualiza la lista de reservaciones aplicando los filtros actuales"""
        # Limpiar lista actual
        for item in self.tree_reservaciones.get_children():
            self.tree_reservaciones.delete(item)

        # Obtener todas las reservaciones
        reservaciones = self.controlador.obtener_reservaciones()

        # Aplicar filtros
        espacio_filtro = self.filtro_espacio.get()
        tipo_filtro = self.filtro_tipo.get()

        for reservacion in reservaciones:
            # Aplicar filtro de espacio
            if espacio_filtro != "Todos" and reservacion.espacio.nombre != espacio_filtro:
                continue

            # Aplicar filtro de tipo
            if tipo_filtro != "Todos" and reservacion.tipo_evento != tipo_filtro:
                continue

            # Añadir a la lista si pasa todos los filtros
            self.tree_reservaciones.insert('', 'end', values=(
                reservacion.id,
                reservacion.espacio.nombre,
                reservacion.horario.fecha,
                f"{reservacion.horario.hora_inicio} - {reservacion.horario.hora_fin}",
                reservacion.tipo_evento,
                reservacion.estado
            ))

    def eliminar_reservacion(self):
        """Elimina la reservación seleccionada"""
        seleccion = self.tree_reservaciones.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione una reservación para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la reservación seleccionada?"):
            item = self.tree_reservaciones.item(seleccion[0])
            id_reservacion = item['values'][0]

            if self.controlador.eliminar_reservacion(id_reservacion):
                messagebox.showinfo("Éxito", "Reservación eliminada exitosamente")
                self.actualizar_lista_reservaciones()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la reservación")

    def configurar_tab_usuarios(self):
        # Frame izquierdo para el formulario
        frame_form = ttk.LabelFrame(self.tab_usuarios, text="Nuevo Usuario", padding="10")
        frame_form.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # Elementos del formulario
        ttk.Label(frame_form, text="ID:").grid(row=0, column=0, pady=5)
        self.usuario_id = ttk.Entry(frame_form)
        self.usuario_id.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=1, column=0, pady=5)
        self.usuario_nombre = ttk.Entry(frame_form)
        self.usuario_nombre.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Tipo:").grid(row=2, column=0, pady=5)
        self.usuario_tipo = ttk.Combobox(frame_form,
                                         values=["estudiante", "profesor", "administrativo"])
        self.usuario_tipo.grid(row=2, column=1, pady=5)
        self.usuario_tipo.bind('<<ComboboxSelected>>', self.actualizar_campos_usuario)

        # Frame para campos dinámicos
        self.frame_campos_dinamicos = ttk.Frame(frame_form)
        self.frame_campos_dinamicos.grid(row=3, column=0, columnspan=2, pady=5)

        # Campos base
        ttk.Label(frame_form, text="Email:").grid(row=4, column=0, pady=5)
        self.usuario_email = ttk.Entry(frame_form)
        self.usuario_email.grid(row=4, column=1, pady=5)

        ttk.Label(frame_form, text="Unidad Académica:").grid(row=5, column=0, pady=5)
        self.usuario_unidad = ttk.Entry(frame_form)
        self.usuario_unidad.grid(row=5, column=1, pady=5)

        # Botón crear
        ttk.Button(frame_form, text="Crear Usuario",
                   command=self.crear_usuario).grid(row=6, column=0, columnspan=2, pady=20)

        # Frame derecho para lista de usuarios
        frame_lista = ttk.LabelFrame(self.tab_usuarios, text="Usuarios Registrados", padding="10")
        frame_lista.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Crear Treeview
        columns = ("ID", "Nombre", "Tipo", "Email", "Unidad Académica", "Detalles")
        self.tree_usuarios = ttk.Treeview(frame_lista, columns=columns, show='headings')

        # Configurar columnas
        for col in columns:
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=100)

        self.tree_usuarios.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical",
                                  command=self.tree_usuarios.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_usuarios.configure(yscrollcommand=scrollbar.set)

        # Botón eliminar
        ttk.Button(frame_lista, text="Eliminar Usuario Seleccionado",
                   command=self.eliminar_usuario).pack(pady=10)

        # Actualizar lista
        self.actualizar_lista_usuarios()

    def actualizar_campos_usuario(self, event=None):
        # Limpiar campos dinámicos
        for widget in self.frame_campos_dinamicos.winfo_children():
            widget.destroy()

        tipo = self.usuario_tipo.get()

        if tipo == "estudiante":
            ttk.Label(self.frame_campos_dinamicos, text="Carrera:").grid(row=0, column=0, pady=5)
            self.estudiante_carrera = ttk.Entry(self.frame_campos_dinamicos)
            self.estudiante_carrera.grid(row=0, column=1, pady=5)

            ttk.Label(self.frame_campos_dinamicos, text="Semestre:").grid(row=1, column=0, pady=5)
            self.estudiante_semestre = ttk.Entry(self.frame_campos_dinamicos)
            self.estudiante_semestre.grid(row=1, column=1, pady=5)

        elif tipo in ["profesor", "administrativo"]:
            ttk.Label(self.frame_campos_dinamicos, text="Departamento:").grid(row=0, column=0, pady=5)
            self.departamento = ttk.Entry(self.frame_campos_dinamicos)
            self.departamento.grid(row=0, column=1, pady=5)

            if tipo == "administrativo":
                ttk.Label(self.frame_campos_dinamicos, text="Cargo:").grid(row=1, column=0, pady=5)
                self.administrativo_cargo = ttk.Entry(self.frame_campos_dinamicos)
                self.administrativo_cargo.grid(row=1, column=1, pady=5)

    def crear_usuario(self):
        try:
            tipo = self.usuario_tipo.get()
            kwargs = {
                'email': self.usuario_email.get(),
                'unidad_academica': self.usuario_unidad.get()
            }

            if tipo == "estudiante":
                kwargs.update({
                    'carrera': self.estudiante_carrera.get(),
                    'semestre': self.estudiante_semestre.get()
                })
            elif tipo in ["profesor", "administrativo"]:
                kwargs['departamento'] = self.departamento.get()
                if tipo == "administrativo":
                    kwargs['cargo'] = self.administrativo_cargo.get()

            usuario = self.controlador.crear_usuario(
                self.usuario_id.get(),
                self.usuario_nombre.get(),
                tipo,
                **kwargs
            )

            if usuario:
                messagebox.showinfo("Éxito", "Usuario creado exitosamente")
                self.actualizar_lista_usuarios()
                # Limpiar campos
                self.usuario_id.delete(0, tk.END)
                self.usuario_nombre.delete(0, tk.END)
                self.usuario_tipo.set('')
                self.usuario_email.delete(0, tk.END)
                self.usuario_unidad.delete(0, tk.END)
                self.actualizar_campos_usuario()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario")

        except Exception as e:
            messagebox.showerror("Error", f"Error al crear usuario: {str(e)}")

    def eliminar_usuario(self):
        seleccion = self.tree_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar el usuario seleccionado?"):
            item = self.tree_usuarios.item(seleccion[0])
            id_usuario = item['values'][0]

            if self.controlador.eliminar_usuario(id_usuario):
                messagebox.showinfo("Éxito", "Usuario eliminado exitosamente")
                self.actualizar_lista_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario")

    def actualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)

        usuarios = self.controlador.obtener_usuarios()
        for usuario in usuarios:
            detalles = ""
            if usuario.rol == "estudiante":
                detalles = f"Carrera: {usuario.carrera}, Semestre: {usuario.semestre}"
            elif usuario.rol in ["profesor", "administrativo"]:
                detalles = f"Departamento: {usuario.departamento}"
                if usuario.rol == "administrativo":
                    detalles += f", Cargo: {usuario.cargo}"

            self.tree_usuarios.insert('', 'end', values=(
                usuario.id,
                usuario.nombre,
                usuario.rol,
                usuario.email,
                usuario.unidad_academica,
                detalles
            ))

    def configurar_tab_espacios(self):
        # Frame izquierdo para el formulario
        frame_form = ttk.LabelFrame(self.tab_espacios, text="Nuevo Espacio", padding="10")
        frame_form.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # Elementos del formulario
        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, pady=5)
        self.espacio_nombre = ttk.Entry(frame_form)
        self.espacio_nombre.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="Tipo:").grid(row=1, column=0, pady=5)
        self.espacio_tipo = ttk.Combobox(frame_form,
                                         values=["salon", "laboratorio", "salajuntas", "auditorio"])
        self.espacio_tipo.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Capacidad:").grid(row=2, column=0, pady=5)
        self.espacio_capacidad = ttk.Entry(frame_form)
        self.espacio_capacidad.grid(row=2, column=1, pady=5)

        ttk.Label(frame_form, text="Responsable ID:").grid(row=3, column=0, pady=5)
        self.espacio_responsable = ttk.Combobox(frame_form)
        self.espacio_responsable.grid(row=3, column=1, pady=5)
        self.actualizar_lista_responsables()

        # Botón crear
        ttk.Button(frame_form, text="Crear Espacio",
                   command=self.crear_espacio).grid(row=4, column=0, columnspan=2, pady=20)

        # Frame derecho para lista de espacios
        frame_lista = ttk.LabelFrame(self.tab_espacios, text="Espacios Disponibles", padding="10")
        frame_lista.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Crear Treeview
        columns = ("Nombre", "Tipo", "Capacidad", "Responsable")
        self.tree_espacios = ttk.Treeview(frame_lista, columns=columns, show='headings')

        # Configurar columnas
        for col in columns:
            self.tree_espacios.heading(col, text=col)
            self.tree_espacios.column(col, width=100)

        self.tree_espacios.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical",
                                  command=self.tree_espacios.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_espacios.configure(yscrollcommand=scrollbar.set)

        # Botón eliminar
        ttk.Button(frame_lista, text="Eliminar Espacio Seleccionado",
                   command=self.eliminar_espacio).pack(pady=10)

        # Actualizar lista
        self.actualizar_lista_espacios()

    def actualizar_lista_responsables(self):
        usuarios = self.controlador.obtener_usuarios()
        responsables = [(u.id, u.nombre) for u in usuarios
                        if u.rol in ["profesor", "administrativo"]]
        self.espacio_responsable['values'] = [f"{id} - {nombre}" for id, nombre in responsables]

    def crear_espacio(self):
        try:
            nombre = self.espacio_nombre.get()
            tipo = self.espacio_tipo.get()
            capacidad = int(self.espacio_capacidad.get())
            responsable_id = self.espacio_responsable.get().split(' - ')[0]

            if self.controlador.crear_espacio(nombre, tipo, capacidad, responsable_id):
                messagebox.showinfo("Éxito", "Espacio creado exitosamente")
                self.actualizar_lista_espacios()
                # Limpiar campos
                self.espacio_nombre.delete(0, tk.END)
                self.espacio_tipo.set('')
                self.espacio_capacidad.delete(0, tk.END)
                self.espacio_responsable.set('')
            else:
                messagebox.showerror("Error", "No se pudo crear el espacio")

        except ValueError:
            messagebox.showerror("Error", "La capacidad debe ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear espacio: {str(e)}")

    def eliminar_espacio(self):
        seleccion = self.tree_espacios.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un espacio para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar el espacio seleccionado?"):
            item = self.tree_espacios.item(seleccion[0])
            nombre_espacio = item['values'][0]

            if self.controlador.eliminar_espacio(nombre_espacio):
                messagebox.showinfo("Éxito", "Espacio eliminado exitosamente")
                self.actualizar_lista_espacios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el espacio")

    def actualizar_lista_espacios(self):
        for item in self.tree_espacios.get_children():
            self.tree_espacios.delete(item)

        espacios = self.controlador.obtener_espacios()
        for espacio in espacios:
            self.tree_espacios.insert('', 'end', values=(
                espacio.nombre,
                espacio.tipo,
                espacio.capacidad,
                "Responsable"  # Aquí podrías agregar el nombre del responsable si lo necesitas
            ))

    def crear_reservacion(self):
        try:
            espacio = self.espacio.get()
            fecha = self.cal.get_date()
            hora_inicio = self.hora_inicio.get()
            hora_fin = self.hora_fin.get()
            tipo_evento = self.tipo_evento.get()
            descripcion = self.descripcion.get("1.0", tk.END).strip()

            exito, mensaje = self.controlador.crear_reservacion(
                espacio, fecha, hora_inicio, hora_fin, tipo_evento, descripcion
            )

            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.actualizar_lista_reservaciones()
                # Limpiar campos
                self.espacio.set('')
                self.hora_inicio.set('')
                self.hora_fin.set('')
                self.tipo_evento.set('')
                self.descripcion.delete("1.0", tk.END)
            else:
                messagebox.showerror("Error", mensaje)

        except Exception as e:
            messagebox.showerror("Error", f"Error al crear reservación: {str(e)}")

if __name__ == "__main__":
    app = SistemaReservaciones()
    app.mainloop()
