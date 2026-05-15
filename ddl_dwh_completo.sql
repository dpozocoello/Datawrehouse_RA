-- ==============================================================================
-- SCRIPT COMPLETO DDL/DML - DATA WAREHOUSE dw_reg_v1
-- Regularizacion Ambiental - Modelo Estrella
-- ==============================================================================
-- EJECUCION: psql -U postgres -d dw_reg_v1 -f ddl_dwh_completo.sql
-- ==============================================================================
-- 1. ESQUEMAS
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS dw;
-- ==============================================================================
-- 2. LIMPIEZA TOTAL (DROP CASCADE)
-- ==============================================================================
DROP TABLE IF EXISTS dw.fact_regularizacion CASCADE;
DROP TABLE IF EXISTS dw.dim_proyecto CASCADE;
DROP TABLE IF EXISTS dw.dim_geografia CASCADE;
DROP TABLE IF EXISTS dw.dim_proponente CASCADE;
DROP TABLE IF EXISTS dw.dim_actividad CASCADE;
DROP TABLE IF EXISTS dw.dim_usuario CASCADE;
DROP TABLE IF EXISTS dw.dim_estado CASCADE;
DROP TABLE IF EXISTS dw.dim_tiempo CASCADE;
DROP TABLE IF EXISTS stg.suia_rcoa_bi CASCADE;
DROP TABLE IF EXISTS stg.suia_coa_bi CASCADE;
DROP TABLE IF EXISTS stg.jbpm_sector_bi CASCADE;
DROP TABLE IF EXISTS stg.jbpm_4cat_bi CASCADE;
DROP TABLE IF EXISTS stg.jbpm_hidro_bi CASCADE;
DROP TABLE IF EXISTS stg.jbpm_snap_variables CASCADE;
DROP TABLE IF EXISTS stg.consolidado_proyectos CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_dimensiones() CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_hechos() CASCADE;
DROP FUNCTION IF EXISTS dw.sp_consolidar_staging() CASCADE;
-- ==============================================================================
-- 3. TABLAS STAGING - Una por cada origen remoto
-- ==============================================================================
-- 3.1 Origen: suia_enlisy / coa_mae.tmp_rcoa_bi
CREATE TABLE stg.suia_rcoa_bi (
    codigo_proyecto TEXT,
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    fecha_registro DATE,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    ced_ruc_proponente TEXT,
    nombre_proponente TEXT,
    area_responsable_proyecto TEXT,
    tipo_sector TEXT,
    tipo_permiso_ambiental TEXT,
    tipo_ente TEXT,
    provincia TEXT,
    canton TEXT,
    parroquia TEXT,
    proceso TEXT,
    estado_proceso TEXT,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP,
    tarea TEXT,
    estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT,
    estado_proyecto TEXT,
    intersecta_con TEXT,
    areas_protegidas TEXT,
    sistema TEXT,
    nombre_zona VARCHAR(500),
    finalizado_con_resolucion VARCHAR(500),
    numero_resolucion VARCHAR(500),
    fecha_resolucion TIMESTAMP,
    id_area INTEGER,
    estado_tramite TEXT,
    superficie_proyecto DOUBLE PRECISION,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'RCOA'
);
-- 3.2 Origen: suia_enlisy / suia_iii.tmp_coa_bi
CREATE TABLE stg.suia_coa_bi (
    codigo_proyecto TEXT,
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    fecha_registro DATE,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    ced_ruc_proponente TEXT,
    nombre_proponente TEXT,
    area_responsable_proyecto TEXT,
    tipo_sector TEXT,
    tipo_permiso_ambiental TEXT,
    tipo_ente TEXT,
    provincia TEXT,
    canton TEXT,
    parroquia TEXT,
    proceso TEXT,
    estado_proceso TEXT,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP,
    tarea TEXT,
    estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT,
    estado_proyecto TEXT,
    intersecta_con TEXT,
    areas_protegidas TEXT,
    sistema TEXT,
    nombre_zona VARCHAR(500),
    finalizado_con_resolucion VARCHAR(500),
    numero_resolucion VARCHAR(500),
    fecha_resolucion TIMESTAMP,
    id_area INTEGER,
    estado_tramite TEXT,
    superficie_proyecto DOUBLE PRECISION,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'COA'
);
-- 3.3 Origen: jbpmdb_prod_old / public.vm_sector_subsector_bi
CREATE TABLE stg.jbpm_sector_bi (
    codigo_proyecto VARCHAR(255),
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    fecha_registro DATE,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    ced_ruc_proponente VARCHAR(255),
    nombre_proponente TEXT,
    area_responsable_proyecto TEXT,
    tipo_sector VARCHAR(255),
    tipo_permiso_ambiental TEXT,
    tipo_ente TEXT,
    provincia TEXT,
    canton TEXT,
    parroquia TEXT,
    proceso TEXT,
    estado_proceso TEXT,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP,
    tarea VARCHAR(500),
    estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT,
    estado_proyecto TEXT,
    intersecta_con TEXT,
    areas_protegidas TEXT,
    sistema TEXT,
    ente_acreditado TEXT,
    estado_tramite TEXT,
    estrategico TEXT,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'JBPM_SECTOR'
);
-- 3.4 Origen: jbpmdb / public.vm_cuatro_categorias_bi
CREATE TABLE stg.jbpm_4cat_bi (
    codigo_proyecto VARCHAR(255),
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    fecha_registro DATE,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    ced_ruc_proponente VARCHAR(255),
    nombre_proponente TEXT,
    area_responsable_proyecto TEXT,
    tipo_sector VARCHAR(255),
    tipo_permiso_ambiental TEXT,
    tipo_ente TEXT,
    provincia TEXT,
    canton TEXT,
    parroquia TEXT,
    proceso TEXT,
    estado_proceso TEXT,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP,
    tarea VARCHAR(500),
    estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT,
    estado_proyecto TEXT,
    intersecta_con TEXT,
    areas_protegidas TEXT,
    sistema TEXT,
    ente_acreditado TEXT,
    estado_tramite TEXT,
    estrategico TEXT,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'JBPM_4CAT'
);
-- 3.5 Origen: jbpmdb / public.vwt_hidrocarbonos_bi
CREATE TABLE stg.jbpm_hidro_bi (
    codigo_proyecto VARCHAR(255),
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    fecha_registro DATE,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    ced_ruc_proponente VARCHAR(255),
    nombre_proponente VARCHAR(500),
    area_responsable_proyecto TEXT,
    tipo_sector VARCHAR(255),
    tipo_permiso_ambiental TEXT,
    tipo_ente TEXT,
    provincia TEXT,
    canton TEXT,
    parroquia TEXT,
    proceso TEXT,
    estado_proceso TEXT,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP,
    tarea VARCHAR(500),
    estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT,
    estado_proyecto TEXT,
    intersecta_con TEXT,
    id_area INTEGER,
    ente_acreditado TEXT,
    estado_tramite TEXT,
    estrategico TEXT,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'JBPM_HIDRO'
);
-- 3.6 Origen: suia_bpms_enlisy_app (Variables SNAP del BPM)
CREATE TABLE stg.jbpm_snap_variables (
    codigo_proyecto TEXT,
    processinstanceid BIGINT,
    nombre_proceso TEXT,
    estado_proceso INTEGER,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP
);
-- 3.7 Origen: suia_enlisy - public.areas (v1.1)
CREATE TABLE stg.suia_areas_bi (
    area_id INT,
    area_name TEXT,
    area_abbreviation TEXT,
    area_parent_id INT,
    zone_id INT,
    area_status BOOLEAN,
    area_campus TEXT,
    arty_id INT,
    fecha_carga TIMESTAMP DEFAULT NOW()
);
-- 3.7 Tabla consolidada (UNION ALL de todos los STG)
CREATE TABLE stg.consolidado_proyectos (
    codigo_proyecto TEXT,
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    fecha_registro DATE,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    ced_ruc_proponente TEXT,
    nombre_proponente TEXT,
    area_responsable_proyecto TEXT,
    tipo_sector TEXT,
    tipo_permiso_ambiental TEXT,
    tipo_ente TEXT,
    provincia TEXT,
    canton TEXT,
    parroquia TEXT,
    proceso TEXT,
    estado_proceso TEXT,
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP,
    tarea TEXT,
    estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT,
    estado_proyecto TEXT,
    intersecta_con TEXT,
    areas_protegidas TEXT,
    sistema TEXT,
    nombre_zona VARCHAR(500),
    finalizado_con_resolucion VARCHAR(500),
    numero_resolucion VARCHAR(500),
    fecha_resolucion TIMESTAMP,
    ente_acreditado TEXT,
    estado_tramite TEXT,
    id_area INTEGER DEFAULT 0,
    superficie_proyecto DOUBLE PRECISION DEFAULT 0,
    estrategico TEXT,
    origen VARCHAR(50)
);
-- ==============================================================================
-- 4. TABLAS DIMENSIONALES (DW)
-- ==============================================================================
CREATE TABLE dw.dim_tiempo (
    sk_tiempo SERIAL PRIMARY KEY,
    fecha DATE UNIQUE,
    anio INTEGER,
    mes INTEGER,
    dia INTEGER,
    trimestre INTEGER,
    nombre_mes VARCHAR(20),
    dia_semana VARCHAR(15)
);
CREATE TABLE dw.dim_proyecto (
    sk_proyecto SERIAL PRIMARY KEY,
    codigo_proyecto VARCHAR(255) UNIQUE,
    nombre_proyecto TEXT,
    resumen_proyecto TEXT,
    direccion_proyecto TEXT,
    tipo_permiso_ambiental VARCHAR(255),
    tipo_sector VARCHAR(255),
    tipo_ente TEXT,
    sistema VARCHAR(255),
    estrategico TEXT
);
CREATE TABLE dw.dim_proponente (
    sk_proponente SERIAL PRIMARY KEY,
    ced_ruc_proponente VARCHAR(255) UNIQUE,
    nombre_proponente TEXT
);
CREATE TABLE dw.dim_actividad (
    sk_actividad SERIAL PRIMARY KEY,
    codigo_actividad TEXT,
    actividad_economica TEXT,
    CONSTRAINT uk_actividad UNIQUE (codigo_actividad)
);
CREATE TABLE dw.dim_geografia (
    sk_geografia SERIAL PRIMARY KEY,
    provincia VARCHAR(255),
    canton VARCHAR(255),
    parroquia VARCHAR(255),
    CONSTRAINT uk_geo UNIQUE (provincia, canton, parroquia)
);
CREATE TABLE dw.dim_usuario (
    sk_usuario SERIAL PRIMARY KEY,
    usuario_tarea TEXT UNIQUE
);
CREATE TABLE dw.dim_estado (
    sk_estado SERIAL PRIMARY KEY,
    estado_proceso TEXT,
    estado_proyecto TEXT,
    estado_tramite TEXT,
    CONSTRAINT uk_estado UNIQUE (estado_proceso, estado_proyecto, estado_tramite)
);
-- 4.8 Dimension de Area (Oficinas Tecnicas) (v1.1)
CREATE TABLE dw.dim_area (
    sk_area SERIAL PRIMARY KEY,
    id_area INT UNIQUE,
    nombre_area TEXT,
    abreviatura_area TEXT,
    id_area_padre INT,
    zona TEXT,
    campus TEXT,
    estado_area TEXT,
    fecha_carga TIMESTAMP DEFAULT NOW()
);
-- ==============================================================================
-- 5. TABLA DE HECHOS (FACT TABLE)
-- ==============================================================================
CREATE TABLE dw.fact_regularizacion (
    id_fact SERIAL PRIMARY KEY,
    sk_proyecto INT REFERENCES dw.dim_proyecto(sk_proyecto),
    sk_proponente INT REFERENCES dw.dim_proponente(sk_proponente),
    sk_actividad INT REFERENCES dw.dim_actividad(sk_actividad),
    sk_geografia INT REFERENCES dw.dim_geografia(sk_geografia),
    sk_usuario INT REFERENCES dw.dim_usuario(sk_usuario),
    sk_estado INT REFERENCES dw.dim_estado(sk_estado),
    sk_fecha_registro INT REFERENCES dw.dim_tiempo(sk_tiempo),
    sk_area INT REFERENCES dw.dim_area(sk_area),
    -- Metricas
    interseccion_snap TEXT DEFAULT 'NO',
    areas_protegidas TEXT,
    superficie_proyecto DOUBLE PRECISION,
    id_area INTEGER,
    -- Fechas de proceso
    fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP,
    fecha_inicio_tarea TIMESTAMP,
    fecha_fin_tarea TIMESTAMP,
    -- Tarea y proceso
    proceso TEXT,
    tarea TEXT,
    nombre_zona VARCHAR(500),
    finalizado_con_resolucion VARCHAR(500),
    numero_resolucion VARCHAR(500),
    fecha_resolucion TIMESTAMP,
    ente_acreditado TEXT,
    -- Metadata ETL
    origen VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT NOW()
);
-- Indices para rendimiento
CREATE INDEX idx_fact_proyecto ON dw.fact_regularizacion(sk_proyecto);
CREATE INDEX idx_fact_geografia ON dw.fact_regularizacion(sk_geografia);
CREATE INDEX idx_fact_fecha ON dw.fact_regularizacion(sk_fecha_registro);
-- Index idx_fact_snap removed due to B-Tree size limits (v1.1)
-- ==============================================================================
-- 6. FUNCIONES DE TRANSFORMACION
-- ==============================================================================
-- 6.1 Consolidar todos los STG en una sola tabla intermedia
CREATE OR REPLACE FUNCTION dw.sp_consolidar_staging() RETURNS void AS $$ BEGIN TRUNCATE TABLE stg.consolidado_proyectos;
-- RCOA
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        nombre_zona,
        finalizado_con_resolucion,
        numero_resolucion,
        fecha_resolucion,
        ente_acreditado,
        estado_tramite,
        id_area,
        superficie_proyecto,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    nombre_zona,
    finalizado_con_resolucion,
    numero_resolucion,
    fecha_resolucion,
    '',
    estado_tramite,
    id_area,
    superficie_proyecto,
    '',
    origen
