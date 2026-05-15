-- DWH Dimension Initialization Script
-- Restores "Unknown/Not Applicable" records (SK=0) after a full purge.
BEGIN;
-- 1. Dim Area
INSERT INTO dw.dim_area (
        sk_area,
        id_area,
        nombre_area,
        provincia,
        canton,
        parroquia
    )
VALUES (0, 0, 'N/A', 'N/A', 'N/A', 'N/A') ON CONFLICT (sk_area) DO NOTHING;
-- 2. Dim Proyecto
INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
VALUES (0, 'N/A', 'N/A') ON CONFLICT (sk_proyecto) DO NOTHING;
-- 3. Dim Proponente
INSERT INTO dw.dim_proponente (
        sk_proponente,
        ced_ruc_proponente,
        nombre_proponente
    )
VALUES (0, 'N/A', 'N/A') ON CONFLICT (sk_proponente) DO NOTHING;
-- 4. Dim Actividad
INSERT INTO dw.dim_actividad (sk_actividad, codigo_actividad, nombre_actividad)
VALUES (0, 'N/A', 'N/A') ON CONFLICT (sk_actividad) DO NOTHING;
-- 5. Dim Geografia
INSERT INTO dw.dim_geografia (sk_geografia, provincia, canton, parroquia)
VALUES (0, 'N/A', 'N/A', 'N/A') ON CONFLICT (sk_geografia) DO NOTHING;
-- 6. Dim Estado
INSERT INTO dw.dim_estado (
        sk_estado,
        estado_proceso,
        estado_proyecto,
        estado_tramite
    )
VALUES (0, 'N/A', 'N/A', 'N/A') ON CONFLICT (sk_estado) DO NOTHING;
-- 7. Dim Tiempo
INSERT INTO dw.dim_tiempo (sk_tiempo, fecha)
VALUES (0, '1900-01-01') ON CONFLICT (sk_tiempo) DO NOTHING;
-- 8. Dim Pago
INSERT INTO dw.dim_pago (sk_pago, codigo_pago)
VALUES (0, 'N/A') ON CONFLICT (sk_pago) DO NOTHING;
-- 9. Dim Usuario (assuming it exists based on the fact query)
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'dw'
        AND table_name = 'dim_usuario'
) THEN
INSERT INTO dw.dim_usuario (sk_usuario, usuario_tarea)
VALUES (0, 'N/A') ON CONFLICT (sk_usuario) DO NOTHING;
END IF;
END $$;
COMMIT;