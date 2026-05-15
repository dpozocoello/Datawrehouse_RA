-- Fix SP: Usar DISTINCT ON para evitar duplicados de online_payments_historical
CREATE OR REPLACE FUNCTION dw.sp_carga_fact_pago() RETURNS void AS $$ BEGIN -- Cargar pagos JBPM (online_payments) con DISTINCT ON para deduplicar
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
SELECT dp.sk_proyecto,
    dpago.sk_pago,
    dt.sk_tiempo,
    op.payment_value,
    op.payment_value,
    op.convenience_number,
    op.tramit_number,
    NULL,
    NULL,
    'JBPM',
    'JBPM_' || op.online_payment_id::text
FROM (
        SELECT DISTINCT ON (online_payment_id) *
        FROM stg.online_payments_bi
        WHERE transaction_state = true
        ORDER BY online_payment_id,
            date_hour_transaction DESC
    ) op
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = COALESCE(op.bank_code, 'N/A')
    AND dpago.transaction_type = COALESCE(op.transaction_type, 'N/A')
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date ON CONFLICT (id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
-- Cargar pagos SUIA (financial_transaction) con DISTINCT ON para deduplicar
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
SELECT dp.sk_proyecto,
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
FROM (
        SELECT DISTINCT ON (fitr_id) *
        FROM stg.financial_transaction_bi
        WHERE fitr_status = true
        ORDER BY fitr_id
    ) ft
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = ft.codigo_proyecto
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = COALESCE(ft.payment_type_desc, 'N/A')
    AND dpago.bank_code = 'N/A'
    AND dpago.transaction_type = COALESCE(ft.processname, 'N/A')
    AND dpago.sistema_origen = 'SUIA_RCOA'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = ft.fitr_creation_date::date ON CONFLICT (id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
RAISE NOTICE 'Fact pagos cargada: % filas',
(
    SELECT COUNT(1)
    FROM dw.fact_pago
);
END;
$$ LANGUAGE plpgsql;
-- Ejecutar los SPs
SELECT dw.sp_carga_dim_pago();
SELECT dw.sp_carga_fact_pago();
-- Verificar resultados
SELECT 'stg.online_payments_bi' AS tabla,
    COUNT(*) AS registros
FROM stg.online_payments_bi
UNION ALL
SELECT 'stg.financial_transaction_bi',
    COUNT(*)
FROM stg.financial_transaction_bi
UNION ALL
SELECT 'dw.dim_pago',
    COUNT(*)
FROM dw.dim_pago
UNION ALL
SELECT 'dw.fact_pago',
    COUNT(*)
FROM dw.fact_pago;
-- Verificar sin duplicados
SELECT id_transaccion_origen,
    origen,
    COUNT(*)
FROM dw.fact_pago
GROUP BY 1,
    2
HAVING COUNT(*) > 1;