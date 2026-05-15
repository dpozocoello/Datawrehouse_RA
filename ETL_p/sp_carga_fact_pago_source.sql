CREATE OR REPLACE FUNCTION dw.sp_carga_fact_pago()
 RETURNS void
 LANGUAGE plpgsql
AS $function$ BEGIN -- PARTE A: Pagos JBPM directos por project_id
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
SELECT DISTINCT ON (dp.sk_proyecto, op.online_payment_id) dp.sk_proyecto,
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
FROM stg.online_payments_bi op
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = COALESCE(op.bank_code, 'N/A')
    AND dpago.transaction_type = COALESCE(op.transaction_type, 'N/A')
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
WHERE op.transaction_state = true ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
RAISE NOTICE 'PARTE A cargada (JBPM directos): %',
(
    SELECT COUNT(1)
    FROM dw.fact_pago
    WHERE origen = 'JBPM'
);
-- PARTE B: Pagos JBPM indirectos por tramit_number → mismo proponente
-- Para cada pago JBPM ya cargado, asociarlo a todos los proyectos
-- del mismo proponente que compartan "grupo de pagos por trámite"
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
SELECT DISTINCT ON (
        fr_other.sk_proyecto,
        fp_src.id_transaccion_origen
    ) fr_other.sk_proyecto,
    fp_src.sk_pago,
    fp_src.sk_fecha_pago,
    fp_src.monto_transaccion,
    fp_src.monto_pagado,
    fp_src.numero_transaccion,
    fp_src.numero_tramite,
    fp_src.tarea_bpm,
    fp_src.proceso_bpm,
    fp_src.origen,
    fp_src.id_transaccion_origen
FROM dw.fact_pago fp_src -- Obtener el proponente del proyecto con pago directo
    JOIN dw.fact_regularizacion fr_src ON fr_src.sk_proyecto = fp_src.sk_proyecto -- Buscar otros proyectos del mismo proponente
    JOIN dw.fact_regularizacion fr_other ON fr_other.sk_proponente = fr_src.sk_proponente
    AND fr_other.sk_proyecto != fp_src.sk_proyecto
WHERE fp_src.origen = 'JBPM' ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO NOTHING;
RAISE NOTICE 'PARTE B cargada (JBPM indirectos): %',
(
    SELECT COUNT(1)
    FROM dw.fact_pago
    WHERE origen = 'JBPM'
);
-- PARTE C: Pagos SUIA (financial_transaction)
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
RAISE NOTICE 'Fact pagos total: % filas',
(
    SELECT COUNT(1)
    FROM dw.fact_pago
);
END;
$function$
