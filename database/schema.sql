-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-- CARUMA - Sistema de Gestión de Insumos
-- Script de creación de base de datos SQLite
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

-- Tabla de insumos
CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    id_categoria INTEGER REFERENCES categorias(id),
    piezas INTEGER DEFAULT 0,
    contenido_por_pieza REAL,
    unidad_contenido VARCHAR(20),
    fecha_caducidad DATE,
    alerta_piezas INTEGER DEFAULT 0
);

-- Tabla de servicios
CREATE TABLE IF NOT EXISTS servicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- Tabla de relación servicio-insumo
CREATE TABLE IF NOT EXISTS servicio_insumo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_servicio INTEGER REFERENCES servicios(id) ON DELETE CASCADE,
    id_insumo INTEGER REFERENCES insumos(id) ON DELETE CASCADE,
    piezas_por_servicio REAL,
    contenido_por_servicio REAL,
    unidad_contenido VARCHAR(20)
);

-- Tabla de alertas
CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_insumo INTEGER REFERENCES insumos(id),
    tipo VARCHAR(20),
    fecha_alerta DATE DEFAULT CURRENT_DATE,
    mensaje TEXT
);

-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-- Datos de ejemplo para categorías
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

INSERT OR IGNORE INTO categorias (nombre) VALUES 
    ('Frutas'),
    ('Verduras'),
    ('Lácteos'),
    ('Salsas y Aderezos'),
    ('Snacks'),
    ('Bebidas'),
    ('Especias'),
    ('Desechables');

-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-- Datos de ejemplo para insumos
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

INSERT OR IGNORE INTO insumos (nombre, id_categoria, piezas, contenido_por_pieza, unidad_contenido, fecha_caducidad, alerta_piezas)
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