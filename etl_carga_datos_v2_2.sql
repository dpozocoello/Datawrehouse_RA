-- ==============================================================================
-- SCRIPT ETL DE CARGA DE DATOS v2.2 (ACTUALIZADO CON CONTACTOS Y COORDENADAS)
-- Ejecutar después de aplicar enriquecimiento_dwh_contactos_coordenadas.sql
-- Y después de que el DBA haya modificado las vistas en el servidor 179
-- ==============================================================================
-- EJECUCION: psql -U postgres -d dw_reg_v1 -f etl_carga_datos_v2_2.sql
-- ==============================================================================

-- ==============================================================================
-- PASO 1: Cargar STG desde suia_enlisy -> coa_mae.tmp_rcoa_bi (CON CONTACTO+COORDS)
-- ==============================================================================
TRUNCATE TABLE stg.suia_rcoa_bi;
INSERT INTO stg.suia_rcoa_bi (
    codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
    fecha_registro, codigo_actividad, actividad_economica,
    ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
    tipo_sector, tipo_permiso_ambiental, tipo_ente,
    provincia, canton, parroquia,
    proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
    tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
    usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
    sistema, nombre_zona, finalizado_con_resolucion, numero_resolucion,
    fecha_resolucion, id_area, estado_tramite, superficie_proyecto,
    coordenada_x, coordenada_y, correo_electronico, telefono
)
SELECT *
FROM dblink(
    'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
    'SELECT "CÓDIGO PROYECTO", "NOMBRE PROYECTO", "RESUMEN PROYECTO", "DIRECCIÓN PROYECTO",
        "FECHA REGISTRO", "CÓDIGO ACTIVIDAD", "ACTIVIDAD ECONÓMICA",
        "CED/RUC PROPONENTE", "NOMBRE PROPONENTE", "ÁREA RESPONSABLE PROYECTO",
        "TIPO SECTOR", "TIPO PERMISO AMBIENTAL", "TIPO ENTE",
        "PROVINCIA", "CANTON", "PARROQUIA",
        "PROCESO", "ESTADO PROCESO", "FECHA INICIO PROCESO"::timestamp, "FECHA FIN PROCESO"::timestamp,
        "TAREA", "ESTADO TAREA", "FECHA INICIO TAREA", "FECHA FIN TAREA",
        "USUARIO TAREA", "ESTADO PROYECTO", "INTERSECTA CON", "AREAS PROTEGIDAS",
        "SISTEMA", "NOMBRE ZONA", "FINALIZADO CON RESOLUCION", "NUMERO RESOLUCION",
        "FECHA RESOLUCION", "ID AREA", "ESTADO TRÁMITE", "SUPERFICIE PROYECTO",
        "COORDENADA_X", "COORDENADA_Y", "CORREO_ELECTRONICO", "TELEFONO"
    FROM coa_mae.tmp_rcoa_bi'
) AS t(
    codigo_proyecto TEXT, nombre_proyecto TEXT, resumen_proyecto TEXT,
    direccion_proyecto TEXT, fecha_registro DATE, codigo_actividad TEXT,
    actividad_economica TEXT, ced_ruc_proponente TEXT, nombre_proponente TEXT,
    area_responsable_proyecto TEXT, tipo_sector TEXT, tipo_permiso_ambiental TEXT,
    tipo_ente TEXT, provincia TEXT, canton TEXT, parroquia TEXT,
    proceso TEXT, estado_proceso TEXT, fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP, tarea TEXT, estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP, fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT, estado_proyecto TEXT, intersecta_con TEXT,
    areas_protegidas TEXT, sistema TEXT, nombre_zona VARCHAR(500),
    finalizado_con_resolucion VARCHAR(500), numero_resolucion VARCHAR(500),
    fecha_resolucion TIMESTAMP, id_area INTEGER, estado_tramite TEXT,
    superficie_proyecto DOUBLE PRECISION,
    coordenada_x NUMERIC, coordenada_y NUMERIC,
    correo_electronico VARCHAR(255), telefono VARCHAR(50)
);

