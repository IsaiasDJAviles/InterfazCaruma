CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE insumos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    id_categoria INT REFERENCES categorias(id),
    piezas INT DEFAULT 0,
    contenido_por_pieza NUMERIC(10,2),
    unidad_contenido VARCHAR(20),
    fecha_caducidad DATE,
    alerta_piezas INT DEFAULT 0
);

CREATE TABLE servicios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE servicio_insumo (
    id SERIAL PRIMARY KEY,
    id_servicio INT REFERENCES servicios(id) ON DELETE CASCADE,
    id_insumo INT REFERENCES insumos(id) ON DELETE CASCADE,
    piezas_por_servicio NUMERIC(10,2),
    contenido_por_servicio NUMERIC(10,2),
    unidad_contenido VARCHAR(20)
);

CREATE TABLE alertas (
    id SERIAL PRIMARY KEY,
    id_insumo INT REFERENCES insumos(id),
    tipo VARCHAR(20),
    fecha_alerta DATE DEFAULT CURRENT_DATE,
    mensaje TEXT
);