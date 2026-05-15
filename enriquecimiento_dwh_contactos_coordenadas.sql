-- ==============================================================================
-- SCRIPT DE ENRIQUECIMIENTO DWH RA v2.2
-- Agrega: coordenada_x, coordenada_y, correo_electronico, telefono
-- Autor: Arquitecto de Datos DWH-RA
-- Fecha: 2026-05-13
-- ==============================================================================
-- IMPORTANTE: Ejecutar en la base de datos dw_reg_v1
-- psql -U postgres -d dw_reg_v1 -f enriquecimiento_dwh_contactos_coordenadas.sql
-- ==============================================================================

-- ==============================================================================
-- FASE 1: ALTER TABLE — TABLAS STAGING
-- ==============================================================================

-- 1.1 stg.suia_rcoa_bi
ALTER TABLE stg.suia_rcoa_bi
    ADD COLUMN IF NOT EXISTS coordenada_x NUMERIC,
    ADD COLUMN IF NOT EXISTS coordenada_y NUMERIC,
    ADD COLUMN IF NOT EXISTS correo_electronico VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);

-- 1.2 stg.suia_coa_bi
ALTER TABLE stg.suia_coa_bi
    ADD COLUMN IF NOT EXISTS coordenada_x NUMERIC,
    ADD COLUMN IF NOT EXISTS coordenada_y NUMERIC,
    ADD COLUMN IF NOT EXISTS correo_electronico VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);

-- 1.3 stg.jbpm_sector_bi
ALTER TABLE stg.jbpm_sector_bi
    ADD COLUMN IF NOT EXISTS coordenada_x NUMERIC,
    ADD COLUMN IF NOT EXISTS coordenada_y NUMERIC,
    ADD COLUMN IF NOT EXISTS correo_electronico VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);

-- 1.4 stg.jbpm_4cat_bi
ALTER TABLE stg.jbpm_4cat_bi
    ADD COLUMN IF NOT EXISTS coordenada_x NUMERIC,
    ADD COLUMN IF NOT EXISTS coordenada_y NUMERIC,
    ADD COLUMN IF NOT EXISTS correo_electronico VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);

-- 1.5 stg.jbpm_hidro_bi
ALTER TABLE stg.jbpm_hidro_bi
    ADD COLUMN IF NOT EXISTS coordenada_x NUMERIC,
    ADD COLUMN IF NOT EXISTS coordenada_y NUMERIC,
    ADD COLUMN IF NOT EXISTS correo_electronico VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);

-- 1.6 stg.consolidado_proyectos (tabla maestra de consolidación)
ALTER TABLE stg.consolidado_proyectos
    ADD COLUMN IF NOT EXISTS coordenada_x NUMERIC,
    ADD COLUMN IF NOT EXISTS coordenada_y NUMERIC,
    ADD COLUMN IF NOT EXISTS correo_electronico VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);

-- ==============================================================================
-- FASE 2: ALTER TABLE — TABLAS DIMENSIONALES (DW)
-- ==============================================================================

-- 2.1 dw.dim_proyecto — Añadir coordenadas
ALTER TABLE dw.dim_proyecto
    ADD COLUMN IF NOT EXISTS coordenada_x NUMERIC,
    ADD COLUMN IF NOT EXISTS coordenada_y NUMERIC;

-- 2.2 dw.dim_proponente — Añadir contacto
ALTER TABLE dw.dim_proponente
    ADD COLUMN IF NOT EXISTS correo_electronico VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);

