-- =============================================
-- CARUMA - Sistema de Gestión de Insumos
-- Script de creación de base de datos
-- =============================================

-- Crear base de datos (ejecutar por separado si es necesario)
-- CREATE DATABASE CarumaDB;

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

-- Tabla de insumos
CREATE TABLE IF NOT EXISTS insumos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    id_categoria INT REFERENCES categorias(id),
    piezas INT DEFAULT 0,
    contenido_por_pieza NUMERIC(10,2),
    unidad_contenido VARCHAR(20),
    fecha_caducidad DATE,
    alerta_piezas INT DEFAULT 0
);

-- Tabla de servicios
CREATE TABLE IF NOT EXISTS servicios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- Tabla de relación servicio-insumo
CREATE TABLE IF NOT EXISTS servicio_insumo (
    id SERIAL PRIMARY KEY,
    id_servicio INT REFERENCES servicios(id) ON DELETE CASCADE,
    id_insumo INT REFERENCES insumos(id) ON DELETE CASCADE,
    piezas_por_servicio NUMERIC(10,2),
    contenido_por_servicio NUMERIC(10,2),
    unidad_contenido VARCHAR(20)
);

-- Tabla de alertas
CREATE TABLE IF NOT EXISTS alertas (
    id SERIAL PRIMARY KEY,
    id_insumo INT REFERENCES insumos(id),
    tipo VARCHAR(20),
    fecha_alerta DATE DEFAULT CURRENT_DATE,
    mensaje TEXT
);

-- =============================================
-- Datos de ejemplo para categorías
-- =============================================

INSERT INTO categorias (nombre) VALUES 
    ('Frutas'),
    ('Verduras'),
    ('Lácteos'),
    ('Salsas y Aderezos'),
    ('Snacks'),
    ('Bebidas'),
    ('Especias'),
    ('Desechables')
ON CONFLICT (nombre) DO NOTHING;

-- =============================================
-- Índices para mejorar rendimiento
-- =============================================

CREATE INDEX IF NOT EXISTS idx_insumos_categoria ON insumos(id_categoria);
CREATE INDEX IF NOT EXISTS idx_servicio_insumo_servicio ON servicio_insumo(id_servicio);
CREATE INDEX IF NOT EXISTS idx_servicio_insumo_insumo ON servicio_insumo(id_insumo);
CREATE INDEX IF NOT EXISTS idx_alertas_insumo ON alertas(id_insumo);