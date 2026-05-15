-- Optimización de Rendimiento: Secuencia de Pagos
-- 1. Crear índice compuesto para acelerar PARTITION BY y ORDER BY en funciones de ventana
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fact_pago_secuencia ON dw.fact_pago (numero_tramite, sk_fecha_pago, id_fact_pago);
-- 2. Actualizar SP con logging granular para monitoreo
CREATE OR REPLACE FUNCTION dw.sp_calcular_secuencia_pagos() RETURNS void AS $$
DECLARE rows_affected INTEGER;
BEGIN RAISE NOTICE 'Iniciando cálculo de secuencia por numero_tramite...';
-- Calcular secuencia por tramit_number, ordenada por fecha y ID
UPDATE dw.fact_pago fp
SET secuencia_pago = sub.rn,
    es_deposito_inicial = (sub.rn = 1),
    monto_acumulado = sub.acum
FROM (
        SELECT id_fact_pago,
            ROW_NUMBER() OVER (
                PARTITION BY numero_tramite
                ORDER BY sk_fecha_pago NULLS LAST,
                    id_fact_pago
            ) AS rn,
            SUM(monto_transaccion) OVER (
                PARTITION BY numero_tramite
                ORDER BY sk_fecha_pago NULLS LAST,
                    id_fact_pago
            ) AS acum
        FROM dw.fact_pago
        WHERE numero_tramite IS NOT NULL
    ) sub
WHERE fp.id_fact_pago = sub.id_fact_pago;
GET DIAGNOSTICS rows_affected = ROW_COUNT;
RAISE NOTICE 'Secuencias calculadas para % registros con numero_tramite.',
rows_affected;
RAISE NOTICE 'Procesando pagos sin numero_tramite (SUIA)...';
-- Para pagos sin tramit_number (SUIA), marcar como depósito individual
UPDATE dw.fact_pago
SET secuencia_pago = 1,
    es_deposito_inicial = true,
    monto_acumulado = monto_transaccion
WHERE numero_tramite IS NULL
    AND secuencia_pago IS NULL;
GET DIAGNOSTICS rows_affected = ROW_COUNT;
RAISE NOTICE 'Secuencias calculadas para % registros sin numero_tramite.',
rows_affected;
RAISE NOTICE 'Proceso completado exitosamente.';
END;
$$ LANGUAGE plpgsql;