FROM stg.suia_rcoa_bi;
-- COA
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        nombre_zona,
        finalizado_con_resolucion,
        numero_resolucion,
        fecha_resolucion,
        ente_acreditado,
        estado_tramite,
        id_area,
        superficie_proyecto,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    nombre_zona,
    finalizado_con_resolucion,
    numero_resolucion,
    fecha_resolucion,
    '',
    estado_tramite,
    id_area,
    superficie_proyecto,
    '',
    origen
FROM stg.suia_coa_bi;
-- JBPM SECTOR
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        ente_acreditado,
        estado_tramite,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    ente_acreditado,
    estado_tramite,
    estrategico,
    origen
FROM stg.jbpm_sector_bi;
-- JBPM 4 CATEGORIAS
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        ente_acreditado,
        estado_tramite,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    ente_acreditado,
    estado_tramite,
    estrategico,
    origen
FROM stg.jbpm_4cat_bi;
-- JBPM HIDROCARBUROS
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        ente_acreditado,
        estado_tramite,
        id_area,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    ente_acreditado,
    estado_tramite,
    id_area,
    estrategico,
    origen
FROM stg.jbpm_hidro_bi;
RAISE NOTICE 'Consolidado STG completado: % filas',
(
    SELECT COUNT(1)
    FROM stg.consolidado_proyectos
);
END;
$$ LANGUAGE plpgsql;
-- 6.2 Cargar todas las dimensiones
CREATE OR REPLACE FUNCTION dw.sp_carga_dimensiones() RETURNS void AS $$ BEGIN -- Dimension Tiempo (rango de 20 anios)
INSERT INTO dw.dim_tiempo (
        fecha,
        anio,
        mes,
        dia,
        trimestre,
        nombre_mes,
        dia_semana
    )
