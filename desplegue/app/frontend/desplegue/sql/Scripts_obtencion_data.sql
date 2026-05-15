-- ==============================================================================
-- SCRIPT DE OBTENCIÓN DE DATOS - DASHBOARD DE REGULARIZACIÓN AMBIENTAL (v1)
-- ==============================================================================
-- Archivo generado para respaldar la consulta principal utilizada en
-- la aplicación dashboard_ra.py desplegada actualmente.

-- 1. CONSULTA PRINCIPAL UTILIZADA POR PANDAS (DASHBOARD)
-- Esta es la consulta exacta que ejecuta la función load_data() 
-- en la línea 28 de d:\DashboardRA\dashboard_ra.py
SELECT * FROM dw.v_dashboard_regularizacion;

-- ==============================================================================
-- 2. DDL DE RESPALDO (DEFINICIÓN DE LA VISTA)
-- A continuación se documenta el código fuente que conforma 
-- la vista v_dashboard_regularizacion en la base de datos PostgreSQL.
-- ==============================================================================

/*
CREATE OR REPLACE VIEW dw.v_dashboard_regularizacion AS
SELECT 
    f.id_fact,
    f.origen,
    -- Dimension: Proyecto
    p.codigo_proyecto,
    p.nombre_proyecto,
    p.tipo_permiso_ambiental,
    p.tipo_sector,
    p.tipo_ente,
    p.sistema,
    p.estrategico,
    -- Dimension: Proponente
    prop.ced_ruc_proponente,
    prop.nombre_proponente,
    -- Dimension: Actividad
    act.codigo_actividad,
    act.actividad_economica,
    -- Dimension: Geografia
    geo.provincia,
    geo.canton,
    geo.parroquia,
    -- Dimension: Usuario
    u.usuario_tarea,
    -- Dimension: Estado
    est.estado_proceso,
    est.estado_proyecto,
    est.estado_tramite,
    -- Dimension: Tiempo (Registro)
    t.fecha AS fecha_registro,
    t.anio AS anio_registro,
    t.nombre_mes AS mes_registro,
    t.trimestre AS trimestre_registro,
    -- Metricas de Hechos
    f.interseccion_snap,
    f.areas_protegidas,
    f.superficie_proyecto,
    f.id_area,
    -- Fechas y Tiempos
    f.fecha_inicio_proceso,
    f.fecha_fin_proceso,
    EXTRACT(EPOCH FROM (f.fecha_fin_proceso - f.fecha_inicio_proceso)) / 86400 AS duracion_proceso_dias,
    f.fecha_inicio_tarea,
    f.fecha_fin_tarea,
    EXTRACT(EPOCH FROM (f.fecha_fin_tarea - f.fecha_inicio_tarea)) / 3600 AS duracion_tarea_horas,
    -- Resolucion
    f.finalizado_con_resolucion,
    f.numero_resolucion,
    f.fecha_resolucion,
    CASE
        WHEN f.finalizado_con_resolucion IS NOT NULL AND f.finalizado_con_resolucion <> '' THEN 1
        ELSE 0
    END as es_resolucion
FROM dw.fact_regularizacion f
    LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    LEFT JOIN dw.dim_proponente prop ON f.sk_proponente = prop.sk_proponente
    LEFT JOIN dw.dim_actividad act ON f.sk_actividad = act.sk_actividad
    LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
    LEFT JOIN dw.dim_usuario u ON f.sk_usuario = u.sk_usuario
    LEFT JOIN dw.dim_estado est ON f.sk_estado = est.sk_estado
    LEFT JOIN dw.dim_tiempo t ON f.sk_fecha_registro = t.sk_tiempo;
*/
