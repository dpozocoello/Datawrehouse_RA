-- ==============================================================================
-- SCRIPT DE RESOLUCIÓN DE DEADLOCK PARA dw.sp_carga_fact_pago()
-- ==============================================================================
-- Se añade ORDER BY en los INSERT para garantizar un orden de bloqueo secuencial
-- y prevenir esperas circulares entre transacciones concurrentes.
CREATE OR REPLACE FUNCTION dw.sp_carga_fact_pago() RETURNS void AS $$
DECLARE row_count_a INT;
row_count_b INT;
row_count_c INT;
t_start TIMESTAMP;
t_end TIMESTAMP;
BEGIN t_start := clock_timestamp();
RAISE NOTICE '[%] INICIO: dw.sp_carga_fact_pago()',
t_start;
-- 0. Tabla temporal de pagos unicos
DROP TABLE IF EXISTS tmp_jbpm_unicos;
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
-- PARTE A: Asociación DIRECTA
-- ══════════════════════════════════════════════════════════════════
RAISE NOTICE '[%] PARTE A: Iniciando asociación directa por project_id...',
clock_timestamp();
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
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
ORDER BY dp.sk_proyecto,
    op.online_payment_id ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
GET DIAGNOSTICS row_count_a = ROW_COUNT;
RAISE NOTICE '[%] PARTE A Completada: % filas insertadas/actualizadas',
clock_timestamp(),
row_count_a;
-- ══════════════════════════════════════════════════════════════════
-- PARTE B: Asociación INDIRECTA (Proponente)
-- ══════════════════════════════════════════════════════════════════
RAISE NOTICE '[%] PARTE B: Iniciando asociación indirecta por Proponente...',
clock_timestamp();
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
    ) WITH payment_owners AS (
        SELECT DISTINCT ON (op.online_payment_id) fr.sk_proponente,
            op.online_payment_id,
            dp.sk_proyecto as orig_sk_proyecto,
            dpago.sk_pago,
            dt.sk_tiempo,
            op.payment_value,
            op.convenience_number,
            op.tramit_number,
            op.date_hour_transaction,
            op.bank_code,
            op.transaction_type
        FROM tmp_jbpm_unicos op
            INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
            INNER JOIN dw.fact_regularizacion fr ON fr.sk_proyecto = dp.sk_proyecto
            INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
            AND dpago.bank_code = op.bank_code
            AND dpago.transaction_type = op.transaction_type
            AND dpago.sistema_origen = 'JBPM'
            LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
    )
SELECT fr_all.sk_proyecto,
    po.sk_pago,
    po.sk_tiempo,
    po.payment_value,
    po.payment_value,
    po.convenience_number,
    po.tramit_number,
    'JBPM',
    'JBPM_' || po.online_payment_id::text
FROM payment_owners po
    INNER JOIN dw.fact_regularizacion fr_all ON fr_all.sk_proponente = po.sk_proponente
WHERE fr_all.sk_proyecto != po.orig_sk_proyecto
ORDER BY fr_all.sk_proyecto,
    po.online_payment_id ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO NOTHING;
GET DIAGNOSTICS row_count_b = ROW_COUNT;
RAISE NOTICE '[%] PARTE B Completada: % filas nuevas asociadas',
clock_timestamp(),
row_count_b;
-- ══════════════════════════════════════════════════════════════════
-- PARTE C: Cargar pagos SUIA
-- ══════════════════════════════════════════════════════════════════
RAISE NOTICE '[%] PARTE C: Iniciando carga de pagos SUIA...',
clock_timestamp();
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
WHERE ft.fitr_status = true
ORDER BY dp.sk_proyecto,
    ft.fitr_id ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
GET DIAGNOSTICS row_count_c = ROW_COUNT;
RAISE NOTICE '[%] PARTE C Completada: % filas insertadas/actualizadas',
clock_timestamp(),
row_count_c;
t_end := clock_timestamp();
RAISE NOTICE '[%] FIN: dw.sp_carga_fact_pago() - Tiempo total: %',
t_end,
(t_end - t_start);
END;
$$ LANGUAGE plpgsql;