-- Initialize N/A records with SK=0 for all dimensions
-- This ensures referential integrity for the fact table
DO $$ BEGIN -- PROYECTO
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_proyecto
    WHERE sk_proyecto = 0
) THEN
INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
VALUES (0, 'N/A', 'PROYECTO NO DEFINIDO');
END IF;
-- PROPONENTE
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_proponente
    WHERE sk_proponente = 0
) THEN
INSERT INTO dw.dim_proponente (
        sk_proponente,
        ced_ruc_proponente,
        nombre_proponente
    )
VALUES (0, '0000000000', 'PROPONENTE NO DEFINIDO');
END IF;
-- ACTIVIDAD
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_actividad
    WHERE sk_actividad = 0
) THEN
INSERT INTO dw.dim_actividad (
        sk_actividad,
        codigo_actividad,
        actividad_economica
    )
VALUES (0, 'N/A', 'ACTIVIDAD NO DEFINIDA');
END IF;
-- GEOGRAFIA
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_geografia
    WHERE sk_geografia = 0
) THEN
INSERT INTO dw.dim_geografia (sk_geografia, provincia, canton, parroquia)
VALUES (0, 'N/A', 'N/A', 'N/A');
END IF;
-- USUARIO
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_usuario
    WHERE sk_usuario = 0
) THEN
INSERT INTO dw.dim_usuario (sk_usuario, usuario_tarea)
VALUES (0, 'N/A');
END IF;
-- ESTADO
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_estado
    WHERE sk_estado = 0
) THEN
INSERT INTO dw.dim_estado (
        sk_estado,
        estado_proceso,
        estado_proyecto,
        estado_tramite
    )
VALUES (0, 'N/A', 'N/A', 'N/A');
END IF;
-- TIEMPO
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_tiempo
    WHERE sk_tiempo = 0
) THEN
INSERT INTO dw.dim_tiempo (sk_tiempo, fecha, anio, nombre_mes)
VALUES (0, '1900-01-01', 0, 'N/A');
END IF;
END $$;