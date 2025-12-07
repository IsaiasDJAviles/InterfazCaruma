"""
Posiciones y frames base para las ventanas
"""

import os
import sys
import tkinter as tk
from estilos.colores import PaletaColores

class Posiciones:
    
    @staticmethod
    def encabezado(window, titulo, subtitulo=""):
        """
        Crea el frame de encabezado con estilo Caruma
        """
        encabezado = tk.Frame(
            window,
            background=PaletaColores.COLOR_ENCABEZADO,
            height=120
        )
        encabezado.pack(fill="x", expand=False, side="top")
        encabezado.pack_propagate(False)
        
        # Título principal
        from estilos.fuentes import Fuentes
        titulo_label = tk.Label(
            encabezado,
            text=titulo,
            font=Fuentes.FUENTE_ENCABEZADO,
            background=PaletaColores.COLOR_ENCABEZADO,
            foreground=PaletaColores.COLOR_TEXTO_ENCABEZADO
        )
        titulo_label.pack(expand=True, pady=(20, 5))
        
        # Subtítulo (opcional)
        if subtitulo:
            subtitulo_label = tk.Label(
                encabezado,
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