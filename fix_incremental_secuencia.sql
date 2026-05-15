-- Optimización Incremental: Secuencia de Pagos
-- Esta versión solo procesa proyectos que tienen pagos nuevos (secuencia_pago IS NULL)
-- para evitar el escaneo y actualización de los 11.8 millones de registros existentes.
CREATE OR REPLACE FUNCTION dw.sp_calcular_secuencia_pagos() RETURNS void AS $$
DECLARE rows_affected INTEGER;
BEGIN RAISE NOTICE 'Iniciando cálculo INCREMENTAL de secuencia...';
-- 1. Identificar numero_tramite que necesitan actualización
-- Solo recalculamos para trámites que tienen al menos un pago nuevo
CREATE TEMP TABLE tmp_tramites_interes ON COMMIT DROP AS
SELECT DISTINCT numero_tramite
FROM dw.fact_pago
WHERE secuencia_pago IS NULL
    AND numero_tramite IS NOT NULL;
GET DIAGNOSTICS rows_affected = ROW_COUNT;
RAISE NOTICE 'Se encontraron % trámites con nuevos pagos para recalcular.',
rows_affected;
IF rows_affected > 0 THEN -- 2. Actualizar solo esos trámites (usando el índice por numero_tramite)
UPDATE dw.fact_pago fp
SET secuencia_pago = sub.rn,
    es_deposito_inicial = (sub.rn = 1),
    monto_acumulado = sub.acum
FROM (
        SELECT id_fact_pago,
            ROW_NUMBER() OVER (
                PARTITION BY f.numero_tramite
                ORDER BY f.sk_fecha_pago NULLS LAST,
                    f.id_fact_pago
            ) AS rn,
            SUM(f.monto_transaccion) OVER (
                PARTITION BY f.numero_tramite
                ORDER BY f.sk_fecha_pago NULLS LAST,
                    f.id_fact_pago
            ) AS acum
        FROM dw.fact_pago f
        WHERE f.numero_tramite IN (
                SELECT numero_tramite
                FROM tmp_tramites_interes
            )
    ) sub
WHERE fp.id_fact_pago = sub.id_fact_pago;
GET DIAGNOSTICS rows_affected = ROW_COUNT;
RAISE NOTICE 'Secuencias actualizadas para % registros.',
rows_affected;
END IF;
-- 3. Caso SUIA (sin número de trámite)
UPDATE dw.fact_pago
SET secuencia_pago = 1,
    es_deposito_inicial = true,
    monto_acumulado = monto_transaccion
WHERE numero_tramite IS NULL
    AND secuencia_pago IS NULL;
GET DIAGNOSTICS rows_affected = ROW_COUNT;
RAISE NOTICE 'Pagos SUIA (individuales) procesados: %',
rows_affected;
RAISE NOTICE 'Proceso incremental completado.';
END;
$$ LANGUAGE plpgsql;