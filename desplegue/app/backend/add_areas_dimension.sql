-- Step 1: Create Staging Table
CREATE TABLE IF NOT EXISTS stg.suia_areas_bi (
    area_id INT,
    area_name VARCHAR(255),
    area_abbreviation VARCHAR(255),
    area_parent_id INT,
    zone_id INT,
    area_status BOOLEAN,
    area_campus VARCHAR(255),
    arty_id INT,
    fecha_carga TIMESTAMP DEFAULT NOW()
);
-- Step 2: Create Dimension Table
CREATE TABLE IF NOT EXISTS dw.dim_area (
    sk_area SERIAL PRIMARY KEY,
    id_area INT UNIQUE,
    nombre_area VARCHAR(255),
    abreviatura_area VARCHAR(255),
    id_area_padre INT,
    zona VARCHAR(100),
    campus VARCHAR(255),
    estado_area VARCHAR(20),
    fecha_carga TIMESTAMP DEFAULT NOW()
);
-- Step 3: Add FK to Fact Table (if not exists)
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'dw'
        AND table_name = 'fact_regularizacion'
        AND column_name = 'sk_area'
) THEN
ALTER TABLE dw.fact_regularizacion
ADD COLUMN sk_area INT REFERENCES dw.dim_area(sk_area);
END IF;
END $$;
-- Step 4: Stored Procedure to load Dim Area
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_area() RETURNS void AS $$ BEGIN
INSERT INTO dw.dim_area (
        id_area,
        nombre_area,
        abreviatura_area,
        id_area_padre,
        zona,
        campus,
        estado_area
    )
SELECT area_id,
    area_name,
    area_abbreviation,
    area_parent_id,
    'ZONA ' || zone_id::text,
    area_campus,
    CASE
        WHEN area_status THEN 'ACTIVO'
        ELSE 'INACTIVO'
    END
FROM stg.suia_areas_bi ON CONFLICT (id_area) DO
UPDATE
SET nombre_area = EXCLUDED.nombre_area,
    abreviatura_area = EXCLUDED.abreviatura_area,
    id_area_padre = EXCLUDED.id_area_padre,
    zona = EXCLUDED.zona,
    campus = EXCLUDED.campus,
    estado_area = EXCLUDED.estado_area,
    fecha_carga = NOW();
-- Ensure a default record for 0/N/A
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_area
    WHERE id_area = 0
) THEN
INSERT INTO dw.dim_area (id_area, nombre_area, estado_area)
VALUES (0, 'AREA NO DEFINIDA', 'N/A');
END IF;
RAISE NOTICE 'Dimensión Areas cargada exitosamente';
END;
$$ LANGUAGE plpgsql;
-- Step 5: Update sp_carga_hechos to include sk_area
CREATE OR REPLACE FUNCTION dw.sp_carga_hechos() RETURNS void AS $$ BEGIN TRUNCATE TABLE dw.fact_regularizacion;
INSERT INTO dw.fact_regularizacion (
        sk_proyecto,
        sk_proponente,
        sk_actividad,
        sk_geografia,
        sk_usuario,
        sk_estado,
        sk_fecha_registro,
        sk_area,
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
    COALESCE(darea.sk_area, 0),
    CASE
        WHEN snap.codigo_proyecto IS NOT NULL THEN 'SI'
        ELSE COALESCE(c.intersecta_con, 'NO')
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
    LEFT JOIN stg.jbpm_snap_variables snap ON snap.codigo_proyecto = c.codigo_proyecto
    LEFT JOIN dw.dim_area darea ON darea.id_area = c.id_area;
-- Cargar proyectos recuperados que no estan en el consolidado
INSERT INTO dw.fact_regularizacion (
        sk_proyecto,
        sk_proponente,
        sk_geografia,
        sk_actividad,
        sk_fecha_registro,
        sk_area,
        origen
    )
SELECT dp.sk_proyecto,
    0,
    0,
    0,
    0,
    0,
    'RECUPERADO'
FROM dw.dim_proyecto dp
WHERE NOT EXISTS (
        SELECT 1
        FROM dw.fact_regularizacion fr
        WHERE fr.sk_proyecto = dp.sk_proyecto
    );
RAISE NOTICE 'Fact table cargada: % filas',
(
    SELECT COUNT(1)
    FROM dw.fact_regularizacion
);
END;
$$ LANGUAGE plpgsql;