-- ==============================================================================
-- PASO 2: Cargar STG desde suia_enlisy -> suia_iii.tmp_coa_bi (CON CONTACTO+COORDS)
-- ==============================================================================
TRUNCATE TABLE stg.suia_coa_bi;
INSERT INTO stg.suia_coa_bi (
    codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
    fecha_registro, codigo_actividad, actividad_economica,
    ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
    tipo_sector, tipo_permiso_ambiental, tipo_ente,
    provincia, canton, parroquia,
    proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
    tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
    usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
    sistema, nombre_zona, finalizado_con_resolucion, numero_resolucion,
    fecha_resolucion, id_area, estado_tramite, superficie_proyecto,
    coordenada_x, coordenada_y, correo_electronico, telefono
)
SELECT *
FROM dblink(
    'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
    'SELECT "CÓDIGO PROYECTO", "NOMBRE PROYECTO", "RESUMEN PROYECTO", "DIRECCIÓN PROYECTO",
        "FECHA REGISTRO", "CÓDIGO ACTIVIDAD", "ACTIVIDAD ECONÓMICA",
        "CED/RUC PROPONENTE", "NOMBRE PROPONENTE", "ÁREA RESPONSABLE PROYECTO",
        "TIPO SECTOR", "TIPO PERMISO AMBIENTAL", "TIPO ENTE",
        "PROVINCIA", "CANTON", "PARROQUIA",
        "PROCESO", "ESTADO PROCESO", "FECHA INICIO PROCESO"::timestamp, "FECHA FIN PROCESO"::timestamp,
        "TAREA", "ESTADO TAREA", "FECHA INICIO TAREA", "FECHA FIN TAREA",
        "USUARIO TAREA", "ESTADO PROYECTO", "INTERSECTA CON", "AREAS PROTEGIDAS",
        "SISTEMA", "NOMBRE ZONA", "FINALIZADO CON RESOLUCION", "NUMERO RESOLUCION",
        "FECHA RESOLUCION", "ID AREA", "ESTADO TRÁMITE", "SUPERFICIE PROYECTO",
        "COORDENADA_X", "COORDENADA_Y", "CORREO_ELECTRONICO", "TELEFONO"
    FROM suia_iii.tmp_coa_bi'
) AS t(
    codigo_proyecto TEXT, nombre_proyecto TEXT, resumen_proyecto TEXT,
    direccion_proyecto TEXT, fecha_registro DATE, codigo_actividad TEXT,
    actividad_economica TEXT, ced_ruc_proponente TEXT, nombre_proponente TEXT,
    area_responsable_proyecto TEXT, tipo_sector TEXT, tipo_permiso_ambiental TEXT,
    tipo_ente TEXT, provincia TEXT, canton TEXT, parroquia TEXT,
    proceso TEXT, estado_proceso TEXT, fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP, tarea TEXT, estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP, fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT, estado_proyecto TEXT, intersecta_con TEXT,
    areas_protegidas TEXT, sistema TEXT, nombre_zona VARCHAR(500),
    finalizado_con_resolucion VARCHAR(500), numero_resolucion VARCHAR(500),
    fecha_resolucion TIMESTAMP, id_area INTEGER, estado_tramite TEXT,
    superficie_proyecto DOUBLE PRECISION,
    coordenada_x NUMERIC, coordenada_y NUMERIC,
    correo_electronico VARCHAR(255), telefono VARCHAR(50)
);

-- ==============================================================================
-- PASO 3: Cargar STG desde jbpmdb_prod_old -> vm_sector_subsector_bi (CON NUEVOS CAMPOS)
-- ==============================================================================
TRUNCATE TABLE stg.jbpm_sector_bi;
INSERT INTO stg.jbpm_sector_bi (
    codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
    fecha_registro, codigo_actividad, actividad_economica,
    ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
    tipo_sector, tipo_permiso_ambiental, tipo_ente,
    provincia, canton, parroquia,
    proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
    tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
    usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
    sistema, ente_acreditado, estado_tramite, estrategico,
    coordenada_x, coordenada_y, correo_electronico, telefono
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
        "SISTEMA", "ENTE ACREDITADO", "ESTADO TRÁMITE", "ESTRATÉGICO",
        "COORDENADA_X", "COORDENADA_Y", "CORREO_ELECTRONICO", "TELEFONO"
    FROM public.vm_sector_subsector_bi'
) AS t(
    codigo_proyecto TEXT, nombre_proyecto TEXT, resumen_proyecto TEXT,
    direccion_proyecto TEXT, fecha_registro DATE, codigo_actividad TEXT,
    actividad_economica TEXT, ced_ruc_proponente TEXT, nombre_proponente TEXT,
    area_responsable_proyecto TEXT, tipo_sector TEXT, tipo_permiso_ambiental TEXT,
    tipo_ente TEXT, provincia TEXT, canton TEXT, parroquia TEXT,
    proceso TEXT, estado_proceso TEXT, fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP, tarea VARCHAR(500), estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP, fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT, estado_proyecto TEXT, intersecta_con TEXT,
    areas_protegidas TEXT, sistema TEXT, ente_acreditado TEXT,
    estado_tramite TEXT, estrategico TEXT,
    coordenada_x NUMERIC, coordenada_y NUMERIC,
    correo_electronico VARCHAR(255), telefono VARCHAR(50)
);

