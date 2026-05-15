-- ==============================================================================
-- 1. CREACIÓN DE ESQUEMAS
-- ==============================================================================
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS dw;
-- Limpiar objetos si existían corruptos
DROP TABLE IF EXISTS stg.suia_rcoa_bi CASCADE;
DROP TABLE IF EXISTS stg.jbpm_snap_variables CASCADE;
DROP TABLE IF EXISTS dw.fact_regularizacion CASCADE;
DROP TABLE IF EXISTS dw.dim_proyecto CASCADE;
DROP TABLE IF EXISTS dw.dim_geografia CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_dimensiones CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_hechos CASCADE;
-- ==============================================================================
-- 2. DDL - CAPA DE STAGING (STG)
-- ==============================================================================
-- Staging para SUIA ENLISY (Sin acentos ni mayúsculas complejas)
CREATE TABLE stg.suia_rcoa_bi (
    codigo_proyecto VARCHAR(255),
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    fecha_registro DATE,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    ced_ruc_proponente VARCHAR(255),
    nombre_proponente VARCHAR(500),
    area_responsable_proyecto VARCHAR(500),
    tipo_sector VARCHAR(255),
    tipo_permiso_ambiental VARCHAR(255),
    tipo_ente VARCHAR(255),
    provincia VARCHAR(255),
    canton VARCHAR(255),
    parroquia VARCHAR(255),
    proceso VARCHAR(255),
    estado_proceso VARCHAR(255),
    fecha_inicio_proceso DATE,
    fecha_fin_proceso DATE,
    tarea VARCHAR(500),
    estado_tarea VARCHAR(255),
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    usuario_tarea VARCHAR(255),
    estado_proyecto VARCHAR(255),
    intersecta_con TEXT,
    areas_protegidas TEXT,
    sistema VARCHAR(255),
    nombre_zona VARCHAR(255),
    finalizado_con_resolucion VARCHAR(255),
    numero_resolucion VARCHAR(255),
    fecha_resolucion TIMESTAMP,
    id_area INTEGER,
    estado_tramite VARCHAR(255),
    superficie_proyecto DOUBLE PRECISION,
    fecha_carga TIMESTAMP
);
-- Staging para Variables JBPM (Intersecciones SNAP)
CREATE TABLE stg.jbpm_snap_variables (
    codigo_proyecto TEXT,
    processinstanceid BIGINT,
    nombre_proceso TEXT,
    estado_proceso INTEGER,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP
);
-- ==============================================================================
-- 3. DDL - CAPA DIMENSIONAL (DW)
-- ==============================================================================
CREATE TABLE dw.dim_proyecto (
    sk_proyecto SERIAL PRIMARY KEY,
    codigo_proyecto VARCHAR(255) UNIQUE,
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    tipo_permiso_ambiental VARCHAR(255)
);
CREATE TABLE dw.dim_geografia (
    sk_geografia SERIAL PRIMARY KEY,
    provincia VARCHAR(255),
    canton VARCHAR(255),
    parroquia VARCHAR(255),
    CONSTRAINT uk_geo UNIQUE (provincia, canton, parroquia)
);
CREATE TABLE dw.fact_regularizacion (
    sk_proyecto INT REFERENCES dw.dim_proyecto(sk_proyecto),
    sk_geografia INT REFERENCES dw.dim_geografia(sk_geografia),
    fecha_registro DATE,
    estado_tramite VARCHAR(255),
    interseccion_snap VARCHAR(2),
    superficie_proyecto DOUBLE PRECISION,
    fecha_carga TIMESTAMP DEFAULT NOW()
);
-- ==============================================================================
-- 4. PROCEDIMIENTOS DE TRANSFORMACIÓN (DML)
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_dimensiones() RETURNS void AS $$ BEGIN -- Cargar Dimensión Proyecto
INSERT INTO dw.dim_proyecto (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        tipo_permiso_ambiental
    )
SELECT DISTINCT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    tipo_permiso_ambiental
FROM stg.suia_rcoa_bi
WHERE codigo_proyecto IS NOT NULL ON CONFLICT (codigo_proyecto) DO
UPDATE
SET nombre_proyecto = EXCLUDED.nombre_proyecto,
    tipo_permiso_ambiental = EXCLUDED.tipo_permiso_ambiental;
-- Cargar Dimensión Geografía
INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
SELECT DISTINCT provincia,
    canton,
    parroquia
FROM stg.suia_rcoa_bi
WHERE provincia IS NOT NULL ON CONFLICT (provincia, canton, parroquia) DO NOTHING;
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION dw.sp_carga_hechos() RETURNS void AS $$ BEGIN -- Truncar hechos pasados
    TRUNCATE TABLE dw.fact_regularizacion;
INSERT INTO dw.fact_regularizacion (
        sk_proyecto,
        sk_geografia,
        fecha_registro,
        estado_tramite,
        interseccion_snap,
        superficie_proyecto
    )
SELECT dp.sk_proyecto,
    dg.sk_geografia,
    stg.fecha_registro,
    stg.estado_proceso,
    CASE
        WHEN snap.codigo_proyecto IS NOT NULL THEN 'SI'
        ELSE 'NO'
    END AS interseccion_snap,
    stg.superficie_proyecto
FROM stg.suia_rcoa_bi stg
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = stg.codigo_proyecto
    LEFT JOIN dw.dim_geografia dg ON dg.provincia = stg.provincia
    AND dg.canton = stg.canton
    AND dg.parroquia = stg.parroquia
    LEFT JOIN stg.jbpm_snap_variables snap ON snap.codigo_proyecto = stg.codigo_proyecto;
END;
$$ LANGUAGE plpgsql;