SELECT d::date,
    EXTRACT(
        YEAR
        FROM d
    ),
    EXTRACT(
        MONTH
        FROM d
    ),
    EXTRACT(
        DAY
        FROM d
    ),
    EXTRACT(
        QUARTER
        FROM d
    ),
    TO_CHAR(d, 'TMMonth'),
    TO_CHAR(d, 'TMDay')
FROM generate_series(
        '2005-01-01'::date,
        '2030-12-31'::date,
        '1 day'::interval
    ) d ON CONFLICT (fecha) DO NOTHING;
-- Dimension Proyecto
INSERT INTO dw.dim_proyecto (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        tipo_permiso_ambiental,
        tipo_sector,
        tipo_ente,
        sistema,
        estrategico
    )
SELECT DISTINCT codigo_proyecto,
    MAX(nombre_proyecto),
    MAX(resumen_proyecto),
    MAX(direccion_proyecto),
    MAX(tipo_permiso_ambiental),
    MAX(tipo_sector),
    MAX(tipo_ente),
    MAX(sistema),
    MAX(estrategico)
FROM stg.consolidado_proyectos
WHERE codigo_proyecto IS NOT NULL
GROUP BY codigo_proyecto ON CONFLICT (codigo_proyecto) DO
UPDATE
SET nombre_proyecto = EXCLUDED.nombre_proyecto,
    tipo_permiso_ambiental = EXCLUDED.tipo_permiso_ambiental,
    tipo_sector = EXCLUDED.tipo_sector;