-- ==============================================================================
-- PASO 4: Cargar STG desde jbpmdb -> vm_cuatro_categorias_bi (CON NUEVOS CAMPOS)
-- ==============================================================================
TRUNCATE TABLE stg.jbpm_4cat_bi;
INSERT INTO stg.jbpm_4cat_bi (
    codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
    fecha_registro, codigo_actividad, actividad_economica,
    ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
    tipo_sector, tipo_permiso_ambiental, tipo_ente,
    provincia, canton, parroquia,
    proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
    tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
    usuario_tarea, estado_proyecto, intersecta_con, areas_protegidas,
    sistema, ente_acreditado, estado_tramite, estrategico,
    coordenada_x, coordenada_y, correo_electronico, telefono
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
        "SISTEMA", "ENTE ACREDITADO", "ESTADO TRÁMITE", "ESTRATÉGICO",
        "COORDENADA_X", "COORDENADA_Y", "CORREO_ELECTRONICO", "TELEFONO"
    FROM public.vm_cuatro_categorias_bi'
) AS t(
    codigo_proyecto TEXT, nombre_proyecto TEXT, resumen_proyecto TEXT,
    direccion_proyecto TEXT, fecha_registro DATE, codigo_actividad TEXT,
    actividad_economica TEXT, ced_ruc_proponente TEXT, nombre_proponente TEXT,
    area_responsable_proyecto TEXT, tipo_sector TEXT, tipo_permiso_ambiental TEXT,
    tipo_ente TEXT, provincia TEXT, canton TEXT, parroquia TEXT,
    proceso TEXT, estado_proceso TEXT, fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP, tarea VARCHAR(500), estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP, fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT, estado_proyecto TEXT, intersecta_con TEXT,
    areas_protegidas TEXT, sistema TEXT, ente_acreditado TEXT,
    estado_tramite TEXT, estrategico TEXT,
    coordenada_x NUMERIC, coordenada_y NUMERIC,
    correo_electronico VARCHAR(255), telefono VARCHAR(50)
);

-- ==============================================================================
-- PASO 5: Cargar STG desde jbpmdb -> vwt_hidrocarbonos_bi (CON NUEVOS CAMPOS)
-- ==============================================================================
TRUNCATE TABLE stg.jbpm_hidro_bi;
INSERT INTO stg.jbpm_hidro_bi (
    codigo_proyecto, nombre_proyecto, resumen_proyecto, direccion_proyecto,
    fecha_registro, codigo_actividad, actividad_economica,
    ced_ruc_proponente, nombre_proponente, area_responsable_proyecto,
    tipo_sector, tipo_permiso_ambiental, tipo_ente,
    provincia, canton, parroquia,
    proceso, estado_proceso, fecha_inicio_proceso, fecha_fin_proceso,
    tarea, estado_tarea, fecha_inicio_tarea, fecha_fin_tarea,
    usuario_tarea, estado_proyecto, intersecta_con,
    id_area, ente_acreditado, estado_tramite,
    coordenada_x, coordenada_y, correo_electronico, telefono
)
SELECT *
FROM dblink(
    'dbname=jbpmdb port=5432 host=172.16.0.226 user=postgres password=postgres',
    'SELECT "CÓDIGO PROYECTO", "NOMBRE PROYECTO", "RESUMEN" AS "RESUMEN PROYECTO",
        "DIRECCIÓN PROYECTO", "FECHA REGISTRO",
        "CÓDIGO ACTIVIDAD", "ACTIVIDAD ECONÓMICA",
        "CED/RUC EMPRESA", "NOMBRE EMPRESA",
        "ÁREA RESPONSABLE PROYECTO", "TIPO SECTOR",
        ''Licencia Ambiental'' AS "TIPO PERMISO AMBIENTAL",
        "TIPO ENTE",
        "PROVINCIA", "CANTÓN", "PARROQUIA",
        "PROCESO", "ESTADO PROCESO", "FECHA INICIO PROCESO", "FECHA FIN PROCESO",
        "TAREA", "ESTADO TAREA", "FECHA INICIO TAREA", "FECHA FIN TAREA",
        "USUARIO TAREA", "ESTADO PROYECTO", "INTERSECTA CON",
        "ID AREA", "ENTE ACREDITADO", "ESTADO TRÁMITE",
        "COORDENADA_X", "COORDENADA_Y", "CORREO_ELECTRONICO", "TELEFONO"
    FROM public.vwt_hidrocarbonos_bi'
) AS t(
    codigo_proyecto TEXT, nombre_proyecto TEXT, resumen_proyecto TEXT,
    direccion_proyecto TEXT, fecha_registro DATE, codigo_actividad TEXT,
    actividad_economica TEXT, ced_ruc_proponente TEXT,
    nombre_proponente VARCHAR(500), area_responsable_proyecto TEXT,
    tipo_sector TEXT, tipo_permiso_ambiental TEXT, tipo_ente TEXT,
    provincia TEXT, canton TEXT, parroquia TEXT,
    proceso TEXT, estado_proceso TEXT, fecha_inicio_proceso TIMESTAMP,
    fecha_fin_proceso TIMESTAMP, tarea VARCHAR(500), estado_tarea TEXT,
    fecha_inicio_tarea TIMESTAMP, fecha_fin_tarea TIMESTAMP,
    usuario_tarea TEXT, estado_proyecto TEXT, intersecta_con TEXT,
    id_area INTEGER, ente_acreditado TEXT, estado_tramite TEXT,
    coordenada_x NUMERIC, coordenada_y NUMERIC,
    correo_electronico VARCHAR(255), telefono VARCHAR(50)
);

