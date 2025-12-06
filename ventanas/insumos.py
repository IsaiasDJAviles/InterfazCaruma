"""
Módulo de Gestión de Insumos - CARUMA
CRUD completo para insumos con control de inventario
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from estilos.colores import PaletaColores
from estilos.fuentes import Fuentes
from utils.db_connection import Database
from utils.posiciones import Posiciones
from ventanas.formularios import GestorFormularios
import ventanas.formularios as vf


class InsumosCRUD:
    """Operaciones CRUD de insumos"""
    
    @staticmethod
    def obtener_todos():
        try:
            query = """
                SELECT i.id, i.nombre, COALESCE(c.nombre, 'Sin categoría') as categoria,
                    i.piezas, i.contenido_por_pieza, i.unidad_contenido,
                    i.fecha_caducidad, i.alerta_piezas, i.id_categoria
                FROM insumos i LEFT JOIN categorias c ON i.id_categoria = c.id
                ORDER BY i.nombre
            """
            return Database.execute_query(query)
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def obtener_por_id(id_insumo):
        try:
            query = """SELECT id, nombre, id_categoria, piezas, contenido_por_pieza,
                       unidad_contenido, fecha_caducidad, alerta_piezas
                       FROM insumos WHERE id = %s"""
            resultado = Database.execute_query(query, (id_insumo,))
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    @staticmethod
    def crear(nombre, id_categoria, piezas, contenido, unidad, fecha_cad, alerta):
        try:
            query = """INSERT INTO insumos (nombre, id_categoria, piezas, contenido_por_pieza,
                       unidad_contenido, fecha_caducidad, alerta_piezas)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            Database.execute_update(query, (nombre.strip(), id_categoria or None, piezas,
                                            contenido or None, unidad or None, fecha_cad or None, alerta))
            return True, "Insumo creado exitosamente"
        except Exception as e:
            if "unique" in str(e).lower():
                return False, "Ya existe un insumo con ese nombre"
            return False, f"Error: {e}"
    
    @staticmethod
    def actualizar(id_insumo, nombre, id_categoria, piezas, contenido, unidad, fecha_cad, alerta):
        try:
            query = """UPDATE insumos SET nombre=%s, id_categoria=%s, piezas=%s,
                       contenido_por_pieza=%s, unidad_contenido=%s, fecha_caducidad=%s,
                       alerta_piezas=%s WHERE id=%s"""
            Database.execute_update(query, (nombre.strip(), id_categoria or None, piezas,
                                            contenido or None, unidad or None, fecha_cad or None,
                                            alerta, id_insumo))
            return True, "Insumo actualizado exitosamente"
        except Exception as e:
            if "unique" in str(e).lower():
                return False, "Ya existe un insumo con ese nombre"
            return False, f"Error: {e}"
    
    @staticmethod
    def eliminar(id_insumo):
        try:
            check = Database.execute_query("SELECT COUNT(*) FROM servicio_insumo WHERE id_insumo=%s", (id_insumo,))
            if check and check[0][0] > 0:
                return False, "El insumo está asociado a servicios"
            Database.execute_update("DELETE FROM alertas WHERE id_insumo=%s", (id_insumo,))
            Database.execute_update("DELETE FROM insumos WHERE id=%s", (id_insumo,))
            return True, "Insumo eliminado exitosamente"
        except Exception as e:
            return False, f"Error: {e}"
    
    @staticmethod
    def buscar(termino):
        try:
            query = """SELECT i.id, i.nombre, COALESCE(c.nombre, 'Sin categoría'),
                       i.piezas, i.contenido_por_pieza, i.unidad_contenido,
                       i.fecha_caducidad, i.alerta_piezas, i.id_categoria
                       FROM insumos i LEFT JOIN categorias c ON i.id_categoria = c.id
                       WHERE i.nombre ILIKE %s OR c.nombre ILIKE %s ORDER BY i.nombre"""
            return Database.execute_query(query, (f"%{termino}%", f"%{termino}%"))
        except:
            return []
    
    @staticmethod
    def filtrar_por_categoria(id_cat):
        try:
            if id_cat is None:
                return InsumosCRUD.obtener_todos()
            query = """SELECT i.id, i.nombre, COALESCE(c.nombre, 'Sin categoría'),
                       i.piezas, i.contenido_por_pieza, i.unidad_contenido,
                       i.fecha_caducidad, i.alerta_piezas, i.id_categoria
                       FROM insumos i LEFT JOIN categorias c ON i.id_categoria = c.id
                       WHERE i.id_categoria = %s ORDER BY i.nombre"""
            return Database.execute_query(query, (id_cat,))
        except:
            return []
    
    @staticmethod
    def obtener_stock_bajo():
        try:
            query = """SELECT i.id, i.nombre, COALESCE(c.nombre, 'Sin categoría'),
                       i.piezas, i.contenido_por_pieza, i.unidad_contenido,
                       i.fecha_caducidad, i.alerta_piezas, i.id_categoria
                       FROM insumos i LEFT JOIN categorias c ON i.id_categoria = c.id
                       WHERE i.piezas <= i.alerta_piezas AND i.alerta_piezas > 0
                       ORDER BY i.piezas"""
            return Database.execute_query(query)
        except:
            return []
    
    @staticmethod
    def obtener_por_caducar(dias=7):
        try:
            query = """SELECT i.id, i.nombre, COALESCE(c.nombre, 'Sin categoría'),
                       i.piezas, i.contenido_por_pieza, i.unidad_contenido,
                       i.fecha_caducidad, i.alerta_piezas, i.id_categoria
                       FROM insumos i LEFT JOIN categorias c ON i.id_categoria = c.id
                       WHERE i.fecha_caducidad IS NOT NULL 
                       AND i.fecha_caducidad <= CURRENT_DATE + %s
                       AND i.fecha_caducidad >= CURRENT_DATE ORDER BY i.fecha_caducidad"""
            return Database.execute_query(query, (dias,))
        except:
            return []
    
    @staticmethod
    def actualizar_piezas(id_insumo, cantidad, op='set'):
        try:
            if op == 'add':
                q = "UPDATE insumos SET piezas = piezas + %s WHERE id = %s"
            elif op == 'subtract':
                q = "UPDATE insumos SET piezas = GREATEST(0, piezas - %s) WHERE id = %s"
            else:
                q = "UPDATE insumos SET piezas = %s WHERE id = %s"
            Database.execute_update(q, (cantidad, id_insumo))
            return True, "Stock actualizado"
        except Exception as e:
            return False, f"Error: {e}"


