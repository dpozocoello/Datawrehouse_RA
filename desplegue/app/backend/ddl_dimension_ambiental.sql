/*
 * DDL: Dimensión y Puente de Intersecciones Ambientales (Biodiversidad) v1.4.1
 * Autor: Antigravity AI
 */
-- 1. Dimensión de Capas Ambientales
CREATE TABLE IF NOT EXISTS dw.dim_capa_ambiental (
    sk_capa SERIAL PRIMARY KEY,
    id_layer_origen INTEGER,
    -- ID de la capa en suia_iii.layers
    nombre_capa VARCHAR(200),
    descripcion_capa TEXT,
    categoria VARCHAR(50),
    -- SNAP, Patrimonio, Intangible, etc.
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 2. Tabla Puente (Bridge) para Intersecciones
-- Permite que un proyecto tenga múltiplas capas asociadas (Relación N:M)
CREATE TABLE IF NOT EXISTS dw.bridge_interseccion_ambiental (
    sk_proyecto INTEGER REFERENCES dw.dim_proyecto(sk_proyecto),
    sk_capa INTEGER REFERENCES dw.dim_capa_ambiental(sk_capa),
    detalle_interseccion TEXT,
    -- Nombre específico del área o bosque
    PRIMARY KEY (sk_proyecto, sk_capa, detalle_interseccion)
);
-- 3. Población Inicial de la Dimensión
INSERT INTO dw.dim_capa_ambiental (sk_capa, id_layer_origen, nombre_capa, categoria)
VALUES (0, NULL, 'SIN INTERSECCIÓN', 'N/A') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_capa_ambiental (id_layer_origen, nombre_capa, categoria)
VALUES (3, 'SNAP', 'Áreas Protegidas'),
    (2, 'ZONAS INTANGIBLES', 'Conservación Estricta'),
    (4, 'BOSQUES PROTECTORES', 'Biodiversidad'),
    (
        11,
        'PATRIMONIO FORESTAL DEL ESTADO',
        'Suelo Forestal'
    ) ON CONFLICT (sk_capa) DO NOTHING;
-- Índices para optimización de reportes
CREATE INDEX IF NOT EXISTS idx_bridge_proyecto ON dw.bridge_interseccion_ambiental(sk_proyecto);
CREATE INDEX IF NOT EXISTS idx_bridge_capa ON dw.bridge_interseccion_ambiental(sk_capa);