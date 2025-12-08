"""
Módulo de Gestión de Servicios - CARUMA
CRUD completo para servicios con relación a insumos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from estilos.colores import PaletaColores
from estilos.fuentes import Fuentes
from utils.db_connection import Database
from utils.posiciones import Posiciones
from ventanas.formularios import GestorFormularios
import ventanas.formularios as vf


class ServiciosCRUD:
    """Operaciones CRUD de servicios"""
    
    @staticmethod
    def obtener_todos():
        try:
            query = """
                SELECT s.id, s.nombre,
                    (SELECT COUNT(*) FROM servicio_insumo si WHERE si.id_servicio = s.id) as num_insumos
                FROM servicios s ORDER BY s.nombre
            """
            return Database.ejecutar_query(query)
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def obtener_por_id(id_servicio):
        try:
            query = "SELECT id, nombre FROM servicios WHERE id = ?"
            resultado = Database.ejecutar_query(query, (id_servicio,))
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    @staticmethod
    def crear(nombre):
        try:
            query = "INSERT INTO servicios (nombre) VALUES (?)"
            Database.ejecutar_comando(query, (nombre.strip(),))
            return True, "Servicio creado exitosamente"
        except Exception as e:
            if "unique" in str(e).lower():
                return False, "Ya existe un servicio con ese nombre"
            return False, f"Error: {e}"
    
    @staticmethod
    def actualizar(id_servicio, nombre):
        try:
            query = "UPDATE servicios SET nombre = ? WHERE id = ?"
            Database.ejecutar_comando(query, (nombre.strip(), id_servicio))
            return True, "Servicio actualizado exitosamente"
        except Exception as e:
            if "unique" in str(e).lower():
                return False, "Ya existe un servicio con ese nombre"
            return False, f"Error: {e}"
    
    @staticmethod
    def eliminar(id_servicio):
        try:
            # Las relaciones se eliminan en cascada por la FK
            query = "DELETE FROM servicios WHERE id = ?"
            Database.ejecutar_comando(query, (id_servicio,))
            return True, "Servicio eliminado exitosamente"
        except Exception as e:
            return False, f"Error: {e}"
    
    @staticmethod
    def buscar(termino):
        try:
            query = """
                SELECT s.id, s.nombre,
                    (SELECT COUNT(*) FROM servicio_insumo si WHERE si.id_servicio = s.id) as num_insumos
                FROM servicios s 
                WHERE s.nombre LIKE ? COLLATE NOCASE 
                ORDER BY s.nombre
            """
            return Database.ejecutar_query(query, (f"%{termino}%",))
        except Exception as e:
            print("Error búsqueda:", e)
            return []



class ServicioInsumoCRUD:
    """Operaciones para la relación servicio-insumo"""
    
    @staticmethod
    def obtener_insumos_servicio(id_servicio):
        """Obtiene los insumos asociados a un servicio"""
        try:
            query = """
                SELECT si.id, i.id as id_insumo, i.nombre, 
                       si.piezas_por_servicio, si.contenido_por_servicio, si.unidad_contenido
                FROM servicio_insumo si
                JOIN insumos i ON si.id_insumo = i.id
                WHERE si.id_servicio = ?
                ORDER BY i.nombre
            """
            return Database.ejecutar_query(query, (id_servicio,))
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def obtener_insumos_disponibles():
        """Obtiene todos los insumos disponibles para agregar"""
        try:
            query = "SELECT id, nombre, unidad_contenido FROM insumos ORDER BY nombre"
            return Database.ejecutar_query(query)
        except:
            return []
    
    @staticmethod
    def agregar_insumo(id_servicio, id_insumo, piezas, contenido, unidad):
        """Agrega un insumo a un servicio"""
        try:
            # Verificar si ya existe la relación
            check = Database.ejecutar_query(
                "SELECT id FROM servicio_insumo WHERE id_servicio=? AND id_insumo=?",
                (id_servicio, id_insumo))
            if check:
                return False, "Este insumo ya está agregado al servicio"
            
            query = """
                INSERT INTO servicio_insumo (id_servicio, id_insumo, piezas_por_servicio, 
                                             contenido_por_servicio, unidad_contenido)
                VALUES (?, ?, ?, ?, ?)
            """
            Database.ejecutar_comando(query, (id_servicio, id_insumo, piezas or None,
                                            contenido or None, unidad or None))
            return True, "Insumo agregado al servicio"
        except Exception as e:
            return False, f"Error: {e}"
    
    @staticmethod
    def actualizar_insumo(id_relacion, piezas, contenido, unidad):
        """Actualiza la cantidad de insumo en un servicio"""
        try:
            query = """
                UPDATE servicio_insumo SET piezas_por_servicio=?, 
                       contenido_por_servicio=?, unidad_contenido=?
                WHERE id = ?
            """
            Database.ejecutar_comando(query, (piezas or None, contenido or None, unidad or None, id_relacion))
            return True, "Cantidad actualizada"
        except Exception as e:
            return False, f"Error: {e}"
    
    @staticmethod
    def eliminar_insumo(id_relacion):
        """Elimina un insumo de un servicio"""
        try:
            query = "DELETE FROM servicio_insumo WHERE id = ?"
            Database.ejecutar_comando(query, (id_relacion,))
            return True, "Insumo eliminado del servicio"
        except Exception as e:
            return False, f"Error: {e}"


class VentanaServicios:
    """Ventana de gestión de servicios"""
    
    def __init__(self, parent):
        self.parent = parent
        self.servicio_sel = None
        self.insumo_sel = None
        self.editando = False
        self.id_editando = None
        self.mostrar()
    
    def mostrar(self):
        GestorFormularios.limpiar_contenido()
        vf.frame_contenido_actual = Posiciones.contenido(self.parent)
        
        self.frame_principal = tk.Frame(vf.frame_contenido_actual, bg=PaletaColores.COLOR_FONDO, padx=20, pady=15)
        self.frame_principal.pack(fill="both", expand=True)
        
        self.crear_titulo()
        self.crear_panel_servicios()
        self.crear_panel_insumos()
        self.cargar_servicios()
    
    def crear_titulo(self):
        frame = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame.pack(fill="x", pady=(0, 15))
        tk.Label(frame, text="Gestión de Servicios", font=Fuentes.FUENTE_TITULOS,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(side="left")
    
    def crear_panel_servicios(self):
        """Panel izquierdo: Lista de servicios"""
        # Frame contenedor con borde
        self.frame_servicios = tk.LabelFrame(
            self.frame_principal, text=" Servicios ", font=Fuentes.FUENTE_TEXTO_GRANDE,
            bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA, padx=10, pady=10)
        self.frame_servicios.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Barra de herramientas
        frame_tools = tk.Frame(self.frame_servicios, bg=PaletaColores.COLOR_FONDO)
        frame_tools.pack(fill="x", pady=(0, 10))
        
        tk.Label(frame_tools, text='', bg=PaletaColores.COLOR_FONDO).pack(side="left")
        self.ent_buscar = tk.Entry(frame_tools, font=Fuentes.FUENTE_TEXTO, width=20, relief="solid", bd=1)
        self.ent_buscar.pack(side="left", padx=(3, 10))
        self.ent_buscar.bind("<KeyRelease>", self.buscar)
        
        self.btn_nuevo = tk.Button(frame_tools, text="Nuevo", font=Fuentes.FUENTE_MENU,
                                    bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                                    padx=10, command=self.form_nuevo)
        self.btn_nuevo.pack(side="left", padx=2)
        
        self.btn_editar = tk.Button(frame_tools, text="Editar", font=Fuentes.FUENTE_MENU,
                                     bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                                     padx=8, state="disabled", command=self.form_editar)
        self.btn_editar.pack(side="left", padx=2)
        
        self.btn_eliminar = tk.Button(frame_tools, text="X", font=Fuentes.FUENTE_MENU,
                                       bg=PaletaColores.COLOR_ERROR, fg=PaletaColores.BLANCO,
                                       relief="flat", cursor="hand2", padx=8,
                                       state="disabled", command=self.eliminar_servicio)
        self.btn_eliminar.pack(side="left", padx=2)
        
        # Contador
        self.lbl_contador = tk.Label(frame_tools, text="+", font=Fuentes.FUENTE_MENU,
                                      bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.GRIS_MEDIO)
        self.lbl_contador.pack(side="right")
        
        # Tabla de servicios
        frame_tabla = tk.Frame(self.frame_servicios, bg=PaletaColores.COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, pady=(0, 10))
        
        style = ttk.Style()
        style.configure("Serv.Treeview", rowheight=28, font=Fuentes.FUENTE_TEXTO)
        style.configure("Serv.Treeview.Heading", background=PaletaColores.DORADO_CARUMA,
                        font=Fuentes.FUENTE_BOTONES, padding=5)
        style.map("Serv.Treeview", background=[("selected", PaletaColores.DORADO_CLARO)])
        
        cols = ("id", "nombre", "insumos")
        self.tabla_serv = ttk.Treeview(frame_tabla, columns=cols, show="headings",
                                        style="Serv.Treeview", height=12)
        
        self.tabla_serv.heading("id", text="ID")
        self.tabla_serv.heading("nombre", text="Nombre del Servicio")
        self.tabla_serv.heading("insumos", text="Insumos")
        
        self.tabla_serv.column("id", width=40, anchor="center")
        self.tabla_serv.column("nombre", width=200, anchor="w")
        self.tabla_serv.column("insumos", width=60, anchor="center")
        
        sb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_serv.yview)
        self.tabla_serv.configure(yscrollcommand=sb.set)
        self.tabla_serv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tabla_serv.bind("<<TreeviewSelect>>", self.on_select_servicio)
        self.tabla_serv.bind("<Double-1>", lambda e: self.form_editar())
        
        # Formulario de servicio
        self.frame_form = tk.Frame(self.frame_servicios, bg=PaletaColores.GRIS_CLARO, padx=10, pady=10)
        
        self.lbl_titulo_form = tk.Label(self.frame_form, text="Nuevo Servicio",
                                         font=Fuentes.FUENTE_TEXTO, bg=PaletaColores.GRIS_CLARO,
                                         fg=PaletaColores.DORADO_CARUMA)
        self.lbl_titulo_form.pack(anchor="w")
        
        frame_campos = tk.Frame(self.frame_form, bg=PaletaColores.GRIS_CLARO)
        frame_campos.pack(fill="x", pady=(5, 0))
        
        tk.Label(frame_campos, text="Nombre:", bg=PaletaColores.GRIS_CLARO).pack(side="left")
        self.ent_nombre = tk.Entry(frame_campos, font=Fuentes.FUENTE_TEXTO, width=25, relief="solid", bd=1)
        self.ent_nombre.pack(side="left", padx=(5, 10))
        self.ent_nombre.bind("<Return>", lambda e: self.guardar_servicio())
        
        tk.Button(frame_campos, text="OK", font=Fuentes.FUENTE_BOTONES, bg=PaletaColores.COLOR_EXITO,
                  fg=PaletaColores.BLANCO, relief="flat", padx=8,
                  command=self.guardar_servicio).pack(side="left", padx=2)
        tk.Button(frame_campos, text="Cancel", font=Fuentes.FUENTE_BOTONES, bg=PaletaColores.GRIS_MEDIO,
                  fg=PaletaColores.BLANCO, relief="flat", padx=8,
                  command=self.ocultar_form).pack(side="left", padx=2)
    
    def crear_panel_insumos(self):
        """Panel derecho: Insumos del servicio seleccionado"""
        self.frame_insumos = tk.LabelFrame(
            self.frame_principal, text=" Insumos del Servicio ", font=Fuentes.FUENTE_TEXTO_GRANDE,
            bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA, padx=10, pady=10)
        self.frame_insumos.pack(side="right", fill="both", expand=True)
        
        # Etiqueta del servicio seleccionado
        self.lbl_servicio_sel = tk.Label(self.frame_insumos, text="Seleccione un servicio",
                                          font=Fuentes.FUENTE_TEXTO, bg=PaletaColores.COLOR_FONDO,
                                          fg=PaletaColores.GRIS_MEDIO)
        self.lbl_servicio_sel.pack(anchor="w", pady=(0, 10))
        
        # Botones de acción
        frame_btns = tk.Frame(self.frame_insumos, bg=PaletaColores.COLOR_FONDO)
        frame_btns.pack(fill="x", pady=(0, 10))
        
        self.btn_agregar_ins = tk.Button(frame_btns, text="Agregar Insumo", font=Fuentes.FUENTE_MENU,
                                          bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                                          padx=10, state="disabled", command=self.mostrar_agregar_insumo)
        self.btn_agregar_ins.pack(side="left", padx=(0, 5))
        
        self.btn_editar_ins = tk.Button(frame_btns, text="Editar", font=Fuentes.FUENTE_MENU,
                                         bg=PaletaColores.COLOR_INFO, fg=PaletaColores.BLANCO,
                                         relief="flat", cursor="hand2", padx=10,
                                         state="disabled", command=self.editar_insumo_servicio)
        self.btn_editar_ins.pack(side="left", padx=5)
        
        self.btn_quitar_ins = tk.Button(frame_btns, text="Quitar", font=Fuentes.FUENTE_MENU,
                                         bg=PaletaColores.COLOR_ERROR, fg=PaletaColores.BLANCO,
                                         relief="flat", cursor="hand2", padx=10,
                                         state="disabled", command=self.quitar_insumo_servicio)
        self.btn_quitar_ins.pack(side="left", padx=5)
        
        # Tabla de insumos
        frame_tabla_ins = tk.Frame(self.frame_insumos, bg=PaletaColores.COLOR_FONDO)
        frame_tabla_ins.pack(fill="both", expand=True)
        
        cols = ("id", "insumo", "piezas", "contenido", "unidad")
        self.tabla_ins = ttk.Treeview(frame_tabla_ins, columns=cols, show="headings",
                                       style="Serv.Treeview", height=12)
        
        self.tabla_ins.heading("id", text="ID")
        self.tabla_ins.heading("insumo", text="Insumo")
        self.tabla_ins.heading("piezas", text="Piezas")
        self.tabla_ins.heading("contenido", text="Contenido")
        self.tabla_ins.heading("unidad", text="Unidad")
        
        self.tabla_ins.column("id", width=0, stretch=False)  # Oculto
        self.tabla_ins.column("insumo", width=180, anchor="w")
        self.tabla_ins.column("piezas", width=60, anchor="center")
        self.tabla_ins.column("contenido", width=70, anchor="center")
        self.tabla_ins.column("unidad", width=60, anchor="center")
        
        sb_ins = ttk.Scrollbar(frame_tabla_ins, orient="vertical", command=self.tabla_ins.yview)
        self.tabla_ins.configure(yscrollcommand=sb_ins.set)
        self.tabla_ins.pack(side="left", fill="both", expand=True)
        sb_ins.pack(side="right", fill="y")
        
        self.tabla_ins.bind("<<TreeviewSelect>>", self.on_select_insumo)
        self.tabla_ins.bind("<Double-1>", lambda e: self.editar_insumo_servicio())
    
    def cargar_servicios(self, datos=None):
        for i in self.tabla_serv.get_children():
            self.tabla_serv.delete(i)
        
        if datos is None:
            datos = ServiciosCRUD.obtener_todos()
        
        for s in datos:
            self.tabla_serv.insert("", "end", values=(s[0], s[1], s[2]))
        
        self.lbl_contador.config(text=f"{len(datos)} servicio{'s' if len(datos)!=1 else ''}")
        self.servicio_sel = None
        self.btn_editar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
        self.btn_agregar_ins.config(state="disabled")
        self.lbl_servicio_sel.config(text="Seleccione un servicio")
        self.limpiar_tabla_insumos()
    
    def limpiar_tabla_insumos(self):
        for i in self.tabla_ins.get_children():
            self.tabla_ins.delete(i)
        self.insumo_sel = None
        self.btn_editar_ins.config(state="disabled")
        self.btn_quitar_ins.config(state="disabled")
    
    def cargar_insumos_servicio(self):
        self.limpiar_tabla_insumos()
        if not self.servicio_sel:
            return
        
        insumos = ServicioInsumoCRUD.obtener_insumos_servicio(self.servicio_sel["id"])
        for ins in insumos:
            self.tabla_ins.insert("", "end", values=(
                ins[0],  # id relación
                ins[2],  # nombre insumo
                ins[3] or "",  # piezas
                ins[4] or "",  # contenido
                ins[5] or ""   # unidad
            ))
    
    def on_select_servicio(self, e):
        sel = self.tabla_serv.selection()
        if sel:
            v = self.tabla_serv.item(sel[0])["values"]
            self.servicio_sel = {"id": v[0], "nombre": v[1]}
            self.btn_editar.config(state="normal")
            self.btn_eliminar.config(state="normal")
            self.btn_agregar_ins.config(state="normal")
            self.lbl_servicio_sel.config(text=f"{v[1]}", fg=PaletaColores.DORADO_CARUMA)
            self.cargar_insumos_servicio()
        else:
            self.servicio_sel = None
            self.btn_editar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_agregar_ins.config(state="disabled")
    
    def on_select_insumo(self, e):
        sel = self.tabla_ins.selection()
        if sel:
            v = self.tabla_ins.item(sel[0])["values"]
            self.insumo_sel = {"id": v[0], "nombre": v[1], "piezas": v[2], "contenido": v[3], "unidad": v[4]}
            self.btn_editar_ins.config(state="normal")
            self.btn_quitar_ins.config(state="normal")
        else:
            self.insumo_sel = None
            self.btn_editar_ins.config(state="disabled")
            self.btn_quitar_ins.config(state="disabled")
    
    def form_nuevo(self):
        self.editando = False
        self.id_editando = None
        self.lbl_titulo_form.config(text="Nuevo Servicio")
        self.ent_nombre.delete(0, tk.END)
        self.frame_form.pack(fill="x", pady=(0, 5))
        self.ent_nombre.focus_set()
    
    def form_editar(self):
        if not self.servicio_sel:
            messagebox.showwarning("Aviso", "Seleccione un servicio")
            return
        
        self.editando = True
        self.id_editando = self.servicio_sel["id"]
        self.lbl_titulo_form.config(text="Editar Servicio")
        self.ent_nombre.delete(0, tk.END)
        self.ent_nombre.insert(0, self.servicio_sel["nombre"])
        self.frame_form.pack(fill="x", pady=(0, 5))
        self.ent_nombre.focus_set()
        self.ent_nombre.select_range(0, tk.END)
    
    def ocultar_form(self):
        self.frame_form.pack_forget()
        self.editando = False
        self.id_editando = None
    
    def guardar_servicio(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre or len(nombre) < 2:
            messagebox.showwarning("Error", "Nombre inválido (mín. 2 caracteres)")
            return
        
        if self.editando:
            ok, msg = ServiciosCRUD.actualizar(self.id_editando, nombre)
        else:
            ok, msg = ServiciosCRUD.crear(nombre)
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.ocultar_form()
            self.cargar_servicios()
        else:
            messagebox.showerror("Error", msg)
    
    def eliminar_servicio(self):
        if not self.servicio_sel:
            return
        if messagebox.askyesno("Confirmar", 
            f"¿Eliminar el servicio '{self.servicio_sel['nombre']}'?\n\n"
            "También se eliminarán las relaciones con insumos."):
            ok, msg = ServiciosCRUD.eliminar(self.servicio_sel["id"])
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_servicios()
            else:
                messagebox.showerror("Error", msg)
    
    def buscar(self, e=None):
        t = self.ent_buscar.get().strip()
        self.cargar_servicios(ServiciosCRUD.buscar(t) if t else None)
    
    def mostrar_agregar_insumo(self):
        """Muestra diálogo para agregar insumo al servicio"""
        if not self.servicio_sel:
            return
        
        insumos_disponibles = ServicioInsumoCRUD.obtener_insumos_disponibles()
        if not insumos_disponibles:
            messagebox.showwarning("Aviso", "No hay insumos registrados.\nPrimero agregue insumos en el módulo correspondiente.")
            return
        
        dlg = tk.Toplevel(self.parent)
        dlg.title("Agregar Insumo al Servicio")
        dlg.geometry("420x280")
        dlg.configure(bg=PaletaColores.COLOR_FONDO)
        dlg.resizable(False, False)
        dlg.transient(self.parent)
        dlg.grab_set()
        
        x = self.parent.winfo_x() + self.parent.winfo_width()//2 - 210
        y = self.parent.winfo_y() + self.parent.winfo_height()//2 - 140
        dlg.geometry(f"+{x}+{y}")
        
        tk.Label(dlg, text=f" {self.servicio_sel['nombre']}", font=Fuentes.FUENTE_TEXTO_GRANDE,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(pady=(15, 10))
        
        # Frame de campos
        frame_campos = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_campos.pack(fill="x", padx=20, pady=10)
        
        # Insumo
        tk.Label(frame_campos, text="Insumo:", bg=PaletaColores.COLOR_FONDO).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        cmb_insumo = ttk.Combobox(frame_campos, state="readonly", width=28)
        cmb_insumo['values'] = [f"{i[0]} - {i[1]}" for i in insumos_disponibles]
        cmb_insumo.grid(row=0, column=1, sticky="w", pady=5)
        if insumos_disponibles:
            cmb_insumo.current(0)
        
        # Piezas por servicio
        tk.Label(frame_campos, text="Piezas/servicio:", bg=PaletaColores.COLOR_FONDO).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ent_piezas = tk.Entry(frame_campos, width=10, relief="solid", bd=1)
        ent_piezas.grid(row=1, column=1, sticky="w", pady=5)
        
        # Contenido por servicio
        tk.Label(frame_campos, text="Contenido/servicio:", bg=PaletaColores.COLOR_FONDO).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ent_contenido = tk.Entry(frame_campos, width=10, relief="solid", bd=1)
        ent_contenido.grid(row=2, column=1, sticky="w", pady=5)
        
        # Unidad
        tk.Label(frame_campos, text="Unidad:", bg=PaletaColores.COLOR_FONDO).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        cmb_unidad = ttk.Combobox(frame_campos, values=["kg", "g", "L", "ml", "pza"], width=8)
        cmb_unidad.grid(row=3, column=1, sticky="w", pady=5)
        
        # Info
        tk.Label(frame_campos, text="(Ingrese piezas O contenido según aplique)",
                 font=("Segoe UI", 9), bg=PaletaColores.COLOR_FONDO,
                 fg=PaletaColores.GRIS_MEDIO).grid(row=4, column=0, columnspan=2, pady=(5, 0))
        
        # Botones
        frame_btns = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_btns.pack(pady=20)
        
        def agregar():
            if cmb_insumo.current() < 0:
                messagebox.showwarning("Error", "Seleccione un insumo")
                return
            
            id_insumo = insumos_disponibles[cmb_insumo.current()][0]
            
            piezas = None
            if ent_piezas.get().strip():
                try:
                    piezas = float(ent_piezas.get())
                    if piezas < 0: raise ValueError()
                except:
                    messagebox.showwarning("Error", "Piezas inválidas")
                    return
            
            contenido = None
            if ent_contenido.get().strip():
                try:
                    contenido = float(ent_contenido.get())
                    if contenido < 0: raise ValueError()
                except:
                    messagebox.showwarning("Error", "Contenido inválido")
                    return
            
            unidad = cmb_unidad.get().strip()
            
            ok, msg = ServicioInsumoCRUD.agregar_insumo(
                self.servicio_sel["id"], id_insumo, piezas, contenido, unidad)
            
            if ok:
                dlg.destroy()
                self.cargar_insumos_servicio()
                self.cargar_servicios()  # Actualizar contador
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(frame_btns, text="Agregar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.COLOR_EXITO, fg=PaletaColores.BLANCO,
                  relief="flat", padx=15, command=agregar).pack(side="left", padx=5)
        tk.Button(frame_btns, text="Cancelar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.GRIS_MEDIO, fg=PaletaColores.BLANCO,
                  relief="flat", padx=15, command=dlg.destroy).pack(side="left", padx=5)
    
    def editar_insumo_servicio(self):
        """Edita la cantidad de insumo en el servicio"""
        if not self.insumo_sel:
            messagebox.showwarning("Aviso", "Seleccione un insumo")
            return
        
        dlg = tk.Toplevel(self.parent)
        dlg.title("Editar Cantidad")
        dlg.geometry("350x220")
        dlg.configure(bg=PaletaColores.COLOR_FONDO)
        dlg.resizable(False, False)
        dlg.transient(self.parent)
        dlg.grab_set()
        
        x = self.parent.winfo_x() + self.parent.winfo_width()//2 - 175
        y = self.parent.winfo_y() + self.parent.winfo_height()//2 - 110
        dlg.geometry(f"+{x}+{y}")
        
        tk.Label(dlg, text=f" {self.insumo_sel['nombre']}", font=Fuentes.FUENTE_TEXTO_GRANDE,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(pady=(15, 10))
        
        frame_campos = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_campos.pack(fill="x", padx=30, pady=10)
        
        tk.Label(frame_campos, text="Piezas/servicio:", bg=PaletaColores.COLOR_FONDO).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ent_piezas = tk.Entry(frame_campos, width=10, relief="solid", bd=1)
        ent_piezas.grid(row=0, column=1, sticky="w", pady=5)
        if self.insumo_sel["piezas"]:
            ent_piezas.insert(0, str(self.insumo_sel["piezas"]))
        
        tk.Label(frame_campos, text="Contenido/servicio:", bg=PaletaColores.COLOR_FONDO).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ent_contenido = tk.Entry(frame_campos, width=10, relief="solid", bd=1)
        ent_contenido.grid(row=1, column=1, sticky="w", pady=5)
        if self.insumo_sel["contenido"]:
            ent_contenido.insert(0, str(self.insumo_sel["contenido"]))
        
        tk.Label(frame_campos, text="Unidad:", bg=PaletaColores.COLOR_FONDO).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        cmb_unidad = ttk.Combobox(frame_campos, values=["kg", "g", "L", "ml", "pza"], width=8)
        cmb_unidad.grid(row=2, column=1, sticky="w", pady=5)
        if self.insumo_sel["unidad"]:
            cmb_unidad.set(self.insumo_sel["unidad"])
        
        frame_btns = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_btns.pack(pady=15)
        
        def guardar():
            piezas = None
            if ent_piezas.get().strip():
                try:
                    piezas = float(ent_piezas.get())
                    if piezas < 0: raise ValueError()
                except:
                    messagebox.showwarning("Error", "Piezas inválidas")
                    return
            
            contenido = None
            if ent_contenido.get().strip():
                try:
                    contenido = float(ent_contenido.get())
                    if contenido < 0: raise ValueError()
                except:
                    messagebox.showwarning("Error", "Contenido inválido")
                    return
            
            ok, msg = ServicioInsumoCRUD.actualizar_insumo(
                self.insumo_sel["id"], piezas, contenido, cmb_unidad.get().strip())
            
            if ok:
                dlg.destroy()
                self.cargar_insumos_servicio()
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(frame_btns, text="Guardar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.COLOR_EXITO, fg=PaletaColores.BLANCO,
                  relief="flat", padx=15, command=guardar).pack(side="left", padx=5)
        tk.Button(frame_btns, text="Cancelar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.GRIS_MEDIO, fg=PaletaColores.BLANCO,
                  relief="flat", padx=15, command=dlg.destroy).pack(side="left", padx=5)
    
    def quitar_insumo_servicio(self):
        """Quita un insumo del servicio"""
        if not self.insumo_sel:
            return
        
        if messagebox.askyesno("Confirmar", f"¿Quitar '{self.insumo_sel['nombre']}' del servicio?"):
            ok, msg = ServicioInsumoCRUD.eliminar_insumo(self.insumo_sel["id"])
            if ok:
                self.cargar_insumos_servicio()
                self.cargar_servicios()  # Actualizar contador
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)


def abrir_ventana_servicios(parent):
    return VentanaServicios(parent)