-- ==============================================================================
-- FASE 3: ACTUALIZAR SP — dw.sp_consolidar_staging()
-- Incluye las 4 nuevas columnas en cada bloque INSERT del UNION ALL
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_consolidar_staging() RETURNS void AS $$
BEGIN
    TRUNCATE TABLE stg.consolidado_proyectos;

    -- RCOA
    INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, nombre_zona, finalizado_con_resolucion, numero_resolucion,
        fecha_resolucion, ente_acreditado, estado_tramite,
        id_area, superficie_proyecto, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    )
    SELECT
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, nombre_zona, finalizado_con_resolucion, numero_resolucion,
        fecha_resolucion, '', estado_tramite,
        id_area, superficie_proyecto, '', origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    FROM stg.suia_rcoa_bi;

    -- COA
    INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, nombre_zona, finalizado_con_resolucion, numero_resolucion,
        fecha_resolucion, ente_acreditado, estado_tramite,
        id_area, superficie_proyecto, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    )
    SELECT
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, nombre_zona, finalizado_con_resolucion, numero_resolucion,
        fecha_resolucion, '', estado_tramite,
        id_area, superficie_proyecto, '', origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    FROM stg.suia_coa_bi;

    -- JBPM SECTOR
    INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, ente_acreditado, estado_tramite, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    )
    SELECT
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, ente_acreditado, estado_tramite, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    FROM stg.jbpm_sector_bi;

    -- JBPM 4 CATEGORIAS
    INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, ente_acreditado, estado_tramite, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    )
    SELECT
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
        sistema, ente_acreditado, estado_tramite, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    FROM stg.jbpm_4cat_bi;

    -- JBPM HIDROCARBUROS
    INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con,
        ente_acreditado, estado_tramite, id_area, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    )
    SELECT
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        fecha_registro, codigo_actividad, actividad_economica,
        ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
        tipo_sector, tipo_permiso_ambiental, tipo_ente,
        provincia, canton, parroquia,
        proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
        tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
        usuario_tarea, estado_proyecto, intersecta_con,
        ente_acreditado, estado_tramite, id_area, estrategico, origen,
        coordenada_x, coordenada_y, correo_electronico, telefono
    FROM stg.jbpm_hidro_bi;

    RAISE NOTICE 'Consolidado STG completado (v2.2 con contacto+coordenadas): % filas',
        (SELECT COUNT(1) FROM stg.consolidado_proyectos);
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- FASE 4: ACTUALIZAR SP — dw.sp_carga_dimensiones()
-- Incluye coordenadas en dim_proyecto y contacto en dim_proponente
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_dimensiones() RETURNS void AS $$
BEGIN
    -- Dimension Tiempo (rango de 20 anios)
    INSERT INTO dw.dim_tiempo (fecha, anio, mes, dia, trimestre, nombre_mes, dia_semana)
    SELECT d::date,
        EXTRACT(YEAR FROM d), EXTRACT(MONTH FROM d), EXTRACT(DAY FROM d),
        EXTRACT(QUARTER FROM d), TO_CHAR(d, 'TMMonth'), TO_CHAR(d, 'TMDay')
    FROM generate_series('2005-01-01'::date, '2030-12-31'::date, '1 day'::interval) d
    ON CONFLICT (fecha) DO NOTHING;

    -- Dimension Proyecto (AHORA CON COORDENADAS)
    INSERT INTO dw.dim_proyecto (
        codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
        tipo_permiso_ambiental, tipo_sector, tipo_ente, sistema, estrategico,
        coordenada_x, coordenada_y
    )
    SELECT DISTINCT codigo_proyecto,
        MAX(nombre_proyecto), MAX(resumen_proyecto), MAX(direccion_proyecto),
        MAX(tipo_permiso_ambiental), MAX(tipo_sector), MAX(tipo_ente),
        MAX(sistema), MAX(estrategico),
        MAX(coordenada_x), MAX(coordenada_y)
    FROM stg.consolidado_proyectos
    WHERE codigo_proyecto IS NOT NULL
    GROUP BY codigo_proyecto
    ON CONFLICT (codigo_proyecto) DO UPDATE SET
        nombre_proyecto = EXCLUDED.nombre_proyecto,
        tipo_permiso_ambiental = EXCLUDED.tipo_permiso_ambiental,
        tipo_sector = EXCLUDED.tipo_sector,
        coordenada_x = COALESCE(EXCLUDED.coordenada_x, dw.dim_proyecto.coordenada_x),
        coordenada_y = COALESCE(EXCLUDED.coordenada_y, dw.dim_proyecto.coordenada_y);

    -- Proyectos recuperados de tablas de pagos (JBPM)
    INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto)
    SELECT DISTINCT project_id, 'Proyecto Recuperado (JBPM)'
    FROM stg.online_payments_bi
    WHERE project_id IS NOT NULL AND project_id != ''
    ON CONFLICT (codigo_proyecto) DO NOTHING;

    -- Proyectos recuperados de tablas de pagos (SUIA)
    INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto)
    SELECT DISTINCT codigo_proyecto, 'Proyecto Recuperado (SUIA)'
    FROM stg.financial_transaction_bi
    WHERE codigo_proyecto IS NOT NULL AND codigo_proyecto != ''
    ON CONFLICT (codigo_proyecto) DO NOTHING;

    -- Dimension Proponente (AHORA CON CORREO Y TELEFONO — SCD Type 1)
    INSERT INTO dw.dim_proponente (ced_ruc_proponente, nombre_proponente, correo_electronico, telefono)
    SELECT DISTINCT ced_ruc_proponente,
        MAX(nombre_proponente),
        MAX(correo_electronico),
        MAX(telefono)
    FROM stg.consolidado_proyectos
    WHERE ced_ruc_proponente IS NOT NULL
    GROUP BY ced_ruc_proponente
    ON CONFLICT (ced_ruc_proponente) DO UPDATE SET
        nombre_proponente = EXCLUDED.nombre_proponente,
        correo_electronico = COALESCE(EXCLUDED.correo_electronico, dw.dim_proponente.correo_electronico),
        telefono = COALESCE(EXCLUDED.telefono, dw.dim_proponente.telefono);

    -- Dimension Actividad
    INSERT INTO dw.dim_actividad (codigo_actividad, actividad_economica)
    SELECT DISTINCT codigo_actividad, MAX(actividad_economica)
    FROM stg.consolidado_proyectos
    WHERE codigo_actividad IS NOT NULL
    GROUP BY codigo_actividad
    ON CONFLICT (codigo_actividad) DO UPDATE SET
        actividad_economica = EXCLUDED.actividad_economica;

    -- Dimension Geografia
    INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
    SELECT DISTINCT COALESCE(provincia, 'N/A'), COALESCE(canton, 'N/A'), COALESCE(parroquia, 'N/A')
    FROM stg.consolidado_proyectos
    ON CONFLICT (provincia, canton, parroquia) DO NOTHING;

    -- Asegurar registro de Cuenca Matriz
    INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
    VALUES ('AZUAY', 'CUENCA', 'CUENCA')
    ON CONFLICT (provincia, canton, parroquia) DO NOTHING;

    -- Dimension Usuario
    INSERT INTO dw.dim_usuario (usuario_tarea)
    SELECT DISTINCT usuario_tarea
    FROM stg.consolidado_proyectos
    WHERE usuario_tarea IS NOT NULL
    ON CONFLICT (usuario_tarea) DO NOTHING;

    -- Dimension Estado
    INSERT INTO dw.dim_estado (estado_proceso, estado_proyecto, estado_tramite)
    SELECT DISTINCT COALESCE(estado_proceso, 'N/A'),
        COALESCE(estado_proyecto, 'N/A'),
        COALESCE(estado_tramite, 'N/A')
    FROM stg.consolidado_proyectos
    ON CONFLICT (estado_proceso, estado_proyecto, estado_tramite) DO NOTHING;

    RAISE NOTICE 'Dimensiones cargadas exitosamente (v2.2 con contacto+coordenadas)';
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- FASE 5: VALIDACIÓN POST-DESPLIEGUE
-- ==============================================================================
-- Verificar que las columnas existen en staging
SELECT 'stg.suia_rcoa_bi' AS tabla, column_name
FROM information_schema.columns
WHERE table_schema = 'stg' AND table_name = 'suia_rcoa_bi'
AND column_name IN ('coordenada_x', 'coordenada_y', 'correo_electronico', 'telefono');

-- Verificar que las columnas existen en dimensiones
SELECT 'dw.dim_proyecto' AS tabla, column_name
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_proyecto'
AND column_name IN ('coordenada_x', 'coordenada_y');

SELECT 'dw.dim_proponente' AS tabla, column_name
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_proponente'
AND column_name IN ('correo_electronico', 'telefono');

-- ==============================================================================
-- FIN DEL SCRIPT DE ENRIQUECIMIENTO
-- ==============================================================================