-- Proyectos recuperados de tablas de pagos (JBPM)
INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto)
SELECT DISTINCT project_id,
    'Proyecto Recuperado (JBPM)'
FROM stg.online_payments_bi
WHERE project_id IS NOT NULL
    AND project_id != '' ON CONFLICT (codigo_proyecto) DO NOTHING;
-- Proyectos recuperados de tablas de pagos (SUIA)
INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto)
SELECT DISTINCT codigo_proyecto,
    'Proyecto Recuperado (SUIA)'
FROM stg.financial_transaction_bi
WHERE codigo_proyecto IS NOT NULL
    AND codigo_proyecto != '' ON CONFLICT (codigo_proyecto) DO NOTHING;
-- Dimension Proponente
INSERT INTO dw.dim_proponente (ced_ruc_proponente, nombre_proponente)
SELECT DISTINCT ced_ruc_proponente,
    MAX(nombre_proponente)
FROM stg.consolidado_proyectos
WHERE ced_ruc_proponente IS NOT NULL
GROUP BY ced_ruc_proponente ON CONFLICT (ced_ruc_proponente) DO
UPDATE
SET nombre_proponente = EXCLUDED.nombre_proponente;
-- Dimension Actividad
INSERT INTO dw.dim_actividad (codigo_actividad, actividad_economica)
SELECT DISTINCT codigo_actividad,
    MAX(actividad_economica)
