-- ==============================================================================
-- Proyecto: Registro Generador de Desechos (RGD) - Refactorización ETL
-- Script: setup_rgd_control.sql
-- Descripción:
-- 1. Agrega columnas de control a dim_waste_generator para soporte SCD (Tipo 1/2)
-- 2. Crea tabla de rechazos (staging_rejects) para Data Quality
-- 3. Crea tabla de log (etl_log) para trazabilidad de ejecuciones
-- ==============================================================================

-- 1. Modificar dw.dim_waste_generator (SCD Tipo 1 / Tipo 2)
-- Agregamos las columnas sólo si no existen.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema='dw' AND table_name='dim_waste_generator' AND column_name='is_active') THEN
        ALTER TABLE dw.dim_waste_generator ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema='dw' AND table_name='dim_waste_generator' AND column_name='last_update') THEN
        ALTER TABLE dw.dim_waste_generator ADD COLUMN last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- 2. Crear tabla de rechazos por mala calidad de datos (Data Quality)
CREATE TABLE IF NOT EXISTS dw.staging_rejects (
    reject_id SERIAL PRIMARY KEY,
    source_system VARCHAR(50) DEFAULT 'RGD',
    record_payload TEXT NOT NULL, -- El registro JSON o texto crudo
    reject_reason VARCHAR(255) NOT NULL, -- Motivo del rechazo (ej. Cantidad negativa)
    rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Crear tabla de Logs para Trazabilidad ETL
CREATE TABLE IF NOT EXISTS dw.etl_log (
    log_id SERIAL PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'STARTED', 'SUCCESS', 'FAILED'
    rows_read INTEGER DEFAULT 0,
    rows_written INTEGER DEFAULT 0,
    rows_rejected INTEGER DEFAULT 0,
    error_message TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP
);

COMMENT ON TABLE dw.etl_log IS 'Tabla de auditoría para ejecuciones del pipeline ETL del RGD';
COMMENT ON TABLE dw.staging_rejects IS 'Tabla de cuarentena para registros que fallan las reglas de calidad (Non-Breaking)';
