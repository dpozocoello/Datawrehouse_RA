-- ==============================================================================
-- DDL Actualización v1.6: Registro Generador y Trazabilidad Financiera
-- ==============================================================================

-- 1. Extensión de Dimensión Generador
ALTER TABLE dw.dim_waste_generator 
ADD COLUMN IF NOT EXISTS ruc_generator character varying;

-- 2. Dimensión de Flujo de Procesos (BPM)
CREATE TABLE IF NOT EXISTS dw.dim_process_flow (
    sk_process_flow SERIAL PRIMARY KEY,
    process_name character varying(255),
    process_type character varying(100), -- Registro Generador, Declaración, etc.
    process_status character varying(100)
);

-- Inyectar SK=0 para huérfanos
INSERT INTO dw.dim_process_flow (sk_process_flow, process_name, process_type, process_status)
VALUES (0, 'N/A', 'N/A', 'N/A')
ON CONFLICT (sk_process_flow) DO NOTHING;

-- 3. Fact Table: Trazabilidad de Pagos Históricos
CREATE TABLE IF NOT EXISTS dw.fact_payment_traceability (
    id_payment_trace SERIAL PRIMARY KEY,
    sk_proyecto integer NOT NULL REFERENCES dw.dim_proyecto(sk_proyecto),
    sk_pago integer NOT NULL REFERENCES dw.dim_pago(sk_pago),
    sk_tiempo integer NOT NULL REFERENCES dw.dim_tiempo(sk_tiempo),
    id_online_payment_historical bigint,
    retired_value numeric(15,2),
    value_updated numeric(15,2),
    delta_value numeric(15,2),
    update_date timestamp without time zone,
    description text,
    fecha_carga timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_fpt_proyecto ON dw.fact_payment_traceability(sk_proyecto);
CREATE INDEX IF NOT EXISTS idx_fpt_pago ON dw.fact_payment_traceability(sk_pago);
CREATE INDEX IF NOT EXISTS idx_fpt_tiempo ON dw.fact_payment_traceability(sk_tiempo);
