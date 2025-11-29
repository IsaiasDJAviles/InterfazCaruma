"""
Clase base para gestión de formularios
"""

import tkinter as tk
from estilos.colores import PaletaColores

# Variable global para el frame de contenido actual
frame_contenido_actual = None

class GestorFormularios:
    
    @staticmethod
    def limpiar_contenido():
        """Limpia el contenido actual de la ventana"""
        global frame_contenido_actual
        if frame_contenido_actual is not None:
            frame_contenido_actual.destroy()
    
    @staticmethod
    def crear_boton(parent, texto, comando, ancho=20):
        """
        Crea un botón con el estilo Caruma
        """
        from estilos.fuentes import Fuentes
        
        boton = tk.Button(
            parent,
            text=texto,
            font=Fuentes.FUENTE_BOTONES,
            background=PaletaColores.COLOR_BOTONES,
            foreground=PaletaColores.COLOR_TEXTO_PRINCIPAL,
            activebackground=PaletaColores.COLOR_BOTONES_HOVER,
            activeforeground=PaletaColores.COLOR_TEXTO_PRINCIPAL,
            relief="flat",
            cursor="hand2",
            width=ancho,
            pady=10
        )
        boton.config(command=comando)
        
        # Efecto hover
        def on_enter(e):
            boton['background'] = PaletaColores.COLOR_BOTONES_HOVER
        
        def on_leave(e):
            boton['background'] = PaletaColores.COLOR_BOTONES
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
        
        return boton
    
    @staticmethod
    def crear_entrada(parent, ancho=40):
        """
        Crea un campo de entrada con estilo
        """
        from estilos.fuentes import Fuentes
        
        entrada = tk.Entry(
            parent,
            font=Fuentes.FUENTE_TEXTO,
            width=ancho,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=PaletaColores.GRIS_CLARO,
            highlightcolor=PaletaColores.DORADO_CARUMA
        )
        
        return entrada
    
    @staticmethod
    def crear_etiqueta(parent, texto, es_titulo=False):
        """
        Crea una etiqueta de texto
        """
        from estilos.fuentes import Fuentes
        
        fuente = Fuentes.FUENTE_TITULOS if es_titulo else Fuentes.FUENTE_TEXTO
        color = PaletaColores.DORADO_CARUMA if es_titulo else PaletaColores.COLOR_TEXTO_PRINCIPAL
        
        etiqueta = tk.Label(
            parent,
            text=texto,
            font=fuente,
            background=PaletaColores.COLOR_FONDO,
            foreground=color
        )
        
        return etiqueta