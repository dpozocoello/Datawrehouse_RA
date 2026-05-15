-- Script de reparacion: Cargar tablas staging faltantes y recargar fact
-- Ejecutar: psql -U postgres -d dw_reg_v1 -f etl_fix_pendientes.sql
-- ==============================================================================
-- PASO 1: Cargar jbpm_sector_bi desde jbpmdb_prod_old
-- ==============================================================================
TRUNCATE TABLE stg.jbpm_sector_bi;
INSERT INTO stg.jbpm_sector_bi (
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
        estrategico
    )
SELECT *
FROM dblink(
        'dbname=jbpmdb_prod_old port=5432 host=172.16.0.226 user=postgres password=postgres',
        'SELECT "CÓDIGO PROYECTO", "NOMBRE PROYECTO", "RESUMEN PROYECTO", "DIRECCIÓN PROYECTO",
            "FECHA REGISTRO", "CÓDIGO ACTIVIDAD", "ACTIVIDAD ECONÓMICA",
            "CED/RUC PROPONENTE", "NOMBRE PROPONENTE", "ÁREA RESPONSABLE PROYECTO",
            "TIPO SECTOR", "TIPO PERMISO AMBIENTAL", "TIPO ENTE",
            "PROVINCIA", "CANTON", "PARROQUIA",
            "PROCESO", "ESTADO PROCESO", "FECHA INICIO PROCESO"::timestamp, "FECHA FIN PROCESO"::timestamp,
            "TAREA", "ESTADO TAREA", "FECHA INICIO TAREA", "FECHA FIN TAREA",
            "USUARIO TAREA", "ESTADO PROYECTO", "INTERSECTA CON", "AREAS PROTEGIDAS"::text,
            "SISTEMA", "ENTE ACREDITADO", "ESTADO TRÁMITE", "ESTRATÉGICO"
     FROM public.vm_sector_subsector_bi'
    ) AS t(
        codigo_proyecto VARCHAR(255),
        nombre_proyecto TEXT,
        resumen_proyecto TEXT,
        direccion_proyecto TEXT,
        fecha_registro DATE,
        codigo_actividad VARCHAR(255),
        actividad_economica VARCHAR(255),
        ced_ruc_proponente VARCHAR(255),
        nombre_proponente TEXT,
        area_responsable_proyecto TEXT,
        tipo_sector VARCHAR(255),
        tipo_permiso_ambiental TEXT,
        tipo_ente TEXT,
        provincia TEXT,
        canton VARCHAR(255),
        parroquia VARCHAR(255),
        proceso TEXT,
        estado_proceso TEXT,
        fecha_inicio_proceso TIMESTAMP,
        fecha_fin_proceso TIMESTAMP,
        tarea VARCHAR(500),
        estado_tarea TEXT,
        fecha_inicio_tarea TIMESTAMP,
        fecha_fin_tarea TIMESTAMP,
        usuario_tarea VARCHAR(255),
        estado_proyecto VARCHAR(255),
        intersecta_con TEXT,
        areas_protegidas TEXT,
        sistema TEXT,
        ente_acreditado TEXT,
        estado_tramite TEXT,
        estrategico TEXT
    );
-- ==============================================================================
-- PASO 2: Cargar jbpm_4cat_bi desde jbpmdb
-- ==============================================================================
TRUNCATE TABLE stg.jbpm_4cat_bi;
INSERT INTO stg.jbpm_4cat_bi (
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
        estrategico
    )
