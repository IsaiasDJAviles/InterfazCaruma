"""
Paleta de colores basada en la imagen de Caruma
Colores extraídos: Negro, Dorado/Amarillo, Blanco
"""

class PaletaColores:
    # Colores principales de Caruma
    NEGRO_CARUMA = "#1A1A1A"          # Negro principal
    DORADO_CARUMA = "#D4AF37"         # Dorado/amarillo
    DORADO_CLARO = "#F4D03F"          # Amarillo claro
    BLANCO = "#FFFFFF"                # Blanco
    
    # Colores complementarios
    GRIS_OSCURO = "#2C2C2C"           # Para backgrounds alternos
    GRIS_CLARO = "#F5F5F5"            # Para fondos claros
    GRIS_MEDIO = "#808080"            # Para textos secundarios
    
    # Colores funcionales
    COLOR_EXITO = "#28A745"           # Verde para éxito
    COLOR_ALERTA = "#FFC107"          # Amarillo para advertencias
    COLOR_ERROR = "#DC3545"           # Rojo para errores
    COLOR_INFO = "#17A2B8"            # Azul para información
    
    # Aplicación de colores
    COLOR_ENCABEZADO = DORADO_CARUMA
    COLOR_FONDO = BLANCO
    COLOR_FONDO_ALTERNO = GRIS_CLARO
    COLOR_TEXTO_PRINCIPAL = NEGRO_CARUMA
    COLOR_TEXTO_ENCABEZADO = NEGRO_CARUMA
    COLOR_BOTONES = DORADO_CARUMA
    COLOR_BOTONES_HOVER = DORADO_CLARO
    COLOR_BORDES = GRIS_MEDIO