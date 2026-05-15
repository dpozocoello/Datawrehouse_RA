-- ==============================================================================
-- ETL v2 — Carga de datos para las nuevas estructuras
-- Ejecutar DESPUÉS de ddl_dwh_v2.sql
-- Ejecutar: psql -U postgres -d dw_reg_v1 -f etl_carga_datos_v2.sql
-- ==============================================================================
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 1. Cargar area_responsable en dim_proyecto                                ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
UPDATE dw.dim_proyecto dp
SET area_responsable = sub.area_responsable_proyecto
FROM (
        SELECT DISTINCT ON (codigo_proyecto) codigo_proyecto,
            area_responsable_proyecto
        FROM stg.consolidado_proyectos
        WHERE area_responsable_proyecto IS NOT NULL
            AND area_responsable_proyecto != ''
        ORDER BY codigo_proyecto
    ) sub
WHERE dp.codigo_proyecto = sub.codigo_proyecto
    AND (
        dp.area_responsable IS NULL
        OR dp.area_responsable = ''
    );
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 2. Poblar Bridge Table: fact_proyecto_geografia                           ║
-- ║    Inserta TODAS las ubicaciones por proyecto (relación M:N)              ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
CREATE OR REPLACE FUNCTION dw.sp_carga_proyecto_geografia() RETURNS void AS $$ BEGIN -- Truncar y recargar
    TRUNCATE TABLE dw.fact_proyecto_geografia;
-- Insertar todas las combinaciones únicas proyecto ↔ geografía
INSERT INTO dw.fact_proyecto_geografia (sk_proyecto, sk_geografia, es_principal)
SELECT DISTINCT f.sk_proyecto,
    f.sk_geografia,
    false -- Se marca como principal abajo
FROM dw.fact_regularizacion f
WHERE f.sk_geografia IS NOT NULL ON CONFLICT (sk_proyecto, sk_geografia) DO NOTHING;
-- Marcar la primera ubicación (por orden de tarea más reciente) como principal
-- Esto replica el criterio de DISTINCT ON usado en las consultas actuales
UPDATE dw.fact_proyecto_geografia fpg
SET es_principal = true
FROM (
        SELECT DISTINCT ON (f.sk_proyecto) f.sk_proyecto,
            f.sk_geografia
        FROM dw.fact_regularizacion f
        WHERE f.sk_geografia IS NOT NULL
        ORDER BY f.sk_proyecto,
            f.fecha_fin_tarea DESC NULLS LAST
    ) ppal
WHERE fpg.sk_proyecto = ppal.sk_proyecto
    AND fpg.sk_geografia = ppal.sk_geografia;
RAISE NOTICE 'Bridge proyecto-geografia: % registros (% proyectos)',
(
    SELECT COUNT(1)
    FROM dw.fact_proyecto_geografia
),
(
    SELECT COUNT(DISTINCT sk_proyecto)
    FROM dw.fact_proyecto_geografia
);
END;
$$ LANGUAGE plpgsql;
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 3. SP: Carga de fact_pago v2 (con DISTINCT ON + tramit_number M:N)       ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
CREATE OR REPLACE FUNCTION dw.sp_carga_fact_pago() RETURNS void AS $$ BEGIN -- PARTE A: Pagos JBPM directos por project_id
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
$$ LANGUAGE plpgsql;
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 4. SP: Calcular secuencia de pagos (depósito/ordinal)                     ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
CREATE OR REPLACE FUNCTION dw.sp_calcular_secuencia_pagos() RETURNS void AS $$ BEGIN -- Calcular secuencia por tramit_number, ordenada por fecha y ID
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
-- Para pagos sin tramit_number (SUIA), marcar como depósito individual
UPDATE dw.fact_pago
SET secuencia_pago = 1,
    es_deposito_inicial = true,
    monto_acumulado = monto_transaccion
WHERE numero_tramite IS NULL
    AND secuencia_pago IS NULL;
RAISE NOTICE 'Secuencia de pagos calculada: % con secuencia, % depósitos iniciales',
(
    SELECT COUNT(1)
    FROM dw.fact_pago
    WHERE secuencia_pago IS NOT NULL
),
(
    SELECT COUNT(1)
    FROM dw.fact_pago
    WHERE es_deposito_inicial = true
);
END;
$$ LANGUAGE plpgsql;
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 5. Ejecutar todas las cargas v2                                            ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
-- 5.1 Cargar bridge table
SELECT dw.sp_carga_proyecto_geografia();
-- 5.2 Calcular secuencia de pagos (sobre datos ya cargados)
SELECT dw.sp_calcular_secuencia_pagos();
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 6. Verificación rápida                                                     ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
-- V1: Bridge table
SELECT 'fact_proyecto_geografia' AS tabla,
    COUNT(1) AS total_registros,
    COUNT(DISTINCT sk_proyecto) AS proyectos,
    COUNT(DISTINCT sk_geografia) AS ubicaciones,
    SUM(
        CASE
            WHEN es_principal THEN 1
            ELSE 0
        END
    ) AS principales
FROM dw.fact_proyecto_geografia;
-- V2: Jerarquía geográfica
SELECT nivel,
    COUNT(1) AS registros
FROM dw.dim_geografia
GROUP BY nivel
ORDER BY nivel;
-- V3: Secuencia de pagos
SELECT COUNT(1) FILTER (
        WHERE secuencia_pago IS NOT NULL
    ) AS con_secuencia,
    COUNT(1) FILTER (
        WHERE es_deposito_inicial = true
    ) AS depositos_iniciales,
    COUNT(1) FILTER (
        WHERE secuencia_pago > 1
    ) AS pagos_subsecuentes,
    COUNT(1) AS total
FROM dw.fact_pago;
-- V4: Ejemplo de secuencia por tramit_number
SELECT fp.numero_tramite,
    dp.codigo_proyecto,
    fp.secuencia_pago,
    fp.es_deposito_inicial,
    fp.monto_transaccion,
    fp.monto_acumulado
FROM dw.fact_pago fp
    JOIN dw.dim_proyecto dp ON dp.sk_proyecto = fp.sk_proyecto
WHERE fp.numero_tramite IN ('1472163211', '1891165388')
ORDER BY fp.numero_tramite,
    fp.secuencia_pago;
-- V5: area_responsable cargada
SELECT COUNT(1) FILTER (
        WHERE area_responsable IS NOT NULL
    ) AS con_area,
    COUNT(1) FILTER (
        WHERE area_responsable IS NULL
    ) AS sin_area,
    COUNT(1) AS total
FROM dw.dim_proyecto;