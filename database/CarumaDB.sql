-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-- CARUMA - Sistema de Gestión de Insumos
-- Script de creación de base de datos
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-- Datos de ejemplo para categorías
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-- Datos de ejemplo para insumos
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

INSERT INTO insumos (nombre, id_categoria, piezas, contenido_por_pieza, unidad_contenido, fecha_caducidad, alerta_piezas)
VALUES
('Plátano', 1, 25, 1.00, 'pieza', '2025-01-20', 10),
('Manzana Verde', 1, 40, 1.00, 'pieza', '2025-02-05', 15),
('Espinaca', 2, 12, 200.00, 'gramos', '2024-12-18', 5),
('Yogurt Natural', 3, 18, 250.00, 'ml', '2024-12-10', 8),
('Leche Deslactosada', 3, 30, 1.00, 'litro', '2024-12-15', 10),
('Salsa Chamoy', 4, 20, 355.00, 'ml', '2026-03-01', 5),
('Cacahuates Enchilados', 5, 50, 100.00, 'gramos', '2025-08-10', 20),
('Botella de Agua', 6, 80, 600.00, 'ml', NULL, 20),
('Canela Molida', 7, 15, 50.00, 'gramos', '2026-11-01', 5),
('Vasos Plásticos 16oz', 8, 200, 1.00, 'pieza', NULL, 50);

-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-- Índices para mejorar rendimiento
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CREATE INDEX IF NOT EXISTS idx_insumos_categoria ON insumos(id_categoria);
CREATE INDEX IF NOT EXISTS idx_servicio_insumo_servicio ON servicio_insumo(id_servicio);
CREATE INDEX IF NOT EXISTS idx_servicio_insumo_insumo ON servicio_insumo(id_insumo);
CREATE INDEX IF NOT EXISTS idx_alertas_insumo ON alertas(id_insumo);


