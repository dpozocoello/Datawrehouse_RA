-- ==============================================================================
-- VISTA CONSOLIDADA PARA DASHBOARD - LOOKER STUDIO
-- ==============================================================================
CREATE OR REPLACE VIEW dw.v_dashboard_regularizacion AS
SELECT -- IDs y Metadatos
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
    -- Dimension: Area (v1.1)
    COALESCE(da.nombre_area, 'N/A') AS oficina_tecnica,
    COALESCE(da.zona, 'N/A') AS zona_administrativa,
    COALESCE(da.campus, 'N/A') AS sede_campus,
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
    EXTRACT(
        EPOCH
        FROM (f.fecha_fin_proceso - f.fecha_inicio_proceso)
    ) / 86400 AS duracion_proceso_dias,
    f.fecha_inicio_tarea,
    f.fecha_fin_tarea,
    EXTRACT(
        EPOCH
        FROM (f.fecha_fin_tarea - f.fecha_inicio_tarea)
    ) / 3600 AS duracion_tarea_horas,
    -- Resolucion
    f.finalizado_con_resolucion,
    f.numero_resolucion,
    f.fecha_resolucion,
    CASE
        WHEN f.finalizado_con_resolucion IS NOT NULL
        AND f.finalizado_con_resolucion <> '' THEN 1
        ELSE 0
    END as es_resolucion
FROM dw.fact_regularizacion f
    LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    LEFT JOIN dw.dim_proponente prop ON f.sk_proponente = prop.sk_proponente
    LEFT JOIN dw.dim_actividad act ON f.sk_actividad = act.sk_actividad
    LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
    LEFT JOIN dw.dim_usuario u ON f.sk_usuario = u.sk_usuario
    LEFT JOIN dw.dim_estado est ON f.sk_estado = est.sk_estado
    LEFT JOIN dw.dim_tiempo t ON f.sk_fecha_registro = t.sk_tiempo
    LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area;
-- ==============================================================================
-- OPTIMIZACION: VISTA MATERIALIZADA PARA DESEMPEÑO TOP
-- ==============================================================================
DROP MATERIALIZED VIEW IF EXISTS dw.mv_dashboard_regularizacion;
CREATE MATERIALIZED VIEW dw.mv_dashboard_regularizacion AS
SELECT *
FROM dw.v_dashboard_regularizacion;
-- Indices para filtros rapidos en Looker Studio
CREATE INDEX idx_mv_fecha_reg ON dw.mv_dashboard_regularizacion(fecha_registro);
CREATE INDEX idx_mv_provincia ON dw.mv_dashboard_regularizacion(provincia);
CREATE INDEX idx_mv_tipo_permiso ON dw.mv_dashboard_regularizacion(tipo_permiso_ambiental);
CREATE INDEX idx_mv_estado_proceso ON dw.mv_dashboard_regularizacion(estado_proceso);
CREATE INDEX idx_mv_oficina ON dw.mv_dashboard_regularizacion(oficina_tecnica);
CREATE INDEX idx_mv_zona_admin ON dw.mv_dashboard_regularizacion(zona_administrativa);
COMMENT ON MATERIALIZED VIEW dw.mv_dashboard_regularizacion IS 'Vista materializada optimizada para el dashboard de Looker Studio con dimension de Areas';
COMMENT ON VIEW dw.v_dashboard_regularizacion IS 'Vista consolidada para el tablero de control de Regularizacion Ambiental con dimension de Areas';