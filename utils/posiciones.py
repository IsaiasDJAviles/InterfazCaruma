"""
Posiciones y frames base para las ventanas
"""

import os
import sys
import tkinter as tk
from estilos.colores import PaletaColores


class Posiciones:
    
    # Variable de clase para almacenar el logo
    _logo_caruma = None
    
    @staticmethod
    def ruta_recurso(ruta_relativa):
        """Obtiene la ruta correcta para recursos (compatible con PyInstaller)"""
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, ruta_relativa)
    
    @classmethod
    def obtener_logo(cls):
        """Carga el logo solo una vez y lo almacena"""
        if cls._logo_caruma is None:
            try:
                ruta_logo = cls.ruta_recurso("assets/Caruma_logo.png")
                if os.path.exists(ruta_logo):
                    cls._logo_caruma = tk.PhotoImage(file=ruta_logo)
                    # Redimensionar si es necesario (subsample reduce, zoom aumenta)
                    # Ajusta estos valores según el tamaño de tu logo
                    cls._logo_caruma = cls._logo_caruma.subsample(3, 3)
                else:
                    print(f"Logo no encontrado en: {ruta_logo}")
                    cls._logo_caruma = None
            except Exception as e:
                print(f"Error al cargar logo: {e}")
                cls._logo_caruma = None
        return cls._logo_caruma
    
    @staticmethod
    def encabezado(window, titulo, subtitulo=""):
        """
        Crea el frame de encabezado con estilo Caruma
        """
        from estilos.fuentes import Fuentes
        
        encabezado = tk.Frame(
            window,
            background=PaletaColores.NEGRO_CARUMA,
            height=150  # Aumentado para dar espacio al logo
        )
        encabezado.pack(fill="x", expand=False, side="top")
        encabezado.pack_propagate(False)
        
        # Frame interno para centrar contenido
        frame_contenido = tk.Frame(encabezado, background=PaletaColores.NEGRO_CARUMA)
        frame_contenido.pack(expand=True)
        
        # Intentar cargar el logo
        logo = Posiciones.obtener_logo()
        
        if logo:
            # Frame horizontal para logo + título
            frame_titulo = tk.Frame(frame_contenido, background=PaletaColores.NEGRO_CARUMA)
            frame_titulo.pack(pady=(15, 5))
            
            # Logo a la izquierda
            logo_label = tk.Label(
                frame_titulo,
                image=logo,
                background=PaletaColores.NEGRO_CARUMA
            )
            logo_label.image = logo  # Mantener referencia para evitar garbage collection
            logo_label.pack(side="left", padx=(0, 15))
            
        else:
            # Sin logo, solo título centrado
            titulo_label = tk.Label(
                frame_contenido,
                text=titulo,
                font=Fuentes.FUENTE_ENCABEZADO,
                background=PaletaColores.COLOR_ENCABEZADO,
                foreground=PaletaColores.COLOR_TEXTO_ENCABEZADO
            )
            titulo_label.pack(pady=(20, 5))
        
        # Subtítulo (opcional)
        if subtitulo:
            subtitulo_label = tk.Label(
                frame_contenido,
                text=subtitulo,
                font=Fuentes.FUENTE_SUBTITULO,
                background=PaletaColores.COLOR_ENCABEZADO,
                foreground=PaletaColores.COLOR_TEXTO_ENCABEZADO
            )
            subtitulo_label.pack(pady=(0, 15))
        
        return encabezado
    
    @staticmethod
    def contenido(window):
        """
        Crea el frame de contenido principal
        """
        contenido = tk.Frame(
            window,
            background=PaletaColores.COLOR_FONDO
        )
        contenido.pack(fill="both", expand=True)
        
        return contenido
    
    @staticmethod
    def pie(window, texto=""):
        """
        Crea el frame de pie de página
        """
        pie = tk.Frame(
            window,
            background=PaletaColores.GRIS_OSCURO,
            height=40
        )
        pie.pack(fill="x", expand=False, side="bottom")
        pie.pack_propagate(False)
        
        if texto:
            from estilos.fuentes import Fuentes
            label_pie = tk.Label(
                pie,
                text=texto,
                font=Fuentes.FUENTE_TEXTO,
                background=PaletaColores.GRIS_OSCURO,
                foreground=PaletaColores.BLANCO
            )
            label_pie.pack(expand=True)
        
        return pie