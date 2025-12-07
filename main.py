"""
SISTEMA DE GESTIÓN DE INSUMOS - CARUMA
Aplicación principal con Tkinter
"""

import tkinter as tk
from tkinter import messagebox
import sys

# Importaciones del proyecto
from config.constantes import *
from estilos.colores import PaletaColores
from estilos.fuentes import Fuentes
from utils.db_connection import Database
from utils.posiciones import Posiciones
from ventanas.formularios import GestorFormularios


class AplicacionCaruma(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.title(TITULO_WINDOW)
        self.geometry(f"{ANCHO_WINDOW}x{ALTO_WINDOW}")
        self.configure(background=PaletaColores.COLOR_FONDO)
        self.resizable(True, True)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Inicializar base de datos
        self.inicializar_bd()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def inicializar_bd(self):
        """Inicializa la conexión a la base de datos"""
        try:
            Database.initialize()
            print("✓ Conexión a base de datos establecida")
        except Exception as e:
            messagebox.showerror(
                "Error de Conexión",
                f"No se pudo conectar a la base de datos:\n{str(e)}\n\n" +
                "Verifique que PostgreSQL esté ejecutándose y las credenciales sean correctas."
            )
            self.destroy()
    
    def crear_interfaz(self):
        """Crea la interfaz principal"""
        # Encabezado
        self.encabezado = Posiciones.encabezado(
            self,
            "CARUMA",
            SUBTITULO
        )
        
        # Menú
        self.crear_menu()
        
        # Pantalla de inicio
        self.mostrar_pantalla_inicio()
        
        # Pie de página
        Posiciones.pie(
            self,
            f"© 2025 Caruma | Versión {VERSION}"
        )
    
    def crear_menu(self):
        """Crea el menú principal"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Inicio", command=self.mostrar_pantalla_inicio)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.cerrar_aplicacion)
        
        # Menú Catálogos
        menu_catalogos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Catálogos", menu=menu_catalogos)
        menu_catalogos.add_command(label="Categorías", command=self.abrir_categorias)
        menu_catalogos.add_command(label="Insumos", command=self.abrir_insumos)
        menu_catalogos.add_command(label="Servicios", command=self.abrir_servicios)
        
        # Menú Operaciones
        menu_operaciones = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Operaciones", menu=menu_operaciones)
        menu_operaciones.add_command(label="Gestión de Inventario", command=self.abrir_inventario)
        menu_operaciones.add_command(label="Alertas", command=self.abrir_alertas)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Manual de Usuario", command=self.mostrar_manual)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
    
    def mostrar_pantalla_inicio(self):
        """Muestra la pantalla de inicio con botones de acceso rápido"""
        GestorFormularios.limpiar_contenido()
        
        from ventanas.formularios import frame_contenido_actual
        import ventanas.formularios as vf
        vf.frame_contenido_actual = Posiciones.contenido(self)
        
        frame_principal = tk.Frame(
            vf.frame_contenido_actual,
            background=PaletaColores.COLOR_FONDO
        )
        frame_principal.pack(expand=True)
        
        # Título de bienvenida
        titulo = GestorFormularios.crear_etiqueta(
            frame_principal,
            "Sistema de Gestión de Insumos",
            es_titulo=True
        )
        titulo.pack(pady=(40, 60))
        
        # Frame para botones
        frame_botones = tk.Frame(
            frame_principal,
            background=PaletaColores.COLOR_FONDO
        )
        frame_botones.pack()
        
        # Botones de acceso rápido
        botones = [
            ("📋 Gestionar Categorías", self.abrir_categorias),
            ("📦 Gestionar Insumos", self.abrir_insumos),
            ("🍹 Gestionar Servicios", self.abrir_servicios),
            ("📊 Ver Inventario", self.abrir_inventario),
            ("⚠️ Ver Alertas", self.abrir_alertas),
        ]
        
        for i, (texto, comando) in enumerate(botones):
            fila = i // 2
            columna = i % 2
            
            boton = GestorFormularios.crear_boton(
                frame_botones,
                texto,
                comando,
                ancho=30
            )
            boton.grid(row=fila, column=columna, padx=15, pady=15)
    
    # ==================== MÓDULO DE CATEGORÍAS ====================
    def abrir_categorias(self):
        """Abre el módulo de gestión de categorías"""
        from ventanas.categorias import abrir_ventana_categorias
        abrir_ventana_categorias(self)
    
    # ==================== MÓDULO DE INSUMOS ====================
    def abrir_insumos(self):
        """Abre el módulo de gestión de insumos"""
        from ventanas.insumos import abrir_ventana_insumos
        abrir_ventana_insumos(self)
    
    # ==================== MÓDULO DE SERVICIOS ====================
    def abrir_servicios(self):
        """Abre el módulo de gestión de servicios"""
        from ventanas.servicios import abrir_ventana_servicios
        abrir_ventana_servicios(self)
    
    # ==================== MÓDULOS EN DESARROLLO ====================
    
    def abrir_inventario(self):
        messagebox.showinfo("En desarrollo", "Módulo de Inventario en desarrollo")
    
    def abrir_alertas(self):
        messagebox.showinfo("En desarrollo", "Módulo de Alertas en desarrollo")
    
    def mostrar_manual(self):
        messagebox.showinfo(
            "Manual de Usuario",
            "Manual de usuario en desarrollo.\n\n" +
            "Consulte la documentación en docs/manual_usuario.md"
        )
    
    def mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de Caruma",
            f"{TITULO_WINDOW}\n\n" +
            f"Versión: {VERSION}\n" +
            f"Autor: {AUTOR}\n\n" +
            "Sistema de gestión de insumos para barras de smoothies,\n" +
            "chicharrones preparados, tostitos preparados y más."
        )
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación de forma segura"""
        if messagebox.askokcancel("Salir", "¿Desea cerrar la aplicación?"):
            try:
                Database.close_all_connections()
            except:
                pass
            self.destroy()


def main():
    """Función principal"""
    try:
        app = AplicacionCaruma()
        app.mainloop()
    except Exception as e:
        print(f"Error fatal: {e}")
        messagebox.showerror("Error", f"Error al iniciar la aplicación:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()