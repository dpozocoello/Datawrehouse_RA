-- Final Dim Sanitization v1.4.1
-- Corrected column names for sk=0 records.
BEGIN;
-- 1. Area
DELETE FROM dw.dim_area
WHERE sk_area = 0
    OR id_area = 0;
INSERT INTO dw.dim_area (
        sk_area,
        id_area,
        nombre_area,
        provincia,
        canton,
        parroquia
    )
VALUES (0, 0, 'AREA NO DEFINIDA', 'N/A', 'N/A', 'N/A');
-- 2. Proyecto
DELETE FROM dw.dim_proyecto
WHERE sk_proyecto = 0
    OR codigo_proyecto = 'N/A';
INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
VALUES (0, 'N/A', 'PROYECTO NO DEFINIDO');
-- 3. Proponente
DELETE FROM dw.dim_proponente
WHERE sk_proponente = 0
    OR ced_ruc_proponente = 'N/A';
INSERT INTO dw.dim_proponente (
        sk_proponente,
        ced_ruc_proponente,
        nombre_proponente
    )
VALUES (0, 'N/A', 'PROPONENTE NO DEFINIDO');
-- 4. Actividad
DELETE FROM dw.dim_actividad
WHERE sk_actividad = 0
    OR codigo_actividad = 'N/A';
INSERT INTO dw.dim_actividad (sk_actividad, codigo_actividad, actividad)
VALUES (0, 'N/A', 'ACTIVIDAD NO DEFINIDA');
-- 5. Geografia
DELETE FROM dw.dim_geografia
WHERE sk_geografia = 0
    OR (
        provincia = 'N/A'
        AND canton = 'N/A'
    );
INSERT INTO dw.dim_geografia (sk_geografia, provincia, canton, parroquia)
VALUES (0, 'N/A', 'N/A', 'N/A');
-- 6. Estado
DELETE FROM dw.dim_estado
WHERE sk_estado = 0
    OR (
        estado_proceso = 'N/A'
        AND estado_proyecto = 'N/A'
    );
INSERT INTO dw.dim_estado (
        sk_estado,
        estado_proceso,
        estado_proyecto,
        estado_tramite
    )
VALUES (0, 'N/A', 'N/A', 'N/A');
-- 7. Tiempo
DELETE FROM dw.dim_tiempo
WHERE sk_tiempo = 0
    OR fecha = '1900-01-01';
INSERT INTO dw.dim_tiempo (sk_tiempo, fecha)
VALUES (0, '1900-01-01');
-- 8. Pago (if exists)
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'dw'
        AND table_name = 'dim_pago'
) THEN
DELETE FROM dw.dim_pago
WHERE sk_pago = 0;
INSERT INTO dw.dim_pago (sk_pago, codigo_pago)
VALUES (0, 'N/A') ON CONFLICT DO NOTHING;
END IF;
END $$;
COMMIT;