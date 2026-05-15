-- ==============================================================================
-- SCRIPT DE ACTUALIZACION INCREMENTAL - CORRECCION DE LONGITUDES
-- Este script altera solo las columnas necesarias sin recrear las tablas.
-- ==============================================================================

-- 1. STAGING: stg.jbpm_sector_bi (PASO 3 - El del error actual)
ALTER TABLE stg.jbpm_sector_bi ALTER COLUMN codigo_actividad TYPE TEXT;
ALTER TABLE stg.jbpm_sector_bi ALTER COLUMN actividad_economica TYPE TEXT;
ALTER TABLE stg.jbpm_sector_bi ALTER COLUMN canton TYPE TEXT;
ALTER TABLE stg.jbpm_sector_bi ALTER COLUMN parroquia TYPE TEXT;
ALTER TABLE stg.jbpm_sector_bi ALTER COLUMN usuario_tarea TYPE TEXT;
ALTER TABLE stg.jbpm_sector_bi ALTER COLUMN estado_proyecto TYPE TEXT;

-- 2. STAGING: stg.jbpm_4cat_bi (PASO 4 - Preventivo)
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN direccion_proyecto TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN codigo_actividad TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN actividad_economica TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN tipo_permiso_ambiental TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN canton TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN parroquia TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN proceso TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN usuario_tarea TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN estado_tramite TYPE TEXT;
ALTER TABLE stg.jbpm_4cat_bi ALTER COLUMN estrategico TYPE TEXT;

-- 3. STAGING: stg.jbpm_hidro_bi (PASO 5 - Preventivo)
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN direccion_proyecto TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN codigo_actividad TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN actividad_economica TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN area_responsable_proyecto TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN tipo_permiso_ambiental TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN tipo_ente TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN provincia TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN canton TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN parroquia TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN proceso TYPE TEXT;
ALTER TABLE stg.jbpm_hidro_bi ALTER COLUMN estado_tramite TYPE TEXT;

-- 4. STAGING: stg.suia_rcoa_bi y stg.suia_coa_bi (PASO 1 y 2 - Preventivo)
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN ced_ruc_proponente TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN nombre_proponente TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN area_responsable_proyecto TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN tipo_sector TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN tipo_permiso_ambiental TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN tipo_ente TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN provincia TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN canton TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN parroquia TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN proceso TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN estado_proceso TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN tarea TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN estado_tarea TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN usuario_tarea TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN estado_proyecto TYPE TEXT;
ALTER TABLE stg.suia_rcoa_bi ALTER COLUMN estado_tramite TYPE TEXT;

ALTER TABLE stg.suia_coa_bi ALTER COLUMN ced_ruc_proponente TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN nombre_proponente TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN area_responsable_proyecto TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN tipo_sector TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN tipo_permiso_ambiental TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN tipo_ente TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN provincia TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN canton TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN parroquia TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN proceso TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN estado_proceso TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN tarea TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN estado_tarea TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN usuario_tarea TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN estado_proyecto TYPE TEXT;
ALTER TABLE stg.suia_coa_bi ALTER COLUMN estado_tramite TYPE TEXT;

-- 5. STAGING: stg.consolidado_proyectos
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN codigo_proyecto TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN ced_ruc_proponente TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN tipo_sector TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN tipo_permiso_ambiental TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN provincia TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN canton TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN parroquia TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN usuario_tarea TYPE TEXT;
ALTER TABLE stg.consolidado_proyectos ALTER COLUMN sistema TYPE TEXT;

-- 6. DIMENSIONES
ALTER TABLE dw.dim_usuario ALTER COLUMN usuario_tarea TYPE TEXT;

-- Confirmacion
DO $$ BEGIN RAISE NOTICE 'Actualizacion de longitudes completada exitosamente.'; END $$;