-- ==============================================================================
-- PASO 6: Variables SNAP (sin cambios)
-- ==============================================================================
TRUNCATE TABLE stg.jbpm_snap_variables;
INSERT INTO stg.jbpm_snap_variables (
    codigo_proyecto, processinstanceid, nombre_proceso,
    estado_proceso, fecha_inicio_proceso, fecha_fin_proceso
)
SELECT *
FROM dblink(
    'dbname=suia_bpms_enlisy_app port=5632 host=172.16.0.179 user=postgres password=postgres',
    'SELECT DISTINCT v.value AS codigo_proyecto,
        p.processinstanceid,
        p.processname AS nombre_proceso,
        p.status AS estado_proceso,
        p.start_date AS fecha_inicio_proceso,
        p.end_date AS fecha_fin_proceso
    FROM variableinstancelog v
        LEFT JOIN processinstancelog p ON p.processinstanceid = v.processinstanceid
    WHERE v.variableid IN (''tramite'', ''numero_tramite'')
        AND p.status IN (1, 2)
        AND EXISTS (
            SELECT 1 FROM variableinstancelog snap
            WHERE snap.processinstanceid = p.processinstanceid
                AND snap.variableid ILIKE ''%snap%''
        )'
) AS t(
    codigo_proyecto TEXT, processinstanceid BIGINT,
    nombre_proceso TEXT, estado_proceso INTEGER,
    fecha_inicio_proceso TIMESTAMP, fecha_fin_proceso TIMESTAMP
);

-- ==============================================================================
-- PASO 7: Consolidar todos los STG (v2.2)
-- ==============================================================================
SELECT dw.sp_consolidar_staging();

-- ==============================================================================
-- PASO 8: Cargar Dimensiones (v2.2 con contacto+coordenadas)
-- ==============================================================================
SELECT dw.sp_carga_dimensiones();

-- ==============================================================================
-- PASO 9: Cargar Tabla de Hechos
-- ==============================================================================
SELECT dw.sp_carga_hechos();

-- ==============================================================================
-- PASO 10: VALIDACION DE RESULTADOS
-- ==============================================================================
SELECT 'stg.suia_rcoa_bi' AS tabla, COUNT(1) AS registros FROM stg.suia_rcoa_bi
UNION ALL SELECT 'stg.suia_coa_bi', COUNT(1) FROM stg.suia_coa_bi
UNION ALL SELECT 'stg.jbpm_sector_bi', COUNT(1) FROM stg.jbpm_sector_bi
UNION ALL SELECT 'stg.jbpm_4cat_bi', COUNT(1) FROM stg.jbpm_4cat_bi
UNION ALL SELECT 'stg.jbpm_hidro_bi', COUNT(1) FROM stg.jbpm_hidro_bi
UNION ALL SELECT 'stg.consolidado_proyectos', COUNT(1) FROM stg.consolidado_proyectos;

-- Validar campos nuevos
SELECT 'Proyectos con coordenadas' AS metrica,
    COUNT(*) FILTER (WHERE coordenada_x IS NOT NULL) AS con_dato,
    COUNT(*) AS total
FROM stg.consolidado_proyectos;

SELECT 'Proponentes con correo' AS metrica,
    COUNT(*) FILTER (WHERE correo_electronico IS NOT NULL AND correo_electronico != '') AS con_dato,
    COUNT(*) AS total
FROM stg.consolidado_proyectos;
