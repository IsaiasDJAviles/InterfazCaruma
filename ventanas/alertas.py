"""
Módulo de Gestión de Alertas - CARUMA
Sistema de alertas para stock bajo y caducidad
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from estilos.colores import PaletaColores
from estilos.fuentes import Fuentes
from utils.db_connection import Database
from utils.posiciones import Posiciones
from ventanas.formularios import GestorFormularios
import ventanas.formularios as vf


class AlertasCRUD:
    """Operaciones para alertas"""
    
    @staticmethod
    def obtener_alertas_stock_bajo():
        """Obtiene insumos con stock bajo"""
        try:
            query = """
                SELECT 
                    i.id,
                    i.nombre,
                    COALESCE(c.nombre, 'Sin categoría') as categoria,
                    i.piezas,
                    i.alerta_piezas,
                    i.alerta_piezas - i.piezas as faltante
                FROM insumos i
                LEFT JOIN categorias c ON i.id_categoria = c.id
                WHERE i.piezas <= i.alerta_piezas AND i.alerta_piezas > 0
                ORDER BY (i.alerta_piezas - i.piezas) DESC
            """
            return Database.ejecutar_query(query)
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def obtener_alertas_por_caducar(dias=7):
        """Obtiene insumos próximos a caducar"""
        try:
            query = """
                SELECT 
                    i.id,
                    i.nombre,
                    COALESCE(c.nombre, 'Sin categoría') as categoria,
                    i.piezas,
                    i.fecha_caducidad,
                    CAST(julianday(i.fecha_caducidad) - julianday('now') AS INTEGER) AS dias_restantes
                FROM insumos i
                LEFT JOIN categorias c ON i.id_categoria = c.id
                WHERE i.fecha_caducidad IS NOT NULL 
                AND date(i.fecha_caducidad) >= date('now')
                AND date(i.fecha_caducidad) <= date('now', '+' || ? || ' days')
                ORDER BY date(i.fecha_caducidad) ASC
            """
            return Database.ejecutar_query(query, (dias,))
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def obtener_alertas_caducados():
        """Obtiene insumos ya caducados"""
        try:
            query = """
                SELECT 
                    i.id,
                    i.nombre,
                    COALESCE(c.nombre, 'Sin categoría') as categoria,
                    i.piezas,
                    i.fecha_caducidad,
                    CAST(julianday('now') - julianday(i.fecha_caducidad) AS INTEGER) AS dias_caducado
                FROM insumos i
                LEFT JOIN categorias c ON i.id_categoria = c.id
                WHERE i.fecha_caducidad IS NOT NULL 
                AND date(i.fecha_caducidad) < date('now')
                ORDER BY date(i.fecha_caducidad) ASC
            """

            return Database.ejecutar_query(query)
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def obtener_resumen_alertas():
        """Obtiene conteo de alertas por tipo"""
        try:
            query = """
                SELECT 
                    SUM(CASE WHEN piezas <= alerta_piezas AND alerta_piezas > 0 THEN 1 ELSE 0 END) AS stock_bajo,
                    SUM(CASE WHEN fecha_caducidad IS NOT NULL
                        AND date(fecha_caducidad) >= date('now')
                        AND date(fecha_caducidad) <= date('now', '+7 days') THEN 1 ELSE 0 END) AS por_caducar,
                    SUM(CASE WHEN fecha_caducidad IS NOT NULL
                        AND date(fecha_caducidad) < date('now') THEN 1 ELSE 0 END) AS caducados
                FROM insumos
            """
            resultado = Database.ejecutar_query(query)
            return resultado[0] if resultado else (0, 0, 0)
        except:
            return (0, 0, 0)
    
    @staticmethod
    def registrar_alerta(id_insumo, tipo, mensaje):
        """Registra una alerta en la base de datos"""
        try:
            query = """
                INSERT INTO alertas (id_insumo, tipo, mensaje, fecha_alerta)
                VALUES (?, ?, ?, date('now'))
            """

            Database.ejecutar_comando(query, (id_insumo, tipo, mensaje))
            return True
        except:
            return False
    
    @staticmethod
    def obtener_historial_alertas(limite=50):
        """Obtiene el historial de alertas registradas"""
        try:
            query = """
                SELECT 
                    a.id,
                    a.fecha_alerta,
                    i.nombre,
                    a.tipo,
                    a.mensaje
                FROM alertas a
                JOIN insumos i ON a.id_insumo = i.id
                ORDER BY date(a.fecha_alerta) DESC, a.id DESC
                LIMIT ?
            """
            return Database.ejecutar_query(query, (limite,))
        except:
            return []
    
    @staticmethod
    def limpiar_historial():
        """Limpia el historial de alertas"""
        try:
            Database.ejecutar_comando("DELETE FROM alertas")
            return True, "Historial limpiado"
        except Exception as e:
            return False, f"Error: {e}"


class VentanaAlertas:
    """Ventana de gestión de alertas"""
    
    def __init__(self, parent):
        self.parent = parent
        self.mostrar()
    
    def mostrar(self):
        GestorFormularios.limpiar_contenido()
        vf.frame_contenido_actual = Posiciones.contenido(self.parent)
        
        self.frame_principal = tk.Frame(vf.frame_contenido_actual, bg=PaletaColores.COLOR_FONDO, padx=20, pady=15)
        self.frame_principal.pack(fill="both", expand=True)
        
        self.crear_titulo()
        self.crear_panel_resumen()
        self.crear_notebook_alertas()
        self.cargar_datos()
    
    def crear_titulo(self):
        frame = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(frame, text="Centro de Alertas", font=Fuentes.FUENTE_TITULOS,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(side="left")
        
        # Botones de acción
        frame_btns = tk.Frame(frame, bg=PaletaColores.COLOR_FONDO)
        frame_btns.pack(side="right")
        
        tk.Button(frame_btns, text="Actualizar", font=Fuentes.FUENTE_MENU,
                  bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                  padx=10, command=self.cargar_datos).pack(side="left", padx=5)
        
        tk.Button(frame_btns, text="Generar Reporte", font=Fuentes.FUENTE_MENU,
                  bg=PaletaColores.COLOR_INFO, fg=PaletaColores.BLANCO,
                  relief="flat", cursor="hand2", padx=10,
                  command=self.generar_reporte).pack(side="left", padx=5)
    
    def crear_panel_resumen(self):
        """Panel con resumen de alertas"""
        frame_resumen = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame_resumen.pack(fill="x", pady=(0, 15))
        
        self.frame_tarjetas = tk.Frame(frame_resumen, bg=PaletaColores.COLOR_FONDO)
        self.frame_tarjetas.pack()
        
        self.tarjetas_valores = {}
    
    def crear_tarjeta_alerta(self, parent, titulo, valor, icono, color_bg, color_fg, descripcion=""):
        """Crea una tarjeta de alerta"""
        frame = tk.Frame(parent, bg=color_bg, padx=20, pady=15)
        
        # Encabezado
        frame_top = tk.Frame(frame, bg=color_bg)
        frame_top.pack(fill="x")
        
        tk.Label(frame_top, text=icono, font=("Segoe UI", 20), bg=color_bg).pack(side="left")
        tk.Label(frame_top, text=titulo, font=Fuentes.FUENTE_TEXTO_GRANDE, bg=color_bg,
                 fg=color_fg).pack(side="left", padx=(10, 0))
        
        # Valor grande
        lbl_valor = tk.Label(frame, text=str(valor), font=("Segoe UI", 32, "bold"),
                             bg=color_bg, fg=color_fg)
        lbl_valor.pack(pady=(5, 0))
        
        # Descripción
        if descripcion:
            tk.Label(frame, text=descripcion, font=Fuentes.FUENTE_MENU, bg=color_bg,
                     fg=color_fg).pack()
        
        return frame, lbl_valor
    
    def crear_notebook_alertas(self):
        """Crea el notebook con las pestañas de alertas"""
        style = ttk.Style()
        style.configure("Alertas.TNotebook", background=PaletaColores.COLOR_FONDO)
        style.configure("Alertas.TNotebook.Tab", font=Fuentes.FUENTE_TEXTO, padding=[15, 8])
        
        self.notebook = ttk.Notebook(self.frame_principal, style="Alertas.TNotebook")
        self.notebook.pack(fill="both", expand=True)
        
        # Pestaña Stock Bajo
        self.tab_stock = tk.Frame(self.notebook, bg=PaletaColores.COLOR_FONDO)
        self.notebook.add(self.tab_stock, text="Stock Bajo")
        self.crear_tabla_stock_bajo()
        
        # Pestaña Por Caducar
        self.tab_caducar = tk.Frame(self.notebook, bg=PaletaColores.COLOR_FONDO)
        self.notebook.add(self.tab_caducar, text="Por Caducar")
        self.crear_tabla_por_caducar()
        
        # Pestaña Caducados
        self.tab_caducados = tk.Frame(self.notebook, bg=PaletaColores.COLOR_FONDO)
        self.notebook.add(self.tab_caducados, text="Caducados")
        self.crear_tabla_caducados()
        
        # Pestaña Historial
        self.tab_historial = tk.Frame(self.notebook, bg=PaletaColores.COLOR_FONDO)
        self.notebook.add(self.tab_historial, text="Historial")
        self.crear_tabla_historial()
    
    def crear_tabla_stock_bajo(self):
        """Tabla de insumos con stock bajo"""
        frame_info = tk.Frame(self.tab_stock, bg=PaletaColores.COLOR_FONDO)
        frame_info.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_info, text="Insumos que necesitan reabastecimiento",
                 font=Fuentes.FUENTE_TEXTO, bg=PaletaColores.COLOR_FONDO,
                 fg=PaletaColores.GRIS_MEDIO).pack(side="left")
        
        self.lbl_count_stock = tk.Label(frame_info, text="", font=Fuentes.FUENTE_MENU,
                                         bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.GRIS_MEDIO)
        self.lbl_count_stock.pack(side="right")
        
        frame_tabla = tk.Frame(self.tab_stock, bg=PaletaColores.COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        cols = ("id", "nombre", "categoria", "stock", "minimo", "faltante")
        self.tabla_stock = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=12)
        
        self.tabla_stock.heading("id", text="ID")
        self.tabla_stock.heading("nombre", text="Insumo")
        self.tabla_stock.heading("categoria", text="Categoría")
        self.tabla_stock.heading("stock", text="Stock")
        self.tabla_stock.heading("minimo", text="Mínimo")
        self.tabla_stock.heading("faltante", text="Faltante")
        
        self.tabla_stock.column("id", width=40, anchor="center")
        self.tabla_stock.column("nombre", width=200, anchor="w")
        self.tabla_stock.column("categoria", width=120, anchor="w")
        self.tabla_stock.column("stock", width=70, anchor="center")
        self.tabla_stock.column("minimo", width=70, anchor="center")
        self.tabla_stock.column("faltante", width=70, anchor="center")
        
        self.tabla_stock.tag_configure("critico", background="#FFCDD2")
        self.tabla_stock.tag_configure("bajo", background="#FFE0B2")
        
        sb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_stock.yview)
        self.tabla_stock.configure(yscrollcommand=sb.set)
        self.tabla_stock.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        # Botón para ir a compras
        frame_acciones = tk.Frame(self.tab_stock, bg=PaletaColores.COLOR_FONDO)
        frame_acciones.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(frame_acciones, text="Generar Lista de Compras", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                  padx=15, pady=8, command=self.generar_lista_compras).pack(side="left")
    
    def crear_tabla_por_caducar(self):
        """Tabla de insumos por caducar"""
        frame_info = tk.Frame(self.tab_caducar, bg=PaletaColores.COLOR_FONDO)
        frame_info.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_info, text="Insumos que caducan en los próximos 7 días",
                 font=Fuentes.FUENTE_TEXTO, bg=PaletaColores.COLOR_FONDO,
                 fg=PaletaColores.GRIS_MEDIO).pack(side="left")
        
        self.lbl_count_caducar = tk.Label(frame_info, text="", font=Fuentes.FUENTE_MENU,
                                           bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.GRIS_MEDIO)
        self.lbl_count_caducar.pack(side="right")
        
        frame_tabla = tk.Frame(self.tab_caducar, bg=PaletaColores.COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        cols = ("id", "nombre", "categoria", "stock", "caducidad", "dias")
        self.tabla_caducar = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=12)
        
        self.tabla_caducar.heading("id", text="ID")
        self.tabla_caducar.heading("nombre", text="Insumo")
        self.tabla_caducar.heading("categoria", text="Categoría")
        self.tabla_caducar.heading("stock", text="Stock")
        self.tabla_caducar.heading("caducidad", text="Caducidad")
        self.tabla_caducar.heading("dias", text="Días")
        
        self.tabla_caducar.column("id", width=40, anchor="center")
        self.tabla_caducar.column("nombre", width=200, anchor="w")
        self.tabla_caducar.column("categoria", width=120, anchor="w")
        self.tabla_caducar.column("stock", width=70, anchor="center")
        self.tabla_caducar.column("caducidad", width=100, anchor="center")
        self.tabla_caducar.column("dias", width=60, anchor="center")
        
        self.tabla_caducar.tag_configure("urgente", background="#FFCDD2")
        self.tabla_caducar.tag_configure("pronto", background="#FFE0B2")
        
        sb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_caducar.yview)
        self.tabla_caducar.configure(yscrollcommand=sb.set)
        self.tabla_caducar.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
    
    def crear_tabla_caducados(self):
        """Tabla de insumos caducados"""
        frame_info = tk.Frame(self.tab_caducados, bg=PaletaColores.COLOR_FONDO)
        frame_info.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_info, text="Insumos que ya caducaron - Requieren atención inmediata",
                 font=Fuentes.FUENTE_TEXTO, bg=PaletaColores.COLOR_FONDO,
                 fg=PaletaColores.COLOR_ERROR).pack(side="left")
        
        self.lbl_count_caducados = tk.Label(frame_info, text="", font=Fuentes.FUENTE_MENU,
                                             bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.GRIS_MEDIO)
        self.lbl_count_caducados.pack(side="right")
        
        frame_tabla = tk.Frame(self.tab_caducados, bg=PaletaColores.COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        cols = ("id", "nombre", "categoria", "stock", "caducidad", "dias_caducado")
        self.tabla_caducados = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=12)
        
        self.tabla_caducados.heading("id", text="ID")
        self.tabla_caducados.heading("nombre", text="Insumo")
        self.tabla_caducados.heading("categoria", text="Categoría")
        self.tabla_caducados.heading("stock", text="Stock")
        self.tabla_caducados.heading("caducidad", text="Caducó")
        self.tabla_caducados.heading("dias_caducado", text="Hace (días)")
        
        self.tabla_caducados.column("id", width=40, anchor="center")
        self.tabla_caducados.column("nombre", width=200, anchor="w")
        self.tabla_caducados.column("categoria", width=120, anchor="w")
        self.tabla_caducados.column("stock", width=70, anchor="center")
        self.tabla_caducados.column("caducidad", width=100, anchor="center")
        self.tabla_caducados.column("dias_caducado", width=80, anchor="center")
        
        self.tabla_caducados.tag_configure("caducado", background="#F8BBD0")
        
        sb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_caducados.yview)
        self.tabla_caducados.configure(yscrollcommand=sb.set)
        self.tabla_caducados.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        # Advertencia
        frame_warn = tk.Frame(self.tab_caducados, bg="#FFEBEE", padx=10, pady=8)
        frame_warn.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Label(frame_warn, text="Los productos caducados deben ser retirados del inventario por seguridad alimentaria",
                 font=Fuentes.FUENTE_TEXTO, bg="#FFEBEE", fg=PaletaColores.COLOR_ERROR).pack()
    
    def crear_tabla_historial(self):
        """Tabla de historial de alertas"""
        frame_info = tk.Frame(self.tab_historial, bg=PaletaColores.COLOR_FONDO)
        frame_info.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_info, text="Historial de alertas registradas",
                 font=Fuentes.FUENTE_TEXTO, bg=PaletaColores.COLOR_FONDO,
                 fg=PaletaColores.GRIS_MEDIO).pack(side="left")
        
        tk.Button(frame_info, text="Limpiar Historial", font=Fuentes.FUENTE_MENU,
                  bg=PaletaColores.COLOR_ERROR, fg=PaletaColores.BLANCO,
                  relief="flat", cursor="hand2", padx=8,
                  command=self.limpiar_historial).pack(side="right")
        
        frame_tabla = tk.Frame(self.tab_historial, bg=PaletaColores.COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        cols = ("id", "fecha", "insumo", "tipo", "mensaje")
        self.tabla_historial = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=12)
        
        self.tabla_historial.heading("id", text="ID")
        self.tabla_historial.heading("fecha", text="Fecha")
        self.tabla_historial.heading("insumo", text="Insumo")
        self.tabla_historial.heading("tipo", text="Tipo")
        self.tabla_historial.heading("mensaje", text="Mensaje")
        
        self.tabla_historial.column("id", width=40, anchor="center")
        self.tabla_historial.column("fecha", width=90, anchor="center")
        self.tabla_historial.column("insumo", width=150, anchor="w")
        self.tabla_historial.column("tipo", width=100, anchor="center")
        self.tabla_historial.column("mensaje", width=300, anchor="w")
        
        sb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscrollcommand=sb.set)
        self.tabla_historial.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
    
    def cargar_datos(self):
        """Carga todos los datos de alertas"""
        self.cargar_resumen()
        self.cargar_stock_bajo()
        self.cargar_por_caducar()
        self.cargar_caducados()
        self.cargar_historial()
    
    def cargar_resumen(self):
        """Carga las tarjetas de resumen"""
        for widget in self.frame_tarjetas.winfo_children():
            widget.destroy()
        
        stock_bajo, por_caducar, caducados = AlertasCRUD.obtener_resumen_alertas()
        total = stock_bajo + por_caducar + caducados
        
        tarjetas = [
            ("Total Alertas", total, "", PaletaColores.GRIS_CLARO, PaletaColores.NEGRO_CARUMA, "Alertas activas"),
            ("Stock Bajo", stock_bajo, "", PaletaColores.COLOR_ALERTA, PaletaColores.NEGRO_CARUMA, "Necesitan compra"),
            ("Por Caducar", por_caducar, "", "#FF9800", PaletaColores.BLANCO, "Próximos 7 días"),
            ("Caducados", caducados, "", PaletaColores.COLOR_ERROR, PaletaColores.BLANCO, "Retirar urgente"),
        ]
        
        for titulo, valor, icono, bg, fg, desc in tarjetas:
            frame, lbl = self.crear_tarjeta_alerta(self.frame_tarjetas, titulo, valor, icono, bg, fg, desc)
            frame.pack(side="left", padx=(0, 15))
            self.tarjetas_valores[titulo] = lbl
    
    def cargar_stock_bajo(self):
        """Carga la tabla de stock bajo"""
        for item in self.tabla_stock.get_children():
            self.tabla_stock.delete(item)
        
        datos = AlertasCRUD.obtener_alertas_stock_bajo()
        
        for d in datos:
            faltante = d[5] if d[5] > 0 else 0
            tag = "critico" if d[3] == 0 else "bajo"
            self.tabla_stock.insert("", "end", values=(
                d[0], d[1], d[2], d[3], d[4], faltante
            ), tags=(tag,))
        
        self.lbl_count_stock.config(text=f"{len(datos)} alerta{'s' if len(datos)!=1 else ''}")
    
    def cargar_por_caducar(self):
        """Carga la tabla de por caducar"""
        for item in self.tabla_caducar.get_children():
            self.tabla_caducar.delete(item)
        
        datos = AlertasCRUD.obtener_alertas_por_caducar(7)
        
        for d in datos:
            dias = d[5]
            tag = "urgente" if dias <= 2 else "pronto"
            fecha_str = d[4].strftime("%Y-%m-%d") if d[4] else ""
            self.tabla_caducar.insert("", "end", values=(
                d[0], d[1], d[2], d[3], fecha_str, dias
            ), tags=(tag,))
        
        self.lbl_count_caducar.config(text=f"{len(datos)} alerta{'s' if len(datos)!=1 else ''}")
    
    def cargar_caducados(self):
        """Carga la tabla de caducados"""
        for item in self.tabla_caducados.get_children():
            self.tabla_caducados.delete(item)
        
        datos = AlertasCRUD.obtener_alertas_caducados()
        
        for d in datos:
            fecha_str = d[4] if isinstance(d[4], str) else ""
            self.tabla_caducados.insert("", "end", values=(
                d[0], d[1], d[2], d[3], fecha_str, d[5]
            ), tags=("caducado",))
        
        self.lbl_count_caducados.config(text=f"{len(datos)} alerta{'s' if len(datos)!=1 else ''}")
    
    def cargar_historial(self):
        """Carga el historial de alertas"""
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)
        
        datos = AlertasCRUD.obtener_historial_alertas(50)
        
        for d in datos:
            fecha_str = d[1].strftime("%Y-%m-%d") if d[1] else ""
            self.tabla_historial.insert("", "end", values=(
                d[0], fecha_str, d[2], d[3], d[4]
            ))
    
    def generar_lista_compras(self):
        """Genera una lista de compras basada en stock bajo"""
        datos = AlertasCRUD.obtener_alertas_stock_bajo()
        
        if not datos:
            messagebox.showinfo("Lista de Compras", "No hay insumos con stock bajo")
            return
        
        # Crear ventana
        dlg = tk.Toplevel(self.parent)
        dlg.title("Lista de Compras")
        dlg.geometry("500x450")
        dlg.configure(bg=PaletaColores.COLOR_FONDO)
        dlg.transient(self.parent)
        
        x = self.parent.winfo_x() + self.parent.winfo_width()//2 - 250
        y = self.parent.winfo_y() + self.parent.winfo_height()//2 - 225
        dlg.geometry(f"+{x}+{y}")
        
        tk.Label(dlg, text="Lista de Compras", font=Fuentes.FUENTE_TITULOS,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(pady=15)
        
        tk.Label(dlg, text=f"Fecha: {date.today().strftime('%d/%m/%Y')}",
                 font=Fuentes.FUENTE_TEXTO, bg=PaletaColores.COLOR_FONDO,
                 fg=PaletaColores.GRIS_MEDIO).pack()
        
        # Área de texto con la lista
        frame_texto = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_texto.pack(fill="both", expand=True, padx=20, pady=15)
        
        texto = tk.Text(frame_texto, font=Fuentes.FUENTE_TEXTO, wrap="word",
                        relief="solid", bd=1, padx=10, pady=10)
        texto.pack(fill="both", expand=True)
        
        # Generar contenido
        contenido = "LISTA DE COMPRAS - CARUMA\n"
        contenido += "=" * 40 + "\n\n"
        
        for d in datos:
            faltante = max(0, d[5])
            contenido += f"☐ {d[1]}\n"
            contenido += f"   Categoría: {d[2]}\n"
            contenido += f"   Stock actual: {d[3]} | Mínimo: {d[4]}\n"
            contenido += f"   Cantidad sugerida: {faltante + 5} unidades\n\n"
        
        contenido += "=" * 40 + "\n"
        contenido += f"Total de productos: {len(datos)}\n"
        
        texto.insert("1.0", contenido)
        texto.config(state="disabled")
        
        # Botones
        frame_btns = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_btns.pack(pady=10)
        
        def copiar():
            dlg.clipboard_clear()
            dlg.clipboard_append(contenido)
            messagebox.showinfo("Copiado", "Lista copiada al portapapeles")
        
        tk.Button(frame_btns, text="Copiar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.DORADO_CARUMA, relief="flat", padx=15,
                  command=copiar).pack(side="left", padx=5)
        
        tk.Button(frame_btns, text="Cerrar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.GRIS_MEDIO, fg=PaletaColores.BLANCO,
                  relief="flat", padx=15, command=dlg.destroy).pack(side="left", padx=5)
    
    def generar_reporte(self):
        """Genera un reporte completo de alertas"""
        stock_bajo = AlertasCRUD.obtener_alertas_stock_bajo()
        por_caducar = AlertasCRUD.obtener_alertas_por_caducar(7)
        caducados = AlertasCRUD.obtener_alertas_caducados()
        
        dlg = tk.Toplevel(self.parent)
        dlg.title("Reporte de Alertas")
        dlg.geometry("550x500")
        dlg.configure(bg=PaletaColores.COLOR_FONDO)
        dlg.transient(self.parent)
        
        x = self.parent.winfo_x() + self.parent.winfo_width()//2 - 275
        y = self.parent.winfo_y() + self.parent.winfo_height()//2 - 250
        dlg.geometry(f"+{x}+{y}")
        
        tk.Label(dlg, text="Reporte de Alertas", font=Fuentes.FUENTE_TITULOS,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(pady=15)
        
        frame_texto = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_texto.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        texto = tk.Text(frame_texto, font=("Consolas", 10), wrap="word",
                        relief="solid", bd=1, padx=10, pady=10)
        sb = ttk.Scrollbar(frame_texto, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=sb.set)
        texto.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        # Generar reporte
        reporte = "=" * 50 + "\n"
        reporte += "       REPORTE DE ALERTAS - CARUMA\n"
        reporte += "=" * 50 + "\n"
        reporte += f"Fecha: {date.today().strftime('%d/%m/%Y')}\n\n"
        
        reporte += f"RESUMEN\n{'-'*50}\n"
        reporte += f"  Stock Bajo:    {len(stock_bajo)} productos\n"
        reporte += f"  Por Caducar:   {len(por_caducar)} productos\n"
        reporte += f"  Caducados:     {len(caducados)} productos\n"
        reporte += f"  TOTAL:         {len(stock_bajo)+len(por_caducar)+len(caducados)} alertas\n\n"
        
        if stock_bajo:
            reporte += f"STOCK BAJO\n{'-'*50}\n"
            for d in stock_bajo:
                reporte += f"  • {d[1]} ({d[2]})\n"
                reporte += f"    Stock: {d[3]} / Mínimo: {d[4]}\n"
            reporte += "\n"
        
        if por_caducar:
            reporte += f"POR CADUCAR (7 días)\n{'-'*50}\n"
            for d in por_caducar:
                reporte += f"  • {d[1]} - Caduca: {d[4]}\n"
                reporte += f"    Stock: {d[3]} piezas ({d[5]} días restantes)\n"
            reporte += "\n"
        
        if caducados:
            reporte += f"CADUCADOS (URGENTE)\n{'-'*50}\n"
            for d in caducados:
                reporte += f"  • {d[1]} - Caducó: {d[4]}\n"
                reporte += f"    Stock a retirar: {d[3]} piezas\n"
            reporte += "\n"
        
        reporte += "=" * 50 + "\n"
        reporte += "Fin del reporte\n"
        
        texto.insert("1.0", reporte)
        texto.config(state="disabled")
        
        frame_btns = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame_btns.pack(pady=10)
        
        def copiar():
            dlg.clipboard_clear()
            dlg.clipboard_append(reporte)
            messagebox.showinfo("Copiado", "Reporte copiado al portapapeles")
        
        tk.Button(frame_btns, text="Copiar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.DORADO_CARUMA, relief="flat", padx=15,
                  command=copiar).pack(side="left", padx=5)
        
        tk.Button(frame_btns, text="Cerrar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.GRIS_MEDIO, fg=PaletaColores.BLANCO,
                  relief="flat", padx=15, command=dlg.destroy).pack(side="left", padx=5)
    
    def limpiar_historial(self):
        """Limpia el historial de alertas"""
        if messagebox.askyesno("Confirmar", "¿Eliminar todo el historial de alertas?"):
            ok, msg = AlertasCRUD.limpiar_historial()
            if ok:
                self.cargar_historial()
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)


def abrir_ventana_alertas(parent):
    return VentanaAlertas(parent)