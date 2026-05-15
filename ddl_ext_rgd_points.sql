-- ==============================================================================
-- EXTENSIÓN MODELO DIMENSIONAL: PUNTOS DE GENERACIÓN RGD (FIX UNIQUE)
-- ==============================================================================

-- 1. Nueva Dimensión: Puntos de Generación
CREATE TABLE IF NOT EXISTS dw.dim_punto_generacion (
    punto_generacion_key BIGSERIAL PRIMARY KEY,
    source_id BIGINT, 
    source_system VARCHAR(50),
    waste_generator_id BIGINT, 
    point_name VARCHAR(500),
    x_coordinate NUMERIC(15,8),
    y_coordinate NUMERIC(15,8),
    province VARCHAR(100),
    canton VARCHAR(100),
    parroquia VARCHAR(100),
    sk_geografia BIGINT DEFAULT 0, 
    date_add TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE,
    UNIQUE (source_id, source_system),
    FOREIGN KEY (sk_geografia) REFERENCES dw.dim_geografia(sk_geografia)
);

-- 2. Modificar fact_waste_generation para incluir el punto y restricción de unicidad
DO $$
BEGIN
    -- Agregar columna si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema='dw' AND table_name='fact_waste_generation' AND column_name='punto_generacion_key') THEN
        ALTER TABLE dw.fact_waste_generation ADD COLUMN punto_generacion_key BIGINT DEFAULT 0;
    END IF;

    -- Eliminar restricción antigua si existe (para permitir la nueva granularidad)
    -- Asumiendo que la anterior era sobre (sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key)
    ALTER TABLE dw.fact_waste_generation DROP CONSTRAINT IF EXISTS fact_waste_generation_unique_key;
    
    -- Crear la nueva restricción de unicidad que incluye el punto
    -- Nota: Usamos una técnica de "DROP and ADD" para asegurar que la granularidad sea la correcta
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fact_waste_generation_pk_v2') THEN
        ALTER TABLE dw.fact_waste_generation ADD CONSTRAINT fact_waste_generation_pk_v2 
        UNIQUE (sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key, punto_generacion_key);
    END IF;
END $$;

-- 3. Crear índices para optimización
CREATE INDEX IF NOT EXISTS idx_fact_waste_pt_gen ON dw.fact_waste_generation(punto_generacion_key);
