-- Optimización por Lotes (Batching) para Escenarios de Volumen Extremo (11.8M+)
-- El uso de lotes evita la saturación del log de transacciones (WAL) y bloqueos prolongados.
CREATE OR REPLACE FUNCTION dw.sp_calcular_secuencia_pagos() RETURNS void AS $$
DECLARE batch_size INTEGER := 50000;
-- Procesar 50k trámites a la vez
offset_val INTEGER := 0;
records_updated INTEGER;
BEGIN RAISE NOTICE 'Iniciando cálculo por LOTES para % millones de registros...',
11.8;
-- 1. Identificar todos los trámites que necesitan cálculo
CREATE TEMP TABLE tmp_tramites_all ON COMMIT DROP AS
SELECT DISTINCT numero_tramite
FROM dw.fact_pago
WHERE numero_tramite IS NOT NULL;
RAISE NOTICE 'Total de trámites únicos detectados: %',
(
    SELECT COUNT(*)
    FROM tmp_tramites_all
);
-- 2. Procesar en bucle para no colapsar la base de datos
LOOP
UPDATE dw.fact_pago fp
SET secuencia_pago = sub.rn,
    es_deposito_inicial = (sub.rn = 1),
    monto_acumulado = sub.acum
FROM (
        SELECT id_fact_pago,
            ROW_NUMBER() OVER (
                PARTITION BY f.numero_tramite
                ORDER BY f.sk_fecha_pago,
                    f.id_fact_pago
            ) AS rn,
            SUM(f.monto_transaccion) OVER (
                PARTITION BY f.numero_tramite
                ORDER BY f.sk_fecha_pago,
                    f.id_fact_pago
            ) AS acum
        FROM dw.fact_pago f
        WHERE f.numero_tramite IN (
                SELECT numero_tramite
                FROM tmp_tramites_all
                WHERE numero_tramite IS NOT NULL
                LIMIT batch_size OFFSET offset_val
            )
    ) sub
WHERE fp.id_fact_pago = sub.id_fact_pago;
GET DIAGNOSTICS records_updated = ROW_COUNT;
EXIT
WHEN records_updated = 0;
offset_val := offset_val + batch_size;
RAISE NOTICE 'Lote procesado. Offset: %, Registros actualizados: %',
offset_val,
records_updated;
-- Opcional: COMMIT intermedio no es posible en un SP tradicional de Postgres 11-, 
-- pero en Postgres 11+ se puede usar PROCEDURE en lugar de FUNCTION si se requiere.
END LOOP;
-- 3. Marcar pagos individuales SUIA
UPDATE dw.fact_pago
SET secuencia_pago = 1,
    es_deposito_inicial = true,
    monto_acumulado = monto_transaccion
WHERE numero_tramite IS NULL
    AND secuencia_pago IS NULL;
RAISE NOTICE 'Proceso completado.';
END;
$$ LANGUAGE plpgsql;