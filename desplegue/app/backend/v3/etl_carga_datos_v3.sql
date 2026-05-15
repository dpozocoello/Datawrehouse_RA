-- ==============================================================================
-- ETL v3 — Carga Histórica de Pagos JBPM y Recálculo del Monto
-- Ejecutar DESPUÉS de ddl_dwh_v3.sql
-- ==============================================================================
-- 1. Extraer online_payments_historical desde jbpmdb
TRUNCATE TABLE stg.online_payments_historical_bi;
INSERT INTO stg.online_payments_historical_bi (
        id_online_payment_historical,
        description,
        project_id,
        retired_value,
        sender_ip,
        tramit_number,
        update_date,
        value_updated,
        online_payment_id,
        enabled,
        user_create,
        user_modification,
        date_create,
        date_modification,
        reactivate,
        observations,
        retired_value_1
    )
SELECT *
FROM dblink(
        'host=172.16.0.226 dbname=jbpmdb user=postgres password=postgres port=5432',
        'SELECT id_online_payment_historical, description, project_id, retired_value, sender_ip,
            tramit_number, update_date, value_updated, online_payment_id, enabled,
            user_create, user_modification, date_create, date_modification,
            reactivate, observations, retired_value_1
     FROM online_payment.online_payments_historical'
    ) AS t1(
        id_online_payment_historical bigint,
        description character varying,
        project_id character varying,
        retired_value character varying,
        sender_ip character varying,
        tramit_number character varying,
        update_date timestamp without time zone,
        value_updated character varying,
        online_payment_id bigint,
        enabled boolean,
        user_create character varying,
        user_modification character varying,
        date_create character varying,
        date_modification character varying,
        reactivate integer,
        observations character varying,
        retired_value_1 character varying
    );
-- 2. Recalcular el monto descontado y actualizar la fact_pago
-- Se ordenan por ID histórico para simular la línea de tiempo del saldo (value_updated)
WITH desc_saldos AS (
    SELECT TRIM(oph.project_id) AS project_id,
        TRIM(oph.tramit_number) AS tramit_number,
        COALESCE(
            LAG(REPLACE(oph.value_updated::TEXT, ',', '.')::numeric) OVER (
                PARTITION BY TRIM(oph.tramit_number)
                ORDER BY oph.id_online_payment_historical ASC
            ),
            (
                REPLACE(oph.value_updated::TEXT, ',', '.')::numeric + REPLACE(COALESCE(oph.retired_value::TEXT, '0'), ',', '.')::numeric
            )
        ) AS saldo_anterior,
        REPLACE(oph.value_updated::TEXT, ',', '.')::numeric AS saldo_actual
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
-- 3. Volver a calcular secuencia tras la reestructuración de montos
SELECT dw.sp_calcular_secuencia_pagos();