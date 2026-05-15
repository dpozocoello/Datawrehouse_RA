-- ==============================================================================
-- SCRIPT DDL - MODULO DE PAGOS para Data Warehouse dw_reg_v1
-- Ejecutar en DBeaver conectado a: localhost:5432/dw_reg_v1
-- ==============================================================================
-- 1. LIMPIEZA (por si existieran versiones previas)
DROP TABLE IF EXISTS dw.fact_pago CASCADE;
DROP TABLE IF EXISTS dw.dim_pago CASCADE;
DROP TABLE IF EXISTS stg.online_payments_bi CASCADE;
DROP TABLE IF EXISTS stg.financial_transaction_bi CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_dim_pago() CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_fact_pago() CASCADE;
-- ==============================================================================
-- 2. TABLAS STAGING DE PAGOS
-- ==============================================================================
-- 2.1 Origen: jbpmdb @ 172.16.0.226 / online_payment
CREATE TABLE stg.online_payments_bi (
    online_payment_id INTEGER,
    project_id VARCHAR(255),
    tramit_number VARCHAR(255),
    convenience_number VARCHAR(255),
    bank_code VARCHAR(50),
    payment_value NUMERIC(20, 2),
    date_hour_transaction TIMESTAMP,
    transaction_type VARCHAR(100),
    transaction_state BOOLEAN,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'JBPM'
);
-- 2.2 Origen: suia_enlisy @ 172.16.0.179 / suia_iii
CREATE TABLE stg.financial_transaction_bi (
    fitr_id INTEGER,
    codigo_proyecto VARCHAR(255),
    fitr_transaction_amount NUMERIC(20, 2),
    fitr_paid_value NUMERIC(20, 2),
    fitr_transaction_number VARCHAR(255),
    fitr_payment_type INTEGER,
    payment_type_desc VARCHAR(100),
    fitr_creation_date TIMESTAMP,
    fitr_status BOOLEAN,
    task_name VARCHAR(255),
    processname VARCHAR(255),
    processinstanceid BIGINT,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'SUIA_RCOA'
);
-- ==============================================================================
-- 3. DIMENSION DE PAGO (unificada ambos origenes)
-- ==============================================================================
CREATE TABLE dw.dim_pago (
    sk_pago SERIAL PRIMARY KEY,
    tipo_pago VARCHAR(100),
    bank_code VARCHAR(50),
    transaction_type VARCHAR(100),
    sistema_origen VARCHAR(50),
    CONSTRAINT uk_dim_pago UNIQUE (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
);
-- ==============================================================================
-- 4. FACT TABLE DE PAGOS
-- ==============================================================================
CREATE TABLE dw.fact_pago (
    id_fact_pago SERIAL PRIMARY KEY,
    sk_proyecto INT REFERENCES dw.dim_proyecto(sk_proyecto),
    sk_pago INT REFERENCES dw.dim_pago(sk_pago),
    sk_fecha_pago INT REFERENCES dw.dim_tiempo(sk_tiempo),
    -- Metricas
    monto_transaccion NUMERIC(20, 2),
    monto_pagado NUMERIC(20, 2),
    numero_transaccion VARCHAR(255),
    numero_tramite VARCHAR(255),
    -- Proceso BPM (SUIA)
    tarea_bpm VARCHAR(255),
    proceso_bpm VARCHAR(255),
    -- Metadata ETL
    origen VARCHAR(50),
    id_transaccion_origen VARCHAR(255),
    secuencia_pago INT,
    es_deposito_inicial BOOLEAN DEFAULT false,
    monto_acumulado NUMERIC(20, 2),
    fecha_carga TIMESTAMP DEFAULT NOW(),
    -- Constraint para evitar duplicados: permite un mismo pago en múltiples proyectos
    CONSTRAINT uk_fact_pago_dedup UNIQUE (sk_proyecto, id_transaccion_origen, origen)
);
-- Indices para rendimiento
CREATE INDEX idx_fact_pago_proyecto ON dw.fact_pago(sk_proyecto);
CREATE INDEX idx_fact_pago_fecha ON dw.fact_pago(sk_fecha_pago);
CREATE INDEX idx_fact_pago_origen ON dw.fact_pago(origen);
CREATE INDEX idx_fact_pago_secuencia ON dw.fact_pago(numero_tramite, secuencia_pago);
-- ==============================================================================
-- 5. SP: Cargar Dimension de Pagos
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_pago() RETURNS void AS $$ BEGIN -- Insertar tipos de pago desde JBPM (online_payments)
INSERT INTO dw.dim_pago (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
SELECT DISTINCT 'Online Payment',
    COALESCE(bank_code, 'N/A'),
    COALESCE(transaction_type, 'N/A'),
    'JBPM'
FROM stg.online_payments_bi
WHERE transaction_state = true ON CONFLICT (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    ) DO NOTHING;
-- Insertar tipos de pago desde SUIA (financial_transaction)
INSERT INTO dw.dim_pago (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
SELECT DISTINCT COALESCE(payment_type_desc, 'N/A'),
    'N/A',
    COALESCE(processname, 'N/A'),
    'SUIA_RCOA'
FROM stg.financial_transaction_bi
WHERE fitr_status = true ON CONFLICT (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    ) DO NOTHING;
RAISE NOTICE 'Dimension de pagos cargada: % registros',
(
    SELECT COUNT(1)
    FROM dw.dim_pago
);
END;
$$ LANGUAGE plpgsql;
-- ==============================================================================
-- 6. SP: Cargar Fact Table de Pagos (con deduplicacion)
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_fact_pago() RETURNS void AS $$
DECLARE row_count_a INT;
row_count_b INT;
row_count_c INT;
BEGIN -- 0. Tabla temporal de pagos unicos (Mejora performance significativamente)
CREATE TEMPORARY TABLE tmp_jbpm_unicos AS
SELECT DISTINCT ON (online_payment_id, project_id) online_payment_id,
    project_id,
    tramit_number,
    convenience_number,
    COALESCE(bank_code, 'N/A') as bank_code,
    payment_value,
    date_hour_transaction,
    COALESCE(transaction_type, 'N/A') as transaction_type
FROM stg.online_payments_bi
WHERE transaction_state = true
ORDER BY online_payment_id,
    project_id;
ANALYZE tmp_jbpm_unicos;
-- ══════════════════════════════════════════════════════════════════
-- PARTE A: Cargar pagos JBPM - Asociación DIRECTA por project_id
-- ══════════════════════════════════════════════════════════════════
INSERT INTO dw.fact_pago (
        sk_proyecto,
        sk_pago,
        sk_fecha_pago,
        monto_transaccion,
        monto_pagado,
        numero_transaccion,
        numero_tramite,
        origen,
        id_transaccion_origen
    )
SELECT dp.sk_proyecto,
    dpago.sk_pago,
    dt.sk_tiempo,
    op.payment_value,
    op.payment_value,
    op.convenience_number,
    op.tramit_number,
    'JBPM',
    'JBPM_' || op.online_payment_id::text
FROM tmp_jbpm_unicos op
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = op.bank_code
    AND dpago.transaction_type = op.transaction_type
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
GET DIAGNOSTICS row_count_a = ROW_COUNT;
RAISE NOTICE 'Parte A (Directos) completada: % filas',
row_count_a;
-- PARTE B (Removida por inconsistencia de datos: evitaba sobre-asociación por proponente)
-- ══════════════════════════════════════════════════════════════════
-- PARTE C: Cargar pagos SUIA (financial_transaction)
-- ══════════════════════════════════════════════════════════════════
INSERT INTO dw.fact_pago (
        sk_proyecto,
        sk_pago,
        sk_fecha_pago,
        monto_transaccion,
        monto_pagado,
        numero_transaccion,
        numero_tramite,
        tarea_bpm,
        proceso_bpm,
        origen,
        id_transaccion_origen
    )
SELECT DISTINCT ON (dp.sk_proyecto, ft.fitr_id) dp.sk_proyecto,
    dpago.sk_pago,
    dt.sk_tiempo,
    ft.fitr_transaction_amount,
    ft.fitr_paid_value,
    ft.fitr_transaction_number,
    NULL,
    ft.task_name,
    ft.processname,
    'SUIA_RCOA',
    'SUIA_' || ft.fitr_id::text
FROM stg.financial_transaction_bi ft
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = ft.codigo_proyecto
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = COALESCE(ft.payment_type_desc, 'N/A')
    AND dpago.bank_code = 'N/A'
    AND dpago.transaction_type = COALESCE(ft.processname, 'N/A')
    AND dpago.sistema_origen = 'SUIA_RCOA'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = ft.fitr_creation_date::date
WHERE ft.fitr_status = true ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
GET DIAGNOSTICS row_count_c = ROW_COUNT;
RAISE NOTICE 'Parte C (SUIA) completada: % filas',
row_count_c;
DROP TABLE tmp_jbpm_unicos;
END;
$$ LANGUAGE plpgsql;
-- ==============================================================================
-- 7. VERIFICACION
-- ==============================================================================
SELECT table_schema,
    table_name
FROM information_schema.tables
WHERE table_name IN (
        'online_payments_bi',
        'financial_transaction_bi',
        'dim_pago',
        'fact_pago'
    )
ORDER BY table_schema,
    table_name;