SELECT *
FROM dblink(
        'dbname=jbpmdb port=5432 host=172.16.0.226 user=postgres password=postgres',
        'SELECT "CÓDIGO PROYECTO", "NOMBRE PROYECTO", "RESUMEN PROYECTO", "DIRECCIÓN PROYECTO",
            "FECHA REGISTRO", "CÓDIGO ACTIVIDAD", "ACTIVIDAD ECONÓMICA",
            "CED/RUC PROPONENTE", "NOMBRE PROPONENTE", "ÁREA RESPONSABLE PROYECTO",
            "TIPO SECTOR", "TIPO PERMISO AMBIENTAL", "TIPO ENTE",
            "PROVINCIA", "CANTON", "PARROQUIA",
            "PROCESO", "ESTADO PROCESO", "FECHA INICIO PROCESO", "FECHA FIN PROCESO",
            "TAREA", "ESTADO TAREA", "FECHA INICIO TAREA", "FECHA FIN TAREA",
            "USUARIO TAREA", "ESTADO PROYECTO", "INTERSECTA CON", "AREAS PROTEGIDAS",
            "SISTEMA", "ENTE ACREDITADO", "ESTADO TRÁMITE", "ESTRATÉGICO"
     FROM public.vm_cuatro_categorias_bi'
    ) AS t(
        codigo_proyecto VARCHAR(255),
        nombre_proyecto TEXT,
        resumen_proyecto TEXT,
        direccion_proyecto TEXT,
        fecha_registro DATE,
        codigo_actividad VARCHAR(255),
        actividad_economica VARCHAR(255),
        ced_ruc_proponente VARCHAR(255),
        nombre_proponente TEXT,
        area_responsable_proyecto TEXT,
        tipo_sector VARCHAR(255),
        tipo_permiso_ambiental VARCHAR(255),
        tipo_ente TEXT,
        provincia TEXT,
        canton VARCHAR(255),
        parroquia VARCHAR(255),
        proceso VARCHAR(255),
        estado_proceso TEXT,
        fecha_inicio_proceso TIMESTAMP,
        fecha_fin_proceso TIMESTAMP,
        tarea VARCHAR(500),
        estado_tarea TEXT,
        fecha_inicio_tarea TIMESTAMP,
        fecha_fin_tarea TIMESTAMP,
        usuario_tarea VARCHAR(255),
        estado_proyecto TEXT,
        intersecta_con TEXT,
        areas_protegidas TEXT,
        sistema TEXT,
        ente_acreditado TEXT,
        estado_tramite VARCHAR(255),
        estrategico VARCHAR(255)
    );
-- ==============================================================================
-- PASO 3: Re-consolidar staging
-- ==============================================================================
SELECT dw.sp_consolidar_staging();
-- ==============================================================================
-- PASO 4: Re-cargar dimensiones (incluira nuevos datos de sector e hidro)
-- ==============================================================================
SELECT dw.sp_carga_dimensiones();
-- ==============================================================================
-- PASO 5: Cargar Fact Table
-- ==============================================================================
SELECT dw.sp_carga_hechos();
-- ==============================================================================
-- PASO 6: VALIDACION FINAL
-- ==============================================================================
-- Conteos Staging
SELECT 'stg.suia_rcoa_bi' AS tabla,
    COUNT(1) AS registros
FROM stg.suia_rcoa_bi
UNION ALL
SELECT 'stg.suia_coa_bi',
    COUNT(1)
FROM stg.suia_coa_bi
UNION ALL
SELECT 'stg.jbpm_sector_bi',
    COUNT(1)
FROM stg.jbpm_sector_bi
UNION ALL
SELECT 'stg.jbpm_4cat_bi',
    COUNT(1)
FROM stg.jbpm_4cat_bi
UNION ALL
SELECT 'stg.jbpm_hidro_bi',
    COUNT(1)
FROM stg.jbpm_hidro_bi
UNION ALL
SELECT 'stg.jbpm_snap_variables',
    COUNT(1)
FROM stg.jbpm_snap_variables
UNION ALL
SELECT 'stg.consolidado_proyectos',
    COUNT(1)
FROM stg.consolidado_proyectos
ORDER BY 1;
-- Conteos Dimensiones
SELECT 'dw.dim_proyecto' AS tabla,
    COUNT(1) AS registros
FROM dw.dim_proyecto
UNION ALL
SELECT 'dw.dim_proponente',
    COUNT(1)
FROM dw.dim_proponente
UNION ALL
SELECT 'dw.dim_actividad',
    COUNT(1)
FROM dw.dim_actividad
UNION ALL
SELECT 'dw.dim_geografia',
    COUNT(1)
FROM dw.dim_geografia
UNION ALL
SELECT 'dw.dim_usuario',
    COUNT(1)
FROM dw.dim_usuario
UNION ALL
SELECT 'dw.dim_estado',
    COUNT(1)
FROM dw.dim_estado
UNION ALL
SELECT 'dw.dim_tiempo',
    COUNT(1)
FROM dw.dim_tiempo
ORDER BY 1;
-- Conteo Fact
SELECT 'dw.fact_regularizacion' AS tabla,
    COUNT(1) AS registros
FROM dw.fact_regularizacion;
-- Resumen SNAP
SELECT interseccion_snap,
    COUNT(1) AS total
FROM dw.fact_regularizacion
GROUP BY interseccion_snap
ORDER BY total DESC;
-- Resumen por Origen
SELECT origen,
    COUNT(1) AS total
FROM dw.fact_regularizacion
GROUP BY origen
ORDER BY total DESC;
-- Top 10 Provincias
SELECT dg.provincia,
    COUNT(1) AS total
FROM dw.fact_regularizacion f
    JOIN dw.dim_geografia dg ON dg.sk_geografia = f.sk_geografia
GROUP BY dg.provincia
ORDER BY total DESC
LIMIT 10;