FROM stg.consolidado_proyectos
WHERE codigo_actividad IS NOT NULL
GROUP BY codigo_actividad ON CONFLICT (codigo_actividad) DO
UPDATE
SET actividad_economica = EXCLUDED.actividad_economica;
-- Dimension Geografia
INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
SELECT DISTINCT COALESCE(provincia, 'N/A'),
    COALESCE(canton, 'N/A'),
    COALESCE(parroquia, 'N/A')
FROM stg.consolidado_proyectos ON CONFLICT (provincia, canton, parroquia) DO NOTHING;
-- Asegurar registro de Cuenca Matriz
INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
VALUES ('AZUAY', 'CUENCA', 'CUENCA') ON CONFLICT (provincia, canton, parroquia) DO NOTHING;
-- Dimension Usuario
INSERT INTO dw.dim_usuario (usuario_tarea)
SELECT DISTINCT usuario_tarea
FROM stg.consolidado_proyectos
WHERE usuario_tarea IS NOT NULL ON CONFLICT (usuario_tarea) DO NOTHING;
-- Dimension Estado
INSERT INTO dw.dim_estado (estado_proceso, estado_proyecto, estado_tramite)
SELECT DISTINCT COALESCE(estado_proceso, 'N/A'),
    COALESCE(estado_proyecto, 'N/A'),
    COALESCE(estado_tramite, 'N/A')