class VentanaInsumos:
    """Ventana de gestión de insumos"""
    
    UNIDADES = ["kg", "g", "L", "ml", "pza", "paq", "caja", "bolsa", "lata", "botella"]
    
    def __init__(self, parent):
        self.parent = parent
        self.insumo_sel = None
        self.categorias = []
        self.editando = False
        self.id_editando = None
        self.mostrar()
    
    def mostrar(self):
        GestorFormularios.limpiar_contenido()
        vf.frame_contenido_actual = Posiciones.contenido(self.parent)
        
        self.frame_principal = tk.Frame(vf.frame_contenido_actual, bg=PaletaColores.COLOR_FONDO, padx=20, pady=15)
        self.frame_principal.pack(fill="both", expand=True)
        
        self.cargar_categorias()
        self.crear_titulo()
        self.crear_barra_herramientas()
        self.crear_tabla()
        self.crear_formulario()
        self.cargar_insumos()
    
    def cargar_categorias(self):
        try:
            self.categorias = Database.execute_query("SELECT id, nombre FROM categorias ORDER BY nombre")
        except:
            self.categorias = []
    
    def crear_titulo(self):
        frame = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame.pack(fill="x", pady=(0, 15))
        tk.Label(frame, text="📦 Gestión de Insumos", font=Fuentes.FUENTE_TITULOS,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(side="left")
        self.lbl_contador = tk.Label(frame, text="", font=Fuentes.FUENTE_TEXTO,
                                      bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.GRIS_MEDIO)
        self.lbl_contador.pack(side="right")
    
    def crear_barra_herramientas(self):
        # Fila 1: Búsqueda y filtros
        f1 = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        f1.pack(fill="x", pady=(0, 8))
        
        tk.Label(f1, text="🔍", bg=PaletaColores.COLOR_FONDO).pack(side="left")
        self.ent_buscar = tk.Entry(f1, font=Fuentes.FUENTE_TEXTO, width=18, relief="solid", bd=1)
        self.ent_buscar.pack(side="left", padx=(3, 10))
        self.ent_buscar.bind("<KeyRelease>", self.buscar)
        
        tk.Label(f1, text="Categoría:", bg=PaletaColores.COLOR_FONDO).pack(side="left")
        self.cmb_filtro = ttk.Combobox(f1, state="readonly", width=18)
        self.cmb_filtro.pack(side="left", padx=(3, 10))
        self.cmb_filtro.bind("<<ComboboxSelected>>", self.filtrar_categoria)
        self.actualizar_combo_filtro()
        
        tk.Button(f1, text="⚠️ Stock Bajo", font=Fuentes.FUENTE_MENU, bg=PaletaColores.COLOR_ALERTA,
                  relief="flat", cursor="hand2", command=self.ver_stock_bajo).pack(side="left", padx=3)
        tk.Button(f1, text="📅 Por Caducar", font=Fuentes.FUENTE_MENU, bg=PaletaColores.COLOR_ERROR,
                  fg=PaletaColores.BLANCO, relief="flat", cursor="hand2",
                  command=self.ver_por_caducar).pack(side="left", padx=3)
        tk.Button(f1, text="📋 Todos", font=Fuentes.FUENTE_MENU, bg=PaletaColores.GRIS_CLARO,
                  relief="flat", cursor="hand2", command=self.cargar_insumos).pack(side="left", padx=3)
        
        # Fila 2: Botones de acción
        f2 = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        f2.pack(fill="x", pady=(0, 10))
        
        self.btn_nuevo = tk.Button(f2, text="➕ Nuevo Insumo", font=Fuentes.FUENTE_BOTONES,
                                    bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                                    padx=15, pady=8, command=self.form_nuevo)
        self.btn_nuevo.pack(side="left", padx=(0, 5))
        
        self.btn_editar = tk.Button(f2, text="✏️ Editar", font=Fuentes.FUENTE_BOTONES,
                                     bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                                     padx=15, pady=8, state="disabled", command=self.form_editar)
        self.btn_editar.pack(side="left", padx=5)
        
        self.btn_stock = tk.Button(f2, text="📊 Ajustar Stock", font=Fuentes.FUENTE_BOTONES,
                                    bg=PaletaColores.COLOR_INFO, fg=PaletaColores.BLANCO,
                                    relief="flat", cursor="hand2", padx=15, pady=8,
                                    state="disabled", command=self.ajustar_stock)
        self.btn_stock.pack(side="left", padx=5)
        
        self.btn_eliminar = tk.Button(f2, text="🗑️ Eliminar", font=Fuentes.FUENTE_BOTONES,
                                       bg=PaletaColores.COLOR_ERROR, fg=PaletaColores.BLANCO,
                                       relief="flat", cursor="hand2", padx=15, pady=8,
                                       state="disabled", command=self.eliminar)
        self.btn_eliminar.pack(side="left", padx=5)
    
    def actualizar_combo_filtro(self):
        self.cmb_filtro['values'] = ["Todas"] + [c[1] for c in self.categorias]
        self.cmb_filtro.current(0)
    
    def crear_tabla(self):
        frame = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame.pack(fill="both", expand=True, pady=(0, 10))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("T.Treeview", rowheight=28, font=Fuentes.FUENTE_TEXTO)
        style.configure("T.Treeview.Heading", background=PaletaColores.DORADO_CARUMA,
                        font=Fuentes.FUENTE_BOTONES, padding=5)
        style.map("T.Treeview", background=[("selected", PaletaColores.DORADO_CLARO)])
        
        cols = ("id", "nombre", "categoria", "piezas", "contenido", "unidad", "caducidad", "alerta")
        self.tabla = ttk.Treeview(frame, columns=cols, show="headings", style="T.Treeview")
        
        for c, w in [("id", 45), ("nombre", 170), ("categoria", 110), ("piezas", 55),
                     ("contenido", 65), ("unidad", 55), ("caducidad", 85), ("alerta", 50)]:
            self.tabla.heading(c, text=c.capitalize())
            self.tabla.column(c, width=w, anchor="center" if c != "nombre" and c != "categoria" else "w")
        
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tabla.bind("<<TreeviewSelect>>", self.on_select)
        self.tabla.bind("<Double-1>", lambda e: self.form_editar())
        self.tabla.tag_configure("stock_bajo", background="#FFCCCC")
        self.tabla.tag_configure("por_caducar", background="#FFE6CC")
    
    def crear_formulario(self):
        self.frame_form = tk.Frame(self.frame_principal, bg=PaletaColores.GRIS_CLARO, padx=15, pady=12)
        
        self.lbl_titulo_form = tk.Label(self.frame_form, text="Nuevo Insumo", font=Fuentes.FUENTE_TEXTO_GRANDE,
                                         bg=PaletaColores.GRIS_CLARO, fg=PaletaColores.DORADO_CARUMA)
        self.lbl_titulo_form.grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))
        
        # Fila 1
        tk.Label(self.frame_form, text="Nombre:*", bg=PaletaColores.GRIS_CLARO).grid(row=1, column=0, sticky="e", padx=3)
        self.ent_nombre = tk.Entry(self.frame_form, width=22, relief="solid", bd=1)
        self.ent_nombre.grid(row=1, column=1, sticky="w", padx=(0, 10))
        
        tk.Label(self.frame_form, text="Categoría:", bg=PaletaColores.GRIS_CLARO).grid(row=1, column=2, sticky="e", padx=3)
        self.cmb_cat = ttk.Combobox(self.frame_form, state="readonly", width=16)
        self.cmb_cat.grid(row=1, column=3, sticky="w", padx=(0, 10))
        self.actualizar_combo_cat()
        
        tk.Label(self.frame_form, text="Piezas:*", bg=PaletaColores.GRIS_CLARO).grid(row=1, column=4, sticky="e", padx=3)
        self.ent_piezas = tk.Entry(self.frame_form, width=7, relief="solid", bd=1)
        self.ent_piezas.grid(row=1, column=5, sticky="w", padx=(0, 10))
        self.ent_piezas.insert(0, "0")
        
        tk.Label(self.frame_form, text="Alerta:", bg=PaletaColores.GRIS_CLARO).grid(row=1, column=6, sticky="e", padx=3)
        self.ent_alerta = tk.Entry(self.frame_form, width=6, relief="solid", bd=1)
        self.ent_alerta.grid(row=1, column=7, sticky="w")
        self.ent_alerta.insert(0, "0")
        
        # Fila 2
        tk.Label(self.frame_form, text="Contenido:", bg=PaletaColores.GRIS_CLARO).grid(row=2, column=0, sticky="e", padx=3, pady=(8,0))
        self.ent_contenido = tk.Entry(self.frame_form, width=8, relief="solid", bd=1)
        self.ent_contenido.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=(8,0))
        
        tk.Label(self.frame_form, text="Unidad:", bg=PaletaColores.GRIS_CLARO).grid(row=2, column=2, sticky="e", padx=3, pady=(8,0))
        self.cmb_unidad = ttk.Combobox(self.frame_form, values=self.UNIDADES, width=8)
        self.cmb_unidad.grid(row=2, column=3, sticky="w", padx=(0, 10), pady=(8,0))
        
        tk.Label(self.frame_form, text="Caducidad:", bg=PaletaColores.GRIS_CLARO).grid(row=2, column=4, sticky="e", padx=3, pady=(8,0))
        self.ent_caducidad = tk.Entry(self.frame_form, width=11, relief="solid", bd=1)
        self.ent_caducidad.grid(row=2, column=5, sticky="w", pady=(8,0))
        tk.Label(self.frame_form, text="YYYY-MM-DD", font=("Segoe UI", 8), bg=PaletaColores.GRIS_CLARO,
                 fg=PaletaColores.GRIS_MEDIO).grid(row=2, column=6, columnspan=2, sticky="w", pady=(8,0))
        
        # Fila 3: Botones
        frame_btns = tk.Frame(self.frame_form, bg=PaletaColores.GRIS_CLARO)
        frame_btns.grid(row=3, column=0, columnspan=8, pady=(12, 0))
        
        tk.Button(frame_btns, text="💾 Guardar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.COLOR_EXITO, fg=PaletaColores.BLANCO,
                  relief="flat", cursor="hand2", padx=20, pady=6,
                  command=self.guardar).pack(side="left", padx=(0, 10))
        
        tk.Button(frame_btns, text="❌ Cancelar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.GRIS_MEDIO, fg=PaletaColores.BLANCO,
                  relief="flat", cursor="hand2", padx=20, pady=6,
                  command=self.ocultar_form).pack(side="left")
    
    def actualizar_combo_cat(self):
        self.cargar_categorias()
        self.cmb_cat['values'] = ["Sin categoría"] + [c[1] for c in self.categorias]
        self.cmb_cat.current(0)
    
    def cargar_insumos(self, datos=None):
        for i in self.tabla.get_children():
            self.tabla.delete(i)
        
        if datos is None:
            datos = InsumosCRUD.obtener_todos()
        
        hoy = date.today()
        for ins in datos:
            tags = []
            pzas, alerta, fec = ins[3] or 0, ins[7] or 0, ins[6]
            if alerta > 0 and pzas <= alerta:
                tags.append("stock_bajo")
            if fec and 0 <= (fec - hoy).days <= 7:
                tags.append("por_caducar")
            
            fec_str = fec.strftime("%Y-%m-%d") if fec else ""
            self.tabla.insert("", "end", values=(ins[0], ins[1], ins[2], pzas,
                              ins[4] or "", ins[5] or "", fec_str, alerta), tags=tags)
        
        self.lbl_contador.config(text=f"{len(datos)} insumo{'s' if len(datos)!=1 else ''}")
        self.insumo_sel = None
        self.btn_editar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
        self.btn_stock.config(state="disabled")
    
    def on_select(self, e):
        sel = self.tabla.selection()
        if sel:
            v = self.tabla.item(sel[0])["values"]
            self.insumo_sel = {"id": v[0], "nombre": v[1], "piezas": v[3]}
            self.btn_editar.config(state="normal")
            self.btn_eliminar.config(state="normal")
            self.btn_stock.config(state="normal")
    
    def form_nuevo(self):
        self.editando = False
        self.id_editando = None
        self.lbl_titulo_form.config(text="➕ Nuevo Insumo")
        self.limpiar_form()
        self.frame_form.pack(fill="x", pady=(0, 10))
        self.ent_nombre.focus_set()
    
    def form_editar(self):
        if not self.insumo_sel:
            messagebox.showwarning("Aviso", "Seleccione un insumo")
            return
        
        ins = InsumosCRUD.obtener_por_id(self.insumo_sel["id"])
        if not ins:
            messagebox.showerror("Error", "No se pudo cargar")
            return
        
        self.editando = True
        self.id_editando = ins[0]
        self.lbl_titulo_form.config(text="✏️ Editar Insumo")
        
        self.limpiar_form()
        self.ent_nombre.insert(0, ins[1])
        
        self.actualizar_combo_cat()
        if ins[2]:
            for i, c in enumerate(self.categorias):
                if c[0] == ins[2]:
                    self.cmb_cat.current(i + 1)
                    break
        
        self.ent_piezas.delete(0, tk.END)
        self.ent_piezas.insert(0, str(ins[3] or 0))
        if ins[4]:
            self.ent_contenido.insert(0, str(ins[4]))
        self.cmb_unidad.set(ins[5] or "")
        if ins[6]:
            self.ent_caducidad.insert(0, ins[6].strftime("%Y-%m-%d"))
        self.ent_alerta.delete(0, tk.END)
        self.ent_alerta.insert(0, str(ins[7] or 0))
        
        self.frame_form.pack(fill="x", pady=(0, 10))
        self.ent_nombre.focus_set()
    
    def limpiar_form(self):
        self.ent_nombre.delete(0, tk.END)
        self.actualizar_combo_cat()
        self.ent_piezas.delete(0, tk.END)
        self.ent_piezas.insert(0, "0")
        self.ent_contenido.delete(0, tk.END)
        self.cmb_unidad.set("")
        self.ent_caducidad.delete(0, tk.END)
        self.ent_alerta.delete(0, tk.END)
        self.ent_alerta.insert(0, "0")
    
    def ocultar_form(self):
        self.frame_form.pack_forget()
        self.editando = False
        self.id_editando = None
    
    def validar(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre or len(nombre) < 2:
            messagebox.showwarning("Error", "Nombre inválido (mín. 2 caracteres)")
            return None
        
        try:
            piezas = int(self.ent_piezas.get() or 0)
            if piezas < 0: raise ValueError()
        except:
            messagebox.showwarning("Error", "Piezas debe ser número positivo")
            return None
        
        contenido = None
        if self.ent_contenido.get().strip():
            try:
                contenido = float(self.ent_contenido.get())
                if contenido < 0: raise ValueError()
            except:
                messagebox.showwarning("Error", "Contenido inválido")
                return None
        
        fecha = None
        if self.ent_caducidad.get().strip():
            try:
                fecha = datetime.strptime(self.ent_caducidad.get().strip(), "%Y-%m-%d").date()
            except:
                messagebox.showwarning("Error", "Fecha inválida (YYYY-MM-DD)")
                return None
        
        try:
            alerta = int(self.ent_alerta.get() or 0)
            if alerta < 0: raise ValueError()
        except:
            messagebox.showwarning("Error", "Alerta debe ser número positivo")
            return None
        
        id_cat = None
        idx = self.cmb_cat.current()
        if idx > 0:
            id_cat = self.categorias[idx - 1][0]
        
        return {"nombre": nombre, "id_cat": id_cat, "piezas": piezas, "contenido": contenido,
                "unidad": self.cmb_unidad.get().strip(), "fecha": fecha, "alerta": alerta}
    
    def guardar(self):
        d = self.validar()
        if not d:
            return
        
        if self.editando:
            ok, msg = InsumosCRUD.actualizar(self.id_editando, d["nombre"], d["id_cat"], d["piezas"],
                                              d["contenido"], d["unidad"], d["fecha"], d["alerta"])
        else:
            ok, msg = InsumosCRUD.crear(d["nombre"], d["id_cat"], d["piezas"],
                                         d["contenido"], d["unidad"], d["fecha"], d["alerta"])
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.ocultar_form()
            self.cargar_insumos()
        else:
            messagebox.showerror("Error", msg)
    
    def eliminar(self):
        if not self.insumo_sel:
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{self.insumo_sel['nombre']}'?"):
            ok, msg = InsumosCRUD.eliminar(self.insumo_sel["id"])
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_insumos()
            else:
                messagebox.showerror("Error", msg)
    
    def buscar(self, e=None):
        t = self.ent_buscar.get().strip()
        self.cargar_insumos(InsumosCRUD.buscar(t) if t else None)
    
    def filtrar_categoria(self, e=None):
        idx = self.cmb_filtro.current()
        if idx == 0:
            self.cargar_insumos()
        else:
            self.cargar_insumos(InsumosCRUD.filtrar_por_categoria(self.categorias[idx-1][0]))
    
    def ver_stock_bajo(self):
        d = InsumosCRUD.obtener_stock_bajo()
        self.cargar_insumos(d)
        if not d:
            messagebox.showinfo("Info", "No hay insumos con stock bajo")
    
    def ver_por_caducar(self):
        d = InsumosCRUD.obtener_por_caducar(7)
        self.cargar_insumos(d)
        if not d:
            messagebox.showinfo("Info", "No hay insumos por caducar")
    
    def ajustar_stock(self):
        if not self.insumo_sel:
            return
        
        dlg = tk.Toplevel(self.parent)
        dlg.title("Ajustar Stock")
        dlg.geometry("380x170")
        dlg.configure(bg=PaletaColores.COLOR_FONDO)
        dlg.resizable(False, False)
        dlg.transient(self.parent)
        dlg.grab_set()
        
        x = self.parent.winfo_x() + self.parent.winfo_width()//2 - 190
        y = self.parent.winfo_y() + self.parent.winfo_height()//2 - 85
        dlg.geometry(f"+{x}+{y}")
        
        tk.Label(dlg, text=f"📦 {self.insumo_sel['nombre']}", font=Fuentes.FUENTE_TEXTO_GRANDE,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(pady=(12, 3))
        tk.Label(dlg, text=f"Stock actual: {self.insumo_sel['piezas']} piezas",
                 bg=PaletaColores.COLOR_FONDO).pack(pady=(0, 8))
        
        fr = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        fr.pack(pady=5)
        tk.Label(fr, text="Cantidad:", bg=PaletaColores.COLOR_FONDO).pack(side="left", padx=5)
        ent = tk.Entry(fr, width=10, relief="solid", bd=1)
        ent.pack(side="left")
        ent.insert(0, "0")
        ent.focus_set()
        ent.select_range(0, tk.END)
        
        fb = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        fb.pack(pady=12)
        
        def hacer(op):
            try:
                c = int(ent.get())
                if c < 0: raise ValueError()
            except:
                messagebox.showwarning("Error", "Número inválido")
                return
            ok, msg = InsumosCRUD.actualizar_piezas(self.insumo_sel["id"], c, op)
            if ok:
                dlg.destroy()
                self.cargar_insumos()
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(fb, text="➕ Agregar", font=Fuentes.FUENTE_BOTONES, bg=PaletaColores.COLOR_EXITO,
                  fg=PaletaColores.BLANCO, relief="flat", padx=10, command=lambda: hacer('add')).pack(side="left", padx=3)
        tk.Button(fb, text="➖ Restar", font=Fuentes.FUENTE_BOTONES, bg=PaletaColores.COLOR_ERROR,
                  fg=PaletaColores.BLANCO, relief="flat", padx=10, command=lambda: hacer('subtract')).pack(side="left", padx=3)
        tk.Button(fb, text="📝 Establecer", font=Fuentes.FUENTE_BOTONES, bg=PaletaColores.COLOR_INFO,
                  fg=PaletaColores.BLANCO, relief="flat", padx=10, command=lambda: hacer('set')).pack(side="left", padx=3)


def abrir_ventana_insumos(parent):
    return VentanaInsumos(parent)