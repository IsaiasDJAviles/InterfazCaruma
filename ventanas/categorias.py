"""
Módulo de Gestión de Categorías
CRUD completo para categorías de insumos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from estilos.colores import PaletaColores
from estilos.fuentes import Fuentes
from utils.db_connection import Database
from utils.posiciones import Posiciones
from ventanas.formularios import GestorFormularios
import ventanas.formularios as vf


class CategoriasCRUD:
    """Clase para gestionar las operaciones CRUD de categorías"""
    
    @staticmethod
    def obtener_todas():
        """Obtiene todas las categorías de la base de datos"""
        try:
            query = "SELECT id, nombre FROM categorias ORDER BY nombre"
            resultado = Database.execute_query(query)
            return resultado
        except Exception as e:
            print(f"Error al obtener categorías: {e}")
            return []
    
    @staticmethod
    def obtener_por_id(id_categoria):
        """Obtiene una categoría por su ID"""
        try:
            query = "SELECT id, nombre FROM categorias WHERE id = %s"
            resultado = Database.execute_query(query, (id_categoria,))
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"Error al obtener categoría: {e}")
            return None
    
    @staticmethod
    def crear(nombre):
        """Crea una nueva categoría"""
        try:
            query = "INSERT INTO categorias (nombre) VALUES (%s)"
            Database.execute_update(query, (nombre.strip(),))
            return True, "Categoría creada exitosamente"
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return False, "Ya existe una categoría con ese nombre"
            return False, f"Error al crear categoría: {e}"
    
    @staticmethod
    def actualizar(id_categoria, nombre):
        """Actualiza una categoría existente"""
        try:
            query = "UPDATE categorias SET nombre = %s WHERE id = %s"
            Database.execute_update(query, (nombre.strip(), id_categoria))
            return True, "Categoría actualizada exitosamente"
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return False, "Ya existe una categoría con ese nombre"
            return False, f"Error al actualizar categoría: {e}"
    
    @staticmethod
    def eliminar(id_categoria):
        """Elimina una categoría"""
        try:
            # Verificar si tiene insumos asociados
            query_check = "SELECT COUNT(*) FROM insumos WHERE id_categoria = %s"
            resultado = Database.execute_query(query_check, (id_categoria,))
            
            if resultado and resultado[0][0] > 0:
                return False, "No se puede eliminar: la categoría tiene insumos asociados"
            
            query = "DELETE FROM categorias WHERE id = %s"
            Database.execute_update(query, (id_categoria,))
            return True, "Categoría eliminada exitosamente"
        except Exception as e:
            return False, f"Error al eliminar categoría: {e}"
    
    @staticmethod
    def buscar(termino):
        """Busca categorías por nombre"""
        try:
            query = "SELECT id, nombre FROM categorias WHERE nombre ILIKE %s ORDER BY nombre"
            resultado = Database.execute_query(query, (f"%{termino}%",))
            return resultado
        except Exception as e:
            print(f"Error al buscar categorías: {e}")
            return []


class VentanaCategorias:
    """Ventana principal para gestión de categorías"""
    
    def __init__(self, parent):
        self.parent = parent
        self.categoria_seleccionada = None
        self.mostrar()
    
    def mostrar(self):
        """Muestra la ventana de categorías"""
        # Limpiar contenido anterior
        GestorFormularios.limpiar_contenido()
        
        # Crear frame de contenido
        vf.frame_contenido_actual = Posiciones.contenido(self.parent)
        
        # Frame principal con padding
        self.frame_principal = tk.Frame(
            vf.frame_contenido_actual,
            background=PaletaColores.COLOR_FONDO,
            padx=30,
            pady=20
        )
        self.frame_principal.pack(fill="both", expand=True)
        
        # Título de la sección
        self.crear_titulo()
        
        # Frame superior: búsqueda y botón agregar
        self.crear_barra_herramientas()
        
        # Tabla de categorías
        self.crear_tabla()
        
        # Frame de formulario (inicialmente oculto)
        self.crear_formulario()
        
        # Cargar datos
        self.cargar_categorias()
    
    def crear_titulo(self):
        """Crea el título de la sección"""
        frame_titulo = tk.Frame(
            self.frame_principal,
            background=PaletaColores.COLOR_FONDO
        )
        frame_titulo.pack(fill="x", pady=(0, 20))
        
        titulo = tk.Label(
            frame_titulo,
            text="📋 Gestión de Categorías",
            font=Fuentes.FUENTE_TITULOS,
            background=PaletaColores.COLOR_FONDO,
            foreground=PaletaColores.DORADO_CARUMA
        )
        titulo.pack(side="left")
        
        # Contador de registros
        self.label_contador = tk.Label(
            frame_titulo,
            text="",
            font=Fuentes.FUENTE_TEXTO,
            background=PaletaColores.COLOR_FONDO,
            foreground=PaletaColores.GRIS_MEDIO
        )
        self.label_contador.pack(side="right")
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas superior"""
        frame_herramientas = tk.Frame(
            self.frame_principal,
            background=PaletaColores.COLOR_FONDO
        )
        frame_herramientas.pack(fill="x", pady=(0, 15))
        
        # Frame de búsqueda
        frame_busqueda = tk.Frame(
            frame_herramientas,
            background=PaletaColores.COLOR_FONDO
        )
        frame_busqueda.pack(side="left")
        
        tk.Label(
            frame_busqueda,
            text="🔍 Buscar:",
            font=Fuentes.FUENTE_TEXTO,
            background=PaletaColores.COLOR_FONDO,
            foreground=PaletaColores.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left", padx=(0, 5))
        
        self.entrada_busqueda = GestorFormularios.crear_entrada(frame_busqueda, ancho=30)
        self.entrada_busqueda.pack(side="left", padx=(0, 10))
        self.entrada_busqueda.bind("<KeyRelease>", self.buscar_categorias)
        
        # Botón limpiar búsqueda
        btn_limpiar = tk.Button(
            frame_busqueda,
            text="✕",
            font=Fuentes.FUENTE_TEXTO,
            background=PaletaColores.GRIS_CLARO,
            foreground=PaletaColores.GRIS_OSCURO,
            relief="flat",
            cursor="hand2",
            command=self.limpiar_busqueda
        )
        btn_limpiar.pack(side="left")
        
        # Frame de botones de acción
        frame_acciones = tk.Frame(
            frame_herramientas,
            background=PaletaColores.COLOR_FONDO
        )
        frame_acciones.pack(side="right")
        
        # Botón agregar
        self.btn_agregar = GestorFormularios.crear_boton(
            frame_acciones,
            "➕ Nueva Categoría",
            self.mostrar_formulario_nuevo,
            ancho=18
        )
        self.btn_agregar.pack(side="left", padx=5)
        
        # Botón editar
        self.btn_editar = GestorFormularios.crear_boton(
            frame_acciones,
            "✏️ Editar",
            self.mostrar_formulario_editar,
            ancho=12
        )
        self.btn_editar.pack(side="left", padx=5)
        self.btn_editar.config(state="disabled")
        
        # Botón eliminar
        self.btn_eliminar = tk.Button(
            frame_acciones,
            text="🗑️ Eliminar",
            font=Fuentes.FUENTE_BOTONES,
            background=PaletaColores.COLOR_ERROR,
            foreground=PaletaColores.BLANCO,
            activebackground="#c82333",
            activeforeground=PaletaColores.BLANCO,
            relief="flat",
            cursor="hand2",
            width=12,
            pady=10,
            command=self.eliminar_categoria
        )
        self.btn_eliminar.pack(side="left", padx=5)
        self.btn_eliminar.config(state="disabled")
    
    def crear_tabla(self):
        """Crea la tabla de categorías"""
        # Frame contenedor de la tabla
        frame_tabla = tk.Frame(
            self.frame_principal,
            background=PaletaColores.COLOR_FONDO
        )
        frame_tabla.pack(fill="both", expand=True, pady=(0, 15))
        
        # Configurar estilo del Treeview
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Categorias.Treeview",
            background=PaletaColores.BLANCO,
            foreground=PaletaColores.COLOR_TEXTO_PRINCIPAL,
            fieldbackground=PaletaColores.BLANCO,
            rowheight=35,
            font=Fuentes.FUENTE_TEXTO
        )
        
        style.configure(
            "Categorias.Treeview.Heading",
            background=PaletaColores.DORADO_CARUMA,
            foreground=PaletaColores.NEGRO_CARUMA,
            font=Fuentes.FUENTE_BOTONES,
            padding=10
        )
        
        style.map(
            "Categorias.Treeview",
            background=[("selected", PaletaColores.DORADO_CLARO)],
            foreground=[("selected", PaletaColores.NEGRO_CARUMA)]
        )
        
        # Crear Treeview
        columnas = ("id", "nombre")
        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            style="Categorias.Treeview",
            selectmode="browse"
        )
        
        # Configurar columnas
        self.tabla.heading("id", text="ID", anchor="center")
        self.tabla.heading("nombre", text="Nombre de Categoría", anchor="w")
        
        self.tabla.column("id", width=80, minwidth=60, anchor="center")
        self.tabla.column("nombre", width=400, minwidth=200, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            frame_tabla,
            orient="vertical",
            command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar tabla y scrollbar
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Eventos
        self.tabla.bind("<<TreeviewSelect>>", self.on_seleccionar)
        self.tabla.bind("<Double-1>", lambda e: self.mostrar_formulario_editar())
    
    def crear_formulario(self):
        """Crea el frame del formulario (inicialmente oculto)"""
        self.frame_formulario = tk.Frame(
            self.frame_principal,
            background=PaletaColores.GRIS_CLARO,
            padx=20,
            pady=15
        )
        
        # Título del formulario
        self.label_titulo_form = tk.Label(
            self.frame_formulario,
            text="Nueva Categoría",
            font=Fuentes.FUENTE_TEXTO_GRANDE,
            background=PaletaColores.GRIS_CLARO,
            foreground=PaletaColores.DORADO_CARUMA
        )
        self.label_titulo_form.pack(anchor="w", pady=(0, 10))
        
        # Frame para campos
        frame_campos = tk.Frame(
            self.frame_formulario,
            background=PaletaColores.GRIS_CLARO
        )
        frame_campos.pack(fill="x")
        
        # Campo nombre
        tk.Label(
            frame_campos,
            text="Nombre:",
            font=Fuentes.FUENTE_TEXTO,
            background=PaletaColores.GRIS_CLARO,
            foreground=PaletaColores.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left", padx=(0, 10))
        
        self.entrada_nombre = tk.Entry(
            frame_campos,
            font=Fuentes.FUENTE_TEXTO,
            width=40,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=PaletaColores.GRIS_CLARO,
            highlightcolor=PaletaColores.DORADO_CARUMA
        )
        self.entrada_nombre.pack(side="left", padx=(0, 20))
        self.entrada_nombre.bind("<Return>", lambda e: self.guardar_categoria())
        
        # Botones del formulario
        frame_botones_form = tk.Frame(
            frame_campos,
            background=PaletaColores.GRIS_CLARO
        )
        frame_botones_form.pack(side="left")
        
        self.btn_guardar = tk.Button(
            frame_botones_form,
            text="💾 Guardar",
            font=Fuentes.FUENTE_BOTONES,
            background=PaletaColores.COLOR_EXITO,
            foreground=PaletaColores.BLANCO,
            activebackground="#218838",
            activeforeground=PaletaColores.BLANCO,
            relief="flat",
            cursor="hand2",
            width=12,
            pady=8,
            command=self.guardar_categoria
        )
        self.btn_guardar.pack(side="left", padx=5)
        
        btn_cancelar = tk.Button(
            frame_botones_form,
            text="❌ Cancelar",
            font=Fuentes.FUENTE_BOTONES,
            background=PaletaColores.GRIS_MEDIO,
            foreground=PaletaColores.BLANCO,
            activebackground=PaletaColores.GRIS_OSCURO,
            activeforeground=PaletaColores.BLANCO,
            relief="flat",
            cursor="hand2",
            width=12,
            pady=8,
            command=self.ocultar_formulario
        )
        btn_cancelar.pack(side="left", padx=5)
        
        # Variable para saber si estamos editando
        self.editando = False
        self.id_editando = None
    
    def cargar_categorias(self, categorias=None):
        """Carga las categorías en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Obtener categorías si no se proporcionaron
        if categorias is None:
            categorias = CategoriasCRUD.obtener_todas()
        
        # Insertar en tabla
        for categoria in categorias:
            self.tabla.insert("", "end", values=categoria)
        
        # Actualizar contador
        total = len(categorias)
        texto = f"{total} categoría{'s' if total != 1 else ''}"
        self.label_contador.config(text=texto)
        
        # Resetear selección
        self.categoria_seleccionada = None
        self.btn_editar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
    
    def on_seleccionar(self, event):
        """Maneja el evento de selección en la tabla"""
        seleccion = self.tabla.selection()
        if seleccion:
            item = self.tabla.item(seleccion[0])
            self.categoria_seleccionada = {
                "id": item["values"][0],
                "nombre": item["values"][1]
            }
            self.btn_editar.config(state="normal")
            self.btn_eliminar.config(state="normal")
        else:
            self.categoria_seleccionada = None
            self.btn_editar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
    
    def mostrar_formulario_nuevo(self):
        """Muestra el formulario para nueva categoría"""
        self.editando = False
        self.id_editando = None
        self.label_titulo_form.config(text="➕ Nueva Categoría")
        self.entrada_nombre.delete(0, tk.END)
        self.frame_formulario.pack(fill="x", pady=(0, 15))
        self.entrada_nombre.focus_set()
    
    def mostrar_formulario_editar(self):
        """Muestra el formulario para editar categoría"""
        if not self.categoria_seleccionada:
            messagebox.showwarning(
                "Selección requerida",
                "Por favor, seleccione una categoría para editar"
            )
            return
        
        self.editando = True
        self.id_editando = self.categoria_seleccionada["id"]
        self.label_titulo_form.config(text="✏️ Editar Categoría")
        self.entrada_nombre.delete(0, tk.END)
        self.entrada_nombre.insert(0, self.categoria_seleccionada["nombre"])
        self.frame_formulario.pack(fill="x", pady=(0, 15))
        self.entrada_nombre.focus_set()
        self.entrada_nombre.select_range(0, tk.END)
    
    def ocultar_formulario(self):
        """Oculta el formulario"""
        self.frame_formulario.pack_forget()
        self.entrada_nombre.delete(0, tk.END)
        self.editando = False
        self.id_editando = None
    
    def guardar_categoria(self):
        """Guarda la categoría (crear o actualizar)"""
        nombre = self.entrada_nombre.get().strip()
        
        # Validación
        if not nombre:
            messagebox.showwarning(
                "Campo requerido",
                "Por favor, ingrese el nombre de la categoría"
            )
            self.entrada_nombre.focus_set()
            return
        
        if len(nombre) < 2:
            messagebox.showwarning(
                "Nombre muy corto",
                "El nombre debe tener al menos 2 caracteres"
            )
            self.entrada_nombre.focus_set()
            return
        
        if len(nombre) > 50:
            messagebox.showwarning(
                "Nombre muy largo",
                "El nombre no puede exceder 50 caracteres"
            )
            self.entrada_nombre.focus_set()
            return
        
        # Crear o actualizar
        if self.editando:
            exito, mensaje = CategoriasCRUD.actualizar(self.id_editando, nombre)
        else:
            exito, mensaje = CategoriasCRUD.crear(nombre)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.ocultar_formulario()
            self.cargar_categorias()
        else:
            messagebox.showerror("Error", mensaje)
            self.entrada_nombre.focus_set()
    
    def eliminar_categoria(self):
        """Elimina la categoría seleccionada"""
        if not self.categoria_seleccionada:
            messagebox.showwarning(
                "Selección requerida",
                "Por favor, seleccione una categoría para eliminar"
            )
            return
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la categoría '{self.categoria_seleccionada['nombre']}'?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if respuesta:
            exito, mensaje = CategoriasCRUD.eliminar(self.categoria_seleccionada["id"])
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_categorias()
            else:
                messagebox.showerror("Error", mensaje)
    
    def buscar_categorias(self, event=None):
        """Busca categorías por término"""
        termino = self.entrada_busqueda.get().strip()
        
        if termino:
            categorias = CategoriasCRUD.buscar(termino)
        else:
            categorias = CategoriasCRUD.obtener_todas()
        
        self.cargar_categorias(categorias)
    
    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda"""
        self.entrada_busqueda.delete(0, tk.END)
        self.cargar_categorias()


def abrir_ventana_categorias(parent):
    """Función para abrir la ventana de categorías desde el menú principal"""
    return VentanaCategorias(parent)