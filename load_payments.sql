-- ==============================================================================
-- SCRIPT DE CARGA DE PAGOS Y FIX SPs
-- ==============================================================================
-- 1. CARGA DE PAGOS JBPM
TRUNCATE TABLE stg.online_payments_bi;
INSERT INTO stg.online_payments_bi (
        online_payment_id,
        project_id,
        tramit_number,
        convenience_number,
        bank_code,
        payment_value,
        date_hour_transaction,
        transaction_type,
        transaction_state
    )
SELECT *
FROM dblink(
        'dbname=jbpmdb port=5432 host=172.16.0.226 user=postgres password=postgres',
        'SELECT online_payment_id, project_id, tramit_number, convenience_number, bank_code, payment_value, date_hour_transaction, transaction_type, transaction_state FROM online_payment'
    ) AS t(
        online_payment_id INTEGER,
        project_id VARCHAR(255),
        tramit_number VARCHAR(255),
        convenience_number VARCHAR(255),
        bank_code VARCHAR(50),
        payment_value NUMERIC(12, 2),
        date_hour_transaction TIMESTAMP,
        transaction_type VARCHAR(100),
        transaction_state BOOLEAN
    );
-- 2. CARGA DE PAGOS SUIA
TRUNCATE TABLE stg.financial_transaction_bi;
INSERT INTO stg.financial_transaction_bi (
        fitr_id,
        codigo_proyecto,
        fitr_transaction_amount,
        fitr_paid_value,
        fitr_transaction_number,
        fitr_payment_type,
        payment_type_desc,
        fitr_creation_date,
        fitr_status,
        task_name,
        processname,
        processinstanceid
    )
SELECT *
FROM dblink(
        'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
        'SELECT fitr_id, codigo_proyecto, fitr_transaction_amount, fitr_paid_value, fitr_transaction_number, fitr_payment_type, payment_type_desc, fitr_creation_date, fitr_status, task_name, processname, processinstanceid FROM suia_iii.financial_transaction_bi'
    ) AS t(
        fitr_id INTEGER,
        codigo_proyecto VARCHAR(255),
        fitr_transaction_amount NUMERIC(12, 2),
        fitr_paid_value NUMERIC(12, 2),
        fitr_transaction_number VARCHAR(255),
        fitr_payment_type INTEGER,
        payment_type_desc VARCHAR(100),
        fitr_creation_date TIMESTAMP,
        fitr_status BOOLEAN,
        task_name VARCHAR(255),
        processname VARCHAR(255),
        processinstanceid BIGINT
    );
-- 3. FIX sp_carga_hechos (interseccion_snap VARCHAR(2))
CREATE OR REPLACE FUNCTION dw.sp_carga_hechos() RETURNS void AS $$ BEGIN TRUNCATE TABLE dw.fact_regularizacion;
INSERT INTO dw.fact_regularizacion (
        sk_proyecto,
        sk_proponente,
        sk_actividad,
        sk_geografia,
        sk_usuario,
        sk_estado,
        sk_fecha_registro,
        interseccion_snap,
        areas_protegidas,
        superficie_proyecto,
        id_area,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        proceso,
        tarea,
        nombre_zona,
        finalizado_con_resolucion,
        numero_resolucion,
        fecha_resolucion,
        ente_acreditado,
        origen
    )
SELECT dp.sk_proyecto,
    dpp.sk_proponente,
    da.sk_actividad,
    dg.sk_geografia,
    du.sk_usuario,
    de.sk_estado,
    dt.sk_tiempo,
    CASE
        WHEN snap.codigo_proyecto IS NOT NULL THEN 'SI'
        WHEN c.intersecta_con IS NOT NULL
        AND c.intersecta_con NOT IN ('NO', '') THEN 'SI'
        ELSE 'NO'
    END,
    c.areas_protegidas,
    COALESCE(c.superficie_proyecto, 0),
    COALESCE(c.id_area, 0),
    c.fecha_inicio_proceso,
    c.fecha_fin_proceso,
    c.fecha_inicio_tarea,
    c.fecha_fin_tarea,
    c.proceso,
    c.tarea,
    c.nombre_zona,
    c.finalizado_con_resolucion,
    c.numero_resolucion,
    c.fecha_resolucion,
    c.ente_acreditado,
    c.origen
FROM stg.consolidado_proyectos c
    LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = c.codigo_proyecto
    LEFT JOIN dw.dim_proponente dpp ON dpp.ced_ruc_proponente = c.ced_ruc_proponente
    LEFT JOIN dw.dim_actividad da ON da.codigo_actividad = c.codigo_actividad
    LEFT JOIN dw.dim_geografia dg ON dg.provincia = COALESCE(c.provincia, 'N/A')
    AND dg.canton = COALESCE(c.canton, 'N/A')
    AND dg.parroquia = COALESCE(c.parroquia, 'N/A')
    LEFT JOIN dw.dim_usuario du ON du.usuario_tarea = c.usuario_tarea
    LEFT JOIN dw.dim_estado de ON de.estado_proceso = COALESCE(c.estado_proceso, 'N/A')
    AND de.estado_proyecto = COALESCE(c.estado_proyecto, 'N/A')
    AND de.estado_tramite = COALESCE(c.estado_tramite, 'N/A')
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = c.fecha_registro
    LEFT JOIN stg.jbpm_snap_variables snap ON snap.codigo_proyecto = c.codigo_proyecto;
-- Cargar proyectos recuperados que no estan en el consolidado (Usar sk=0 temporalmente si dim_proyecto permitiera, pero mejor NULL)
INSERT INTO dw.fact_regularizacion (
        sk_proyecto,
        sk_proponente,
        sk_geografia,
        sk_actividad,
        sk_fecha_registro,
        origen
    )
SELECT dp.sk_proyecto,
    NULL,
    NULL,
    NULL,
    NULL,
    'RECUPERADO'
FROM dw.dim_proyecto dp
WHERE NOT EXISTS (
        SELECT 1
        FROM dw.fact_regularizacion fr
        WHERE fr.sk_proyecto = dp.sk_proyecto
    );
RAISE NOTICE 'Fact table cargada exitosamente';
END;
$$ LANGUAGE plpgsql;
-- 4. EJECUTAR TODO EL PROCESO FINAL
SELECT dw.sp_consolidar_staging();
SELECT dw.sp_carga_dimensiones();
SELECT dw.sp_carga_hechos();
SELECT dw.sp_carga_dim_pago();
SELECT dw.sp_carga_fact_pago();