FROM stg.consolidado_proyectos ON CONFLICT (estado_proceso, estado_proyecto, estado_tramite) DO NOTHING;
RAISE NOTICE 'Dimensiones cargadas exitosamente';
END;
$$ LANGUAGE plpgsql;
-- 6.3 Cargar Tabla de Hechos
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
-- ==============================================================================
-- 7. MODULO DE PAGOS - STAGING, DIMENSIONES Y FACT TABLE
-- ==============================================================================
-- 7.1 Limpieza modulo de pagos
DROP TABLE IF EXISTS dw.fact_pago CASCADE;
DROP TABLE IF EXISTS dw.dim_pago CASCADE;
DROP TABLE IF EXISTS stg.online_payments_bi CASCADE;
DROP TABLE IF EXISTS stg.financial_transaction_bi CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_dim_pago() CASCADE;
DROP FUNCTION IF EXISTS dw.sp_carga_fact_pago() CASCADE;
-- ==============================================================================
-- 7.2 TABLAS STAGING DE PAGOS
-- ==============================================================================
-- 7.2.1 Origen: jbpmdb @ 172.16.0.226 / online_payment
CREATE TABLE stg.online_payments_bi (
    online_payment_id INTEGER,
    project_id VARCHAR(255),
    tramit_number VARCHAR(255),
    convenience_number VARCHAR(255),
    bank_code VARCHAR(50),
    payment_value NUMERIC(12, 2),
    date_hour_transaction TIMESTAMP,
    transaction_type VARCHAR(100),
    transaction_state BOOLEAN,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'JBPM'
);
-- 7.2.2 Origen: suia_enlisy @ 172.16.0.179 / suia_iii
CREATE TABLE stg.financial_transaction_bi (
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
    processinstanceid BIGINT,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'SUIA_RCOA'
);
-- ==============================================================================
-- 7.3 DIMENSION DE PAGO (unificada ambos origenes)
-- ==============================================================================
CREATE TABLE dw.dim_pago (
    sk_pago SERIAL PRIMARY KEY,
    tipo_pago VARCHAR(100),
    bank_code VARCHAR(50),
    transaction_type VARCHAR(100),
    sistema_origen VARCHAR(50),
    CONSTRAINT uk_dim_pago UNIQUE (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
);
-- ==============================================================================
-- 7.4 FACT TABLE DE PAGOS
-- ==============================================================================
CREATE TABLE dw.fact_pago (
    id_fact_pago SERIAL PRIMARY KEY,
    sk_proyecto INT REFERENCES dw.dim_proyecto(sk_proyecto),
    sk_pago INT REFERENCES dw.dim_pago(sk_pago),
    sk_fecha_pago INT REFERENCES dw.dim_tiempo(sk_tiempo),
    -- Metricas
    monto_transaccion NUMERIC(12, 2),
    monto_pagado NUMERIC(12, 2),
    numero_transaccion VARCHAR(255),
    numero_tramite VARCHAR(255),
    -- Proceso BPM (SUIA)
    tarea_bpm VARCHAR(255),
    proceso_bpm VARCHAR(255),
    -- Metadata ETL
    origen VARCHAR(50),
    id_transaccion_origen VARCHAR(255),
    secuencia_pago INT,
    es_deposito_inicial BOOLEAN DEFAULT false,
    monto_acumulado NUMERIC(12, 2),
    fecha_carga TIMESTAMP DEFAULT NOW(),
    -- Constraint para evitar duplicados: permite un mismo pago en múltiples proyectos
    CONSTRAINT uk_fact_pago_dedup UNIQUE (sk_proyecto, id_transaccion_origen, origen)
);
-- Indices para rendimiento
CREATE INDEX idx_fact_pago_proyecto ON dw.fact_pago(sk_proyecto);
CREATE INDEX idx_fact_pago_fecha ON dw.fact_pago(sk_fecha_pago);
CREATE INDEX idx_fact_pago_origen ON dw.fact_pago(origen);
CREATE INDEX idx_fact_pago_secuencia ON dw.fact_pago(numero_tramite, secuencia_pago);
-- ==============================================================================
-- 7.5 SP: Cargar Dimension de Pagos
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_pago() RETURNS void AS $$ BEGIN -- Insertar tipos de pago desde JBPM (online_payments)
INSERT INTO dw.dim_pago (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
SELECT DISTINCT 'Online Payment',
    COALESCE(bank_code, 'N/A'),
    COALESCE(transaction_type, 'N/A'),
    'JBPM'
FROM stg.online_payments_bi
WHERE transaction_state = true ON CONFLICT (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    ) DO NOTHING;
-- Insertar tipos de pago desde SUIA (financial_transaction)
INSERT INTO dw.dim_pago (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
SELECT DISTINCT COALESCE(payment_type_desc, 'N/A'),
    'N/A',
    COALESCE(processname, 'N/A'),
    'SUIA_RCOA'
FROM stg.financial_transaction_bi
WHERE fitr_status = true ON CONFLICT (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    ) DO NOTHING;
RAISE NOTICE 'Dimension de pagos cargada: % registros',
(
    SELECT COUNT(1)
    FROM dw.dim_pago
);
END;
$$ LANGUAGE plpgsql;
-- ==============================================================================
-- 7.6 SP: Cargar Fact Table de Pagos (con deduplicacion)
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_fact_pago() RETURNS void AS $$ BEGIN -- ══════════════════════════════════════════════════════════════════
    -- PARTE A: Cargar pagos JBPM - Asociación DIRECTA por project_id
    -- ══════════════════════════════════════════════════════════════════
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
-- PARTE B (Removida por inconsistencia de datos)
-- ══════════════════════════════════════════════════════════════════
-- PARTE C: Cargar pagos SUIA (financial_transaction)
-- ══════════════════════════════════════════════════════════════════
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
RAISE NOTICE 'Fact pagos cargada total: % filas',
(
    SELECT COUNT(1)
    FROM dw.fact_pago
);
END;
$$ LANGUAGE plpgsql;