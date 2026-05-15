-- ==============================================================================
-- SCRIPT DE MODIFICACIÓN DE VISTAS REMOTAS EN SERVIDOR 179
-- Para agregar: coordenada_x, coordenada_y, correo_electronico, telefono
-- ==============================================================================
-- IMPORTANTE: Este script debe ejecutarse en el servidor 172.16.0.179
-- en las bases de datos correspondientes (suia_enlisy, jbpmdb, jbpmdb_prod_old)
-- ==============================================================================

-- ==============================================================================
-- NOTAS PARA EL DBA:
-- ==============================================================================
-- Las vistas transaccionales (tmp_rcoa_bi, tmp_coa_bi, vm_sector_subsector_bi, etc.)
-- actualmente no exponen coordenadas, email ni teléfono.
--
-- Para habilitar estos campos, se requiere:
-- 1. Identificar las tablas de origen que contienen esta información
-- 2. Agregar los JOINs necesarios a las vistas existentes
-- 3. Verificar el impacto de rendimiento
--
-- A continuación se presentan las modificaciones sugeridas para cada vista.
-- ==============================================================================

-- ==============================================================================
-- 1. VISTA: coa_mae.tmp_rcoa_bi (Base: suia_enlisy)
-- ==============================================================================
-- Las coordenadas del proyecto normalmente provienen de la tabla de
-- ubicación geográfica del proyecto (projects.latitude, projects.longitude
-- o la tabla de geometrías del sistema SUIA).
--
-- El correo y teléfono del proponente provienen de la tabla de usuarios
-- (users.email, users.phone_number) o de la tabla de proponentes
-- (proponents.email, proponents.phone).
--
-- EJEMPLO DE MODIFICACIÓN (ajustar nombres de tabla según esquema real):
-- ==============================================================================

/*
-- Opción A: Si las coordenadas están directamente en la tabla de proyectos
ALTER VIEW coa_mae.tmp_rcoa_bi AS
SELECT
    -- ... columnas existentes ...
    p.latitude AS "COORDENADA_X",
    p.longitude AS "COORDENADA_Y",
    u.email AS "CORREO_ELECTRONICO",
    u.phone_number AS "TELEFONO"
FROM coa_mae.projects p
    LEFT JOIN coa_mae.users u ON u.user_id = p.proponent_user_id
    -- ... JOINs existentes ...
;

-- Opción B: Si las coordenadas están en una tabla de geometrías separada
ALTER VIEW coa_mae.tmp_rcoa_bi AS
SELECT
    -- ... columnas existentes ...
    ST_X(ST_Centroid(pg.geom)) AS "COORDENADA_X",
    ST_Y(ST_Centroid(pg.geom)) AS "COORDENADA_Y",
    prop.email AS "CORREO_ELECTRONICO",
    prop.phone AS "TELEFONO"
FROM coa_mae.projects p
    LEFT JOIN coa_mae.project_geometries pg ON pg.project_id = p.project_id
    LEFT JOIN coa_mae.proponents prop ON prop.identification = p.proponent_id
    -- ... JOINs existentes ...
;
*/

-- ==============================================================================
-- 2. VISTA: suia_iii.tmp_coa_bi (Base: suia_enlisy)
-- ==============================================================================
-- Misma lógica que la vista RCOA pero apuntando al esquema suia_iii
-- ==============================================================================

/*
ALTER VIEW suia_iii.tmp_coa_bi AS
SELECT
    -- ... columnas existentes ...
    p.latitude AS "COORDENADA_X",
    p.longitude AS "COORDENADA_Y",
    u.email AS "CORREO_ELECTRONICO",
    u.phone_number AS "TELEFONO"
FROM suia_iii.projects p
    LEFT JOIN suia_iii.users u ON u.user_id = p.proponent_user_id
    -- ... JOINs existentes ...
;
*/

-- ==============================================================================
-- 3. VISTA: public.vm_sector_subsector_bi (Base: jbpmdb_prod_old, Host: 226)
-- ==============================================================================
-- En las bases JBPM, las coordenadas y contactos pueden no existir.
-- En ese caso, se proyectan como NULL y se rellenan desde las vistas COA/RCOA
-- durante la consolidación en el DWH.
-- ==============================================================================

/*
-- Si no hay datos disponibles en JBPM, simplemente proyectar NULLs:
ALTER VIEW public.vm_sector_subsector_bi AS
SELECT
    -- ... columnas existentes ...
    NULL::numeric AS "COORDENADA_X",
    NULL::numeric AS "COORDENADA_Y",
    NULL::varchar AS "CORREO_ELECTRONICO",
    NULL::varchar AS "TELEFONO"
FROM -- ... tablas existentes ...
;
*/

-- ==============================================================================
-- 4. VISTA: public.vm_cuatro_categorias_bi (Base: jbpmdb, Host: 226)
-- ==============================================================================
-- Mismo tratamiento que vm_sector_subsector_bi
-- ==============================================================================

/*
ALTER VIEW public.vm_cuatro_categorias_bi AS
SELECT
    -- ... columnas existentes ...
    NULL::numeric AS "COORDENADA_X",
    NULL::numeric AS "COORDENADA_Y",
    NULL::varchar AS "CORREO_ELECTRONICO",
    NULL::varchar AS "TELEFONO"
FROM -- ... tablas existentes ...
;
*/

-- ==============================================================================
-- 5. VISTA: public.vwt_hidrocarbonos_bi (Base: jbpmdb, Host: 226)
-- ==============================================================================

/*
ALTER VIEW public.vwt_hidrocarbonos_bi AS
SELECT
    -- ... columnas existentes ...
    NULL::numeric AS "COORDENADA_X",
    NULL::numeric AS "COORDENADA_Y",
    NULL::varchar AS "CORREO_ELECTRONICO",
    NULL::varchar AS "TELEFONO"
FROM -- ... tablas existentes ...
;
*/

-- ==============================================================================
-- INSTRUCCIONES PARA EL DBA:
-- ==============================================================================
-- 1. Conectarse al servidor 172.16.0.179
-- 2. Identificar las tablas que contienen: email, telefono, lat, lon
-- 3. Descomente y ajuste los bloques ALTER VIEW anteriores
-- 4. Ejecutar las modificaciones
-- 5. Validar con: SELECT * FROM [vista] LIMIT 5;
-- 6. Una vez confirmado, re-ejecutar el ETL desde Pentaho
-- ==============================================================================
