"""Fix sp_carga_fact_pago: remove PARTE B (cartesian product)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connections import get_connection
from config import CONN_DWH_LOCAL

new_sp = """CREATE OR REPLACE FUNCTION dw.sp_carga_fact_pago()
 RETURNS void
 LANGUAGE plpgsql
AS $func$
BEGIN

-- PARTE A: Pagos JBPM directos por project_id
INSERT INTO dw.fact_pago (
        sk_proyecto, sk_pago, sk_fecha_pago, monto_transaccion, monto_pagado,
        numero_transaccion, numero_tramite, tarea_bpm, proceso_bpm, origen, id_transaccion_origen)
SELECT DISTINCT ON (dp.sk_proyecto, op.online_payment_id)
    dp.sk_proyecto, dpago.sk_pago, dt.sk_tiempo,
    op.payment_value, op.payment_value, op.convenience_number, op.tramit_number,
    NULL, NULL, 'JBPM', 'JBPM_' || op.online_payment_id::text
FROM stg.online_payments_bi op
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
        AND dpago.bank_code = COALESCE(op.bank_code, 'N/A')
        AND dpago.transaction_type = COALESCE(op.transaction_type, 'N/A')
        AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
WHERE op.transaction_state = true
ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();

RAISE NOTICE 'PARTE A cargada (JBPM directos): %', (SELECT COUNT(1) FROM dw.fact_pago WHERE origen = 'JBPM');

-- PARTE B: DESHABILITADA (2026-04-08)
-- Propagacion cruzada por proponente genera producto cartesiano inviable:
-- max 16.063 proyectos/proponente x 183.876 pagos = ~2.200 millones de filas.
-- Los pagos se registran solo contra el proyecto que origina el pago (PARTE A).
RAISE NOTICE 'PARTE B (indirectos por proponente): DESHABILITADA - producto cartesiano inviable (2.2B filas estimadas)';

-- PARTE C: Pagos SUIA (financial_transaction)
INSERT INTO dw.fact_pago (
        sk_proyecto, sk_pago, sk_fecha_pago, monto_transaccion, monto_pagado,
        numero_transaccion, numero_tramite, tarea_bpm, proceso_bpm, origen, id_transaccion_origen)
SELECT DISTINCT ON (dp.sk_proyecto, ft.fitr_id)
    dp.sk_proyecto, dpago.sk_pago, dt.sk_tiempo,
    ft.fitr_transaction_amount, ft.fitr_paid_value, ft.fitr_transaction_number,
    NULL, ft.task_name, ft.processname, 'SUIA_RCOA', 'SUIA_' || ft.fitr_id::text
FROM stg.financial_transaction_bi ft
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = ft.codigo_proyecto
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = COALESCE(ft.payment_type_desc, 'N/A')
        AND dpago.bank_code = 'N/A'
        AND dpago.transaction_type = COALESCE(ft.processname, 'N/A')
        AND dpago.sistema_origen = 'SUIA_RCOA'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = ft.fitr_creation_date::date
WHERE ft.fitr_status = true
ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();

RAISE NOTICE 'Fact pagos total: % filas', (SELECT COUNT(1) FROM dw.fact_pago);

END;
$func$;
"""

with get_connection(CONN_DWH_LOCAL) as conn:
    with conn.cursor() as cur:
        cur.execute(new_sp)
    conn.commit()
    print("SP sp_carga_fact_pago updated successfully (PARTE B removed).")

# Verify
with get_connection(CONN_DWH_LOCAL) as conn:
    with conn.cursor() as cur:
        cur.execute("""SELECT pg_get_functiondef(oid) FROM pg_proc
                       WHERE proname='sp_carga_fact_pago' AND pronamespace='dw'::regnamespace""")
        src = cur.fetchone()[0]
        if 'DESHABILITADA' in src:
            print("Fix confirmed in SP.")
        else:
            print("WARNING: fix not confirmed.")
