import psycopg2
import sys
import os

sys.path.insert(0, r'/opt/eco-sieaa/etl')
from config import CONN_DWH_LOCAL

def recalcular():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        
        query = """
        WITH desc_saldos AS (
            SELECT TRIM(oph.project_id) AS project_id,
                TRIM(oph.tramit_number) AS tramit_number,
                COALESCE(
                    LAG(oph.value_updated::numeric) OVER (
                        PARTITION BY TRIM(oph.tramit_number)
                        ORDER BY oph.id_online_payment_historical ASC
                    ),
                    (
                        oph.value_updated::numeric + COALESCE(oph.retired_value, 0)::numeric
                    )
                ) AS saldo_anterior,
                oph.value_updated::numeric AS saldo_actual
            FROM stg.online_payments_historical_bi oph
            WHERE oph.description = 'Uso de transacción'
                AND TRIM(oph.project_id) IS NOT NULL
                AND TRIM(oph.project_id) != ''
        ),
        calculado AS (
            SELECT project_id,
                tramit_number,
                (saldo_anterior - saldo_actual) AS valor_calculado
            FROM desc_saldos
        )
        UPDATE dw.fact_pago fp
        SET monto_transaccion = c.valor_calculado,
            monto_pagado = c.valor_calculado
        FROM calculado c
            INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = c.project_id
        WHERE fp.sk_proyecto = dp.sk_proyecto
            AND fp.numero_tramite = c.tramit_number
            AND fp.origen = 'JBPM';
        """
        cur.execute(query)
        conn.commit()
        print(f"Recalculo exitoso: {cur.statusmessage}")
        
        # Verificar conteo final
        cur.execute("SELECT count(*) FROM dw.fact_pago WHERE monto_transaccion > 0 AND origen = 'JBPM'")
        print(f"Pagos JBPM con monto validado: {cur.fetchone()[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    recalcular()
