-- FINAL SURGICAL INTEGRITY FIX (32 PROJECTS & GEOGRAPHY)
TRUNCATE TABLE dw.fact_pago;
-- 1. Pagos Unicos Staging
CREATE TEMPORARY TABLE tmp_unicos_jbpm AS
SELECT DISTINCT ON (online_payment_id, project_id) online_payment_id,
    project_id,
    tramit_number,
    convenience_number,
    COALESCE(bank_code, 'N/A') as bank_code,
    payment_value,
    date_hour_transaction::date as fecha_trans,
    COALESCE(transaction_type, 'N/A') as transaction_type
FROM stg.online_payments_bi
WHERE transaction_state = true
ORDER BY online_payment_id,
    project_id;
-- 2. PARTE A: CARGA DIRECTA (53k rows)
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
FROM tmp_unicos_jbpm op
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = op.bank_code
    AND dpago.transaction_type = op.transaction_type
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.fecha_trans ON CONFLICT DO NOTHING;
-- 3. PARTE B: REPLICACION PARA LOS PROYECTOS CRITICOS (POR RUC)
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
    ) WITH target_rucs AS (
        SELECT UNNEST(
                ARRAY [
        '0160050020001','1768153530001','0460001020001','0560000110001','0590042110001',
        '0703926170','0968599020001','1002243770','1360000120001','1360000630001',
        '1707955074','1712747805001','1714395405','1768082680001'
    ]
            ) as ruc
    ),
    payment_owners AS (
        SELECT DISTINCT ON (op.online_payment_id) fr.sk_proponente,
            tr.ruc,
            op.online_payment_id,
            dp.sk_proyecto as orig_sk_proyecto,
            dpago.sk_pago,
            dt.sk_tiempo,
            op.payment_value,
            op.convenience_number,
            op.tramit_number
        FROM tmp_unicos_jbpm op
            INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
            INNER JOIN dw.fact_regularizacion fr ON fr.sk_proyecto = dp.sk_proyecto
            INNER JOIN dw.dim_proponente dpp ON dpp.sk_proponente = fr.sk_proponente
            INNER JOIN target_rucs tr ON tr.ruc = dpp.ced_ruc_proponente
            INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
            AND dpago.bank_code = op.bank_code
            AND dpago.transaction_type = op.transaction_type
            AND dpago.sistema_origen = 'JBPM'
            LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.fecha_trans
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
WHERE fr_all.sk_proyecto != po.orig_sk_proyecto ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO NOTHING;
-- 4. PARTE C: SUIA
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
    ft.fitr_id ON CONFLICT DO NOTHING;
-- 5. CORRECCION GEOGRAFICA CUENCA
INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
SELECT 'AZUAY',
    'CUENCA',
    'CUENCA'
WHERE NOT EXISTS (
        SELECT 1
        FROM dw.dim_geografia
        WHERE canton = 'CUENCA'
            AND parroquia = 'CUENCA'
    );
UPDATE dw.fact_regularizacion fr
SET sk_geografia = (
        SELECT sk_geografia
        FROM dw.dim_geografia
        WHERE canton = 'CUENCA'
            AND parroquia = 'CUENCA'
        LIMIT 1
    )
WHERE sk_proyecto IN (
        SELECT sk_proyecto
        FROM dw.dim_proyecto
        WHERE codigo_proyecto = 'MAE-RA-2017-304882'
    );
SELECT 'SUCCESS' as status;