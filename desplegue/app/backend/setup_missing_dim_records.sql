-- ==============================================================================
-- setup_missing_dim_records.sql (v1.0.0)
-- ==============================================================================
-- Garantiza que existan los registros -1 (N/A) en las dimensiones críticas
-- para permitir la carga de hechos con registros huérfanos.
-- ==============================================================================

-- 1. Dimensión Proyecto
INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
SELECT -1, 'N/A', 'PROYECTO NO ENCONTRADO / HUÉRFANO'
WHERE NOT EXISTS (SELECT 1 FROM dw.dim_proyecto WHERE sk_proyecto = -1);

-- 2. Dimensión Geografía
INSERT INTO dw.dim_geografia (sk_geografia, codigo_parroquia, nombre_parroquia)
SELECT -1, 'N/A', 'GEOGRAFÍA NO ENCONTRADA'
WHERE NOT EXISTS (SELECT 1 FROM dw.dim_geografia WHERE sk_geografia = -1);

-- 3. Dimensión Área (Por si acaso)
INSERT INTO dw.dim_area (sk_area, area_nombre)
SELECT -1, 'ÁREA NO DEFINIDA'
WHERE NOT EXISTS (SELECT 1 FROM dw.dim_area WHERE sk_area = -1);

-- Confirmación
ANALYZE dw.dim_proyecto;
ANALYZE dw.dim_geografia;
ANALYZE dw.dim_area;
