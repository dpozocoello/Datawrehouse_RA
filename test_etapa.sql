-- VERSION DE PRUEBA SOLO ETAPA (6385)
CREATE OR REPLACE FUNCTION dw.sp_test_etapa() RETURNS void AS $$
DECLARE row_count_a INT;
row_count_b INT;
BEGIN RAISE NOTICE 'Iniciando PRUEBA ETAPA...';
CREATE TEMP TABLE tmp_jbpm_unicos ON COMMIT DROP AS
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
-- PARTE A: Solo para proyectos de ETAPA en staging
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
    INNER JOIN dw.fact_regularizacion fr ON fr.sk_proyecto = dp.sk_proyecto
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = op.bank_code
    AND dpago.transaction_type = op.transaction_type
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
WHERE fr.sk_proponente = 6385 ON CONFLICT DO NOTHING;
GET DIAGNOSTICS row_count_a = ROW_COUNT;
RAISE NOTICE 'Prueba A (ETAPA Directo): % filas',
row_count_a;
-- PARTE B: Replicación solo ETAPA
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
            op.project_id as orig_project_id,
            dpago.sk_pago,
            dt.sk_tiempo,
            op.payment_value,
            op.convenience_number,
            op.tramit_number
        FROM tmp_jbpm_unicos op
            INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
            INNER JOIN dw.fact_regularizacion fr ON fr.sk_proyecto = dp.sk_proyecto
            INNER JOIN dw.dim_pago dpago ON dpago.sk_pago = (
                SELECT sk_pago
                FROM dw.dim_pago
                WHERE tipo_pago = 'Online Payment'
                    AND bank_code = op.bank_code
                    AND transaction_type = op.transaction_type
                    AND sistema_origen = 'JBPM'
                LIMIT 1
            )
            LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
        WHERE fr.sk_proponente = 6385
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
    INNER JOIN dw.dim_proyecto dp_all ON dp_all.sk_proyecto = fr_all.sk_proyecto
WHERE dp_all.codigo_proyecto != po.orig_project_id ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO NOTHING;
GET DIAGNOSTICS row_count_b = ROW_COUNT;
RAISE NOTICE 'Prueba B (ETAPA Indirecto): % filas',
row_count_b;
END;
$$ LANGUAGE plpgsql;
TRUNCATE TABLE dw.fact_pago;
SELECT dw.sp_test_etapa();