-- CARGA QUIRURGICA CON BUCLE DE PROGRESO
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
-- 2. Mapeo de Pagos a Proponentes
CREATE TEMPORARY TABLE tmp_payment_proponents AS
SELECT DISTINCT ON (op.online_payment_id) fr.sk_proponente,
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
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = op.bank_code
    AND dpago.transaction_type = op.transaction_type
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.fecha_trans
ORDER BY op.online_payment_id;
ANALYZE tmp_unicos_jbpm;
ANALYZE tmp_payment_proponents;
-- PARTE A: CARGA DIRECTA
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
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.fecha_trans ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO NOTHING;
-- PARTE B: REPLICACION MEDIANTE BUCLE (PARA EVITAR CARTESIANO MASSIVO)
DO $$
DECLARE r RECORD;
cnt INT := 0;
tot INT;
BEGIN
SELECT count(*) INTO tot
FROM tmp_payment_proponents;
RAISE NOTICE 'Iniciando Replicación Part B para % pagos...',
tot;
FOR r IN
SELECT *
FROM tmp_payment_proponents LOOP
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
SELECT fr_all.sk_proyecto,
    r.sk_pago,
    r.sk_tiempo,
    r.payment_value,
    r.payment_value,
    r.convenience_number,
    r.tramit_number,
    'JBPM',
    'JBPM_' || r.online_payment_id::text
FROM dw.fact_regularizacion fr_all
WHERE fr_all.sk_proponente = r.sk_proponente
    AND fr_all.sk_proyecto != r.orig_sk_proyecto ON CONFLICT DO NOTHING;
cnt := cnt + 1;
IF cnt % 5000 = 0 THEN RAISE NOTICE 'Progreso Part B: % / % pagos procesados',
cnt,
tot;
END IF;
END LOOP;
END $$;
-- PARTE C: SUIA
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
    ft.fitr_id ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO NOTHING;
-- CONTEOS
SELECT origen,
    COUNT(*)
FROM dw.fact_pago
GROUP BY 1;