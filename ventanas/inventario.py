"""
Módulo de Gestión de Inventario - CARUMA
Vista consolidada del stock con reportes y estadísticas
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


class InventarioCRUD:
    """Consultas para el inventario"""
    
    @staticmethod
    def obtener_resumen():
        """Obtiene estadísticas generales del inventario"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_insumos,
                    COALESCE(SUM(piezas), 0) as total_piezas,
                    COUNT(CASE WHEN piezas <= alerta_piezas AND alerta_piezas > 0 THEN 1 END) as stock_bajo,
                    COUNT(CASE WHEN fecha_caducidad IS NOT NULL 
                          AND fecha_caducidad <= CURRENT_DATE + 7 
                          AND fecha_caducidad >= CURRENT_DATE THEN 1 END) as por_caducar,
                    COUNT(CASE WHEN fecha_caducidad IS NOT NULL 
                          AND fecha_caducidad < CURRENT_DATE THEN 1 END) as caducados
                FROM insumos
            """
            resultado = Database.execute_query(query)
            return resultado[0] if resultado else (0, 0, 0, 0, 0)
        except Exception as e:
            print(f"Error: {e}")
            return (0, 0, 0, 0, 0)
    
    @staticmethod
    def obtener_por_categoria():
        """Obtiene inventario agrupado por categoría"""
        try:
            query = """
                SELECT 
                    COALESCE(c.nombre, 'Sin categoría') as categoria,
                    COUNT(i.id) as num_insumos,
                    COALESCE(SUM(i.piezas), 0) as total_piezas,
                    COUNT(CASE WHEN i.piezas <= i.alerta_piezas AND i.alerta_piezas > 0 THEN 1 END) as alertas
                FROM insumos i
                LEFT JOIN categorias c ON i.id_categoria = c.id
                GROUP BY c.id, c.nombre
                ORDER BY c.nombre
            """
            return Database.execute_query(query)
        except:
            return []
    
    @staticmethod
    def obtener_inventario_completo(filtro=None, orden="nombre"):
        """Obtiene el inventario completo con filtros"""
        try:
            where_clause = ""
            params = []
            
            if filtro == "stock_bajo":
                where_clause = "WHERE i.piezas <= i.alerta_piezas AND i.alerta_piezas > 0"
            elif filtro == "por_caducar":
                where_clause = "WHERE i.fecha_caducidad IS NOT NULL AND i.fecha_caducidad <= CURRENT_DATE + 7 AND i.fecha_caducidad >= CURRENT_DATE"
            elif filtro == "caducados":
                where_clause = "WHERE i.fecha_caducidad IS NOT NULL AND i.fecha_caducidad < CURRENT_DATE"
            elif filtro == "sin_stock":
                where_clause = "WHERE i.piezas = 0"
            
            orden_clause = "ORDER BY i.nombre"
            if orden == "categoria":
                orden_clause = "ORDER BY c.nombre, i.nombre"
            elif orden == "piezas_asc":
                orden_clause = "ORDER BY i.piezas ASC"
            elif orden == "piezas_desc":
                orden_clause = "ORDER BY i.piezas DESC"
            elif orden == "caducidad":
                orden_clause = "ORDER BY i.fecha_caducidad ASC NULLS LAST"
            
            query = f"""
                SELECT 
                    i.id,
                    i.nombre,
                    COALESCE(c.nombre, 'Sin categoría') as categoria,
                    i.piezas,
                    i.contenido_por_pieza,
                    i.unidad_contenido,
                    i.fecha_caducidad,
                    i.alerta_piezas,
                    CASE 
                        WHEN i.fecha_caducidad < CURRENT_DATE THEN 'CADUCADO'
                        WHEN i.piezas <= i.alerta_piezas AND i.alerta_piezas > 0 THEN 'STOCK BAJO'
                        WHEN i.fecha_caducidad <= CURRENT_DATE + 7 THEN 'POR CADUCAR'
                        ELSE 'OK'
                    END as estado
                FROM insumos i
                LEFT JOIN categorias c ON i.id_categoria = c.id
                {where_clause}
                {orden_clause}
            """
            return Database.execute_query(query)
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def obtener_valor_inventario():
        """Calcula estadísticas de contenido total"""
        try:
            query = """
                SELECT 
                    unidad_contenido,
                    SUM(piezas * COALESCE(contenido_por_pieza, 1)) as total
                FROM insumos
                WHERE unidad_contenido IS NOT NULL
                GROUP BY unidad_contenido
                ORDER BY unidad_contenido
            """
            return Database.execute_query(query)
        except:
            return []
    
    @staticmethod
    def obtener_insumos_mas_usados():
        """Obtiene los insumos más utilizados en servicios"""
        try:
            query = """
                SELECT 
                    i.nombre,
                    COUNT(si.id) as num_servicios,
                    i.piezas as stock_actual
                FROM insumos i
                JOIN servicio_insumo si ON i.id = si.id_insumo
                GROUP BY i.id, i.nombre, i.piezas
                ORDER BY num_servicios DESC
                LIMIT 10
            """
            return Database.execute_query(query)
        except:
            return []


class VentanaInventario:
    """Ventana de gestión de inventario"""
    
    def __init__(self, parent):
        self.parent = parent
        self.filtro_actual = None
        self.orden_actual = "nombre"
        self.mostrar()
    
    def mostrar(self):
        GestorFormularios.limpiar_contenido()
        vf.frame_contenido_actual = Posiciones.contenido(self.parent)
        
        self.frame_principal = tk.Frame(vf.frame_contenido_actual, bg=PaletaColores.COLOR_FONDO, padx=20, pady=15)
        self.frame_principal.pack(fill="both", expand=True)
        
        self.crear_titulo()
        self.crear_panel_resumen()
        self.crear_barra_herramientas()
        self.crear_tabla_inventario()
        self.cargar_datos()
    
    def crear_titulo(self):
        frame = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame.pack(fill="x", pady=(0, 15))
        tk.Label(frame, text="Gestión de Inventario", font=Fuentes.FUENTE_TITULOS,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(side="left")
        
        # Botón actualizar
        tk.Button(frame, text="Actualizar", font=Fuentes.FUENTE_MENU,
                  bg=PaletaColores.DORADO_CARUMA, relief="flat", cursor="hand2",
                  padx=10, command=self.cargar_datos).pack(side="right")
    
    def crear_panel_resumen(self):
        """Panel con tarjetas de resumen"""
        frame_resumen = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame_resumen.pack(fill="x", pady=(0, 15))
        
        # Contenedor de tarjetas
        self.frame_tarjetas = tk.Frame(frame_resumen, bg=PaletaColores.COLOR_FONDO)
        self.frame_tarjetas.pack(fill="x")
        
        # Las tarjetas se crearán dinámicamente
        self.tarjetas = {}
    
    def crear_tarjeta(self, parent, titulo, valor, color_fondo, color_texto, icono, comando=None):
        """Crea una tarjeta de resumen"""
        frame = tk.Frame(parent, bg=color_fondo, padx=15, pady=10, cursor="hand2" if comando else "")
        
        # Icono y título
        frame_top = tk.Frame(frame, bg=color_fondo)
        frame_top.pack(fill="x")
        
        tk.Label(frame_top, text=icono, font=("Segoe UI", 16), bg=color_fondo).pack(side="left")
        tk.Label(frame_top, text=titulo, font=Fuentes.FUENTE_MENU, bg=color_fondo,
                 fg=color_texto).pack(side="left", padx=(5, 0))
        
        # Valor
        lbl_valor = tk.Label(frame, text=str(valor), font=("Segoe UI", 24, "bold"),
                             bg=color_fondo, fg=color_texto)
        lbl_valor.pack(pady=(5, 0))
        
        if comando:
            frame.bind("<Button-1>", lambda e: comando())
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e: comando())
                for subchild in child.winfo_children():
                    subchild.bind("<Button-1>", lambda e: comando())
        
        return frame, lbl_valor
    
    def crear_barra_herramientas(self):
        """Barra de filtros y ordenamiento"""
        frame_tools = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame_tools.pack(fill="x", pady=(0, 10))
        
        # Filtros rápidos
        tk.Label(frame_tools, text="Filtrar:", font=Fuentes.FUENTE_TEXTO,
                 bg=PaletaColores.COLOR_FONDO).pack(side="left", padx=(0, 5))
        
        filtros = [
            ("Todos", None),
            ("Stock Bajo", "stock_bajo"),
            ("Por Caducar", "por_caducar"),
            ("Caducados", "caducados"),
            ("Sin Stock", "sin_stock")
        ]
        
        self.btns_filtro = {}
        for texto, filtro in filtros:
            btn = tk.Button(frame_tools, text=texto, font=Fuentes.FUENTE_MENU,
                           bg=PaletaColores.GRIS_CLARO, relief="flat", cursor="hand2",
                           padx=8, command=lambda f=filtro: self.aplicar_filtro(f))
            btn.pack(side="left", padx=2)
            self.btns_filtro[filtro] = btn
        
        # Separador
        tk.Frame(frame_tools, width=20, bg=PaletaColores.COLOR_FONDO).pack(side="left")
        
        # Ordenar por
        tk.Label(frame_tools, text="Ordenar:", font=Fuentes.FUENTE_TEXTO,
                 bg=PaletaColores.COLOR_FONDO).pack(side="left", padx=(0, 5))
        
        self.cmb_orden = ttk.Combobox(frame_tools, state="readonly", width=15,
                                       values=["Nombre", "Categoría", "Menos stock", "Más stock", "Caducidad"])
        self.cmb_orden.current(0)
        self.cmb_orden.pack(side="left")
        self.cmb_orden.bind("<<ComboboxSelected>>", self.cambiar_orden)
        
        # Contador
        self.lbl_contador = tk.Label(frame_tools, text="", font=Fuentes.FUENTE_MENU,
                                      bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.GRIS_MEDIO)
        self.lbl_contador.pack(side="right")
    
    def crear_tabla_inventario(self):
        """Tabla principal del inventario"""
        frame_tabla = tk.Frame(self.frame_principal, bg=PaletaColores.COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True)
        
        # Estilo
        style = ttk.Style()
        style.configure("Inv.Treeview", rowheight=28, font=Fuentes.FUENTE_TEXTO)
        style.configure("Inv.Treeview.Heading", background=PaletaColores.DORADO_CARUMA,
                        font=Fuentes.FUENTE_BOTONES, padding=5)
        style.map("Inv.Treeview", background=[("selected", PaletaColores.DORADO_CLARO)])
        
        cols = ("id", "nombre", "categoria", "piezas", "contenido", "unidad", "caducidad", "estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings", style="Inv.Treeview")
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.heading("piezas", text="Piezas")
        self.tabla.heading("contenido", text="Contenido")
        self.tabla.heading("unidad", text="Unidad")
        self.tabla.heading("caducidad", text="Caducidad")
        self.tabla.heading("estado", text="Estado")
        
        self.tabla.column("id", width=40, anchor="center")
        self.tabla.column("nombre", width=180, anchor="w")
        self.tabla.column("categoria", width=110, anchor="w")
        self.tabla.column("piezas", width=60, anchor="center")
        self.tabla.column("contenido", width=70, anchor="center")
        self.tabla.column("unidad", width=55, anchor="center")
        self.tabla.column("caducidad", width=85, anchor="center")
        self.tabla.column("estado", width=90, anchor="center")
        
        # Scrollbar
        sb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        # Tags para colores
        self.tabla.tag_configure("ok", background="#E8F5E9")
        self.tabla.tag_configure("stock_bajo", background="#FFCDD2")
        self.tabla.tag_configure("por_caducar", background="#FFE0B2")
        self.tabla.tag_configure("caducado", background="#F8BBD9")
        
        # Doble clic para ir a editar
        self.tabla.bind("<Double-1>", self.ir_a_insumo)
    
    def cargar_datos(self):
        """Carga todos los datos del inventario"""
        self.cargar_resumen()
        self.cargar_inventario()
    
    def cargar_resumen(self):
        """Carga las tarjetas de resumen"""
        # Limpiar tarjetas anteriores
        for widget in self.frame_tarjetas.winfo_children():
            widget.destroy()
        
        resumen = InventarioCRUD.obtener_resumen()
        total_insumos, total_piezas, stock_bajo, por_caducar, caducados = resumen
        
        # Crear tarjetas
        tarjetas_config = [
            ("Total Insumos", total_insumos, PaletaColores.GRIS_CLARO, PaletaColores.NEGRO_CARUMA, None),
            ("Total Piezas", total_piezas, PaletaColores.COLOR_INFO, PaletaColores.BLANCO, None),
            ("Stock Bajo", stock_bajo, PaletaColores.COLOR_ERROR, PaletaColores.BLANCO, lambda: self.aplicar_filtro("stock_bajo")),
            ("Por Caducar", por_caducar, PaletaColores.COLOR_ALERTA, PaletaColores.NEGRO_CARUMA, lambda: self.aplicar_filtro("por_caducar")),
            ("Caducados", caducados, "#9C27B0", PaletaColores.BLANCO, lambda: self.aplicar_filtro("caducados")),
        ]
        
        for titulo, valor, bg, fg, icono, cmd in tarjetas_config:
            frame, lbl = self.crear_tarjeta(self.frame_tarjetas, titulo, valor, bg, fg, icono, cmd)
            frame.pack(side="left", padx=(0, 10), fill="y")
            self.tarjetas[titulo] = lbl
    
    def cargar_inventario(self):
        """Carga la tabla de inventario"""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        datos = InventarioCRUD.obtener_inventario_completo(self.filtro_actual, self.orden_actual)
        
        for inv in datos:
            # Determinar tag según estado
            estado = inv[8]
            if estado == "CADUCADO":
                tag = "caducado"
            elif estado == "STOCK BAJO":
                tag = "stock_bajo"
            elif estado == "POR CADUCAR":
                tag = "por_caducar"
            else:
                tag = "ok"
            
            # Formatear fecha
            fecha_str = inv[6].strftime("%Y-%m-%d") if inv[6] else ""
            
            self.tabla.insert("", "end", values=(
                inv[0],  # id
                inv[1],  # nombre
                inv[2],  # categoria
                inv[3] or 0,  # piezas
                inv[4] or "",  # contenido
                inv[5] or "",  # unidad
                fecha_str,  # caducidad
                estado  # estado
            ), tags=(tag,))
        
        self.lbl_contador.config(text=f"{len(datos)} insumo{'s' if len(datos)!=1 else ''}")
        self.actualizar_botones_filtro()
    
    def aplicar_filtro(self, filtro):
        """Aplica un filtro al inventario"""
        self.filtro_actual = filtro
        self.cargar_inventario()
    
    def actualizar_botones_filtro(self):
        """Actualiza el estado visual de los botones de filtro"""
        for f, btn in self.btns_filtro.items():
            if f == self.filtro_actual:
                btn.config(bg=PaletaColores.DORADO_CARUMA)
            else:
                btn.config(bg=PaletaColores.GRIS_CLARO)
    
    def cambiar_orden(self, event=None):
        """Cambia el orden de la tabla"""
        opciones = {
            0: "nombre",
            1: "categoria",
            2: "piezas_asc",
            3: "piezas_desc",
            4: "caducidad"
        }
        self.orden_actual = opciones.get(self.cmb_orden.current(), "nombre")
        self.cargar_inventario()
    
    def ir_a_insumo(self, event):
        """Abre el módulo de insumos al hacer doble clic"""
        sel = self.tabla.selection()
        if sel:
            from ventanas.insumos import abrir_ventana_insumos
            abrir_ventana_insumos(self.parent)


class VentanaInventarioDetalle:
    """Vista detallada por categorías"""
    
    @staticmethod
    def mostrar_por_categorias(parent):
        """Muestra un resumen por categorías"""
        datos = InventarioCRUD.obtener_por_categoria()
        
        dlg = tk.Toplevel(parent)
        dlg.title("Inventario por Categorías")
        dlg.geometry("500x400")
        dlg.configure(bg=PaletaColores.COLOR_FONDO)
        dlg.transient(parent)
        dlg.grab_set()
        
        x = parent.winfo_x() + parent.winfo_width()//2 - 250
        y = parent.winfo_y() + parent.winfo_height()//2 - 200
        dlg.geometry(f"+{x}+{y}")
        
        tk.Label(dlg, text="Inventario por Categorías", font=Fuentes.FUENTE_TITULOS,
                 bg=PaletaColores.COLOR_FONDO, fg=PaletaColores.DORADO_CARUMA).pack(pady=15)
        
        # Tabla
        frame = tk.Frame(dlg, bg=PaletaColores.COLOR_FONDO)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        cols = ("categoria", "insumos", "piezas", "alertas")
        tabla = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        
        tabla.heading("categoria", text="Categoría")
        tabla.heading("insumos", text="Insumos")
        tabla.heading("piezas", text="Total Piezas")
        tabla.heading("alertas", text="Alertas")
        
        tabla.column("categoria", width=180, anchor="w")
        tabla.column("insumos", width=80, anchor="center")
        tabla.column("piezas", width=100, anchor="center")
        tabla.column("alertas", width=80, anchor="center")
        
        for d in datos:
            tabla.insert("", "end", values=d)
        
        tabla.pack(fill="both", expand=True)
        
        tk.Button(dlg, text="Cerrar", font=Fuentes.FUENTE_BOTONES,
                  bg=PaletaColores.GRIS_MEDIO, fg=PaletaColores.BLANCO,
                  relief="flat", padx=20, command=dlg.destroy).pack(pady=10)


def abrir_ventana_inventario(parent):
    return VentanaInventario(parent)