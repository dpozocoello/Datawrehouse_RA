/*
 * Query for Environmental Regularization Matrix
 * Based on materialized view: bi_dashboard.vm_unificado_sistemas_bi
 * 
 * Filters:
 * - Last 10 years based on FECHA REGISTRO
 * - Completed status (ESTADO PROCESO = 'Completado')
 * 
 * Columns:
 * - Código CIIU, Actividad Económica
 * - Nombre Proyecto
 * - Estado, Impacto Ambiental (Derived from type), Tipo Permiso
 * - Ubicación Geográfica (Provincia, Cantón, Parroquia)
 * - Intersección SNAP
 * - Fecha Registro
 */
SELECT "CÓDIGO ACTIVIDAD" AS "Código CIIU",
    "ACTIVIDAD ECONÓMICA" AS "Actividad Económica",
    "CÓDIGO PROYECTO" as "Código de Proyecto",
    "NOMBRE PROYECTO" AS "Nombre Proyecto",
    "ESTADO PROCESO" AS "Estado",
    CASE
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Licencia%' THEN 'Medio/Alto Impacto'
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Registro%' THEN 'Bajo Impacto'
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Certificado%' THEN 'No Requiere Permiso'
        ELSE 'Desconocido'
    END AS "Impacto Ambiental",
    "TIPO PERMISO AMBIENTAL" AS "Tipo Permiso",
    "PROVINCIA" || ' - ' || "CANTON" || ' - ' || "PARROQUIA" AS "Ubicación Geográfica",
    "INTERSECTA CON" AS "Intersección SNAP",
    "FECHA REGISTRO" AS "Fecha Registro"
FROM bi_dashboard.vm_unificado_sistemas_bi
WHERE "FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '10 years'
    AND "ESTADO PROCESO" = 'Completado'
ORDER BY "FECHA REGISTRO" ASC;



/*
 * Query for Environmental Regularization Matrix with SNAP Intersection
 * Based on materialized view: bi_dashboard.vm_unificado_sistemas_bi
 * Includes remote check via dblink for SNAP intersection.
 * 
 * Remote DB: suia_bpms_enlisy_app (172.16.0.179)
 * Logic: Projects with a completed process instance having a variable ILIKE '%snap%'.
 * 
 * Filters:
 * - Last 10 years based on FECHA REGISTRO
 * - Completed status (ESTADO PROCESO = 'Completado')
 * 
 * Columns:
 * - Código CIIU, Actividad Económica, Código Proyecto
 * - Nombre Proyecto, Estado
 * - Impacto Ambiental (Derived from type), Tipo Permiso
 * - Ubicación Geográfica
 * - Intersección SNAP (from remote DB)
 * - Fecha Registro
 */
WITH snap_intersections AS (
    SELECT *
    FROM dblink(
            'dbname=suia_bpms_enlisy_app port=5632 host=172.16.0.179 user=postgres password=postgres',
            'SELECT DISTINCT v.value
         FROM variableinstancelog v
         JOIN bamtasksummary b ON v.processinstanceid = b.processinstanceid
         WHERE v.variableid ILIKE ''%snap%''
         AND b.status = ''Completed'''
        ) AS remote_data(codigo_proyecto text)
)
SELECT main."CÓDIGO ACTIVIDAD" AS "Código CIIU",
    main."ACTIVIDAD ECONÓMICA" AS "Actividad Económica",
    main."CÓDIGO PROYECTO" AS "Código de Proyecto",
    main."NOMBRE PROYECTO" AS "Nombre Proyecto",
    main."ESTADO PROCESO" AS "Estado",
    CASE
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Licencia%' THEN 'Medio/Alto Impacto'
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Registro%' THEN 'Bajo Impacto'
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Certificado%' THEN 'No Requiere Permiso'
        ELSE 'Desconocido'
    END AS "Impacto Ambiental",
    main."TIPO PERMISO AMBIENTAL" AS "Tipo Permiso",
    main."PROVINCIA" || ' - ' || main."CANTON" || ' - ' || main."PARROQUIA" AS "Ubicación Geográfica",
    CASE
        WHEN snap.codigo_proyecto IS NOT NULL THEN 'SI'
        ELSE 'NO' -- Or fallback to main."INTERSECTA CON" if desired, but request implies this logic is primary.
    END AS "Intersección SNAP",
    main."FECHA REGISTRO" AS "Fecha Registro"
FROM bi_dashboard.vm_unificado_sistemas_bi main
    LEFT JOIN snap_intersections snap ON main."CÓDIGO PROYECTO" = snap.codigo_proyecto
WHERE main."FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '10 years'
    AND main."ESTADO PROCESO" = 'Completado'
ORDER BY main."FECHA REGISTRO" ASC;



/*
 * Query for Environmental Regularization Matrix with SNAP Intersection
 * Source View: bi_dashboard.vm_unificado_sistemas_bi
 * Remote DB (for SNAP intersection): suia_bpms_enlisy_app (172.16.0.179)
 * 
 * Logic:
 * - Projects filtered by 'Completado' status and last 10 years.
 * - 'Intersección SNAP' is determined by checking the existence of the project code in the remote BPM variable logs (variableid ILIKE '%snap%').
 */
WITH snap_intersections AS (
    SELECT *
    FROM dblink(
            'dbname=suia_bpms_enlisy_app port=5632 host=172.16.0.179 user=postgres password=postgres',
            'SELECT DISTINCT v.value
         FROM variableinstancelog v
         JOIN bamtasksummary b ON v.processinstanceid = b.processinstanceid
         WHERE v.variableid ILIKE ''%snap%''
         AND b.status = ''Completed'''
        ) AS remote_data(codigo_proyecto text)
)
SELECT main."CÓDIGO ACTIVIDAD" AS "Código CIIU",
    main."ACTIVIDAD ECONÓMICA" AS "Actividad Económica",
    main."CÓDIGO PROYECTO" AS "Código de Proyecto",
    main."NOMBRE PROYECTO" AS "Nombre Proyecto",
    main."ESTADO PROCESO" AS "Estado",
    CASE
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Licencia%' THEN 'Medio/Alto Impacto'
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Registro%' THEN 'Bajo Impacto'
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Certificado%' THEN 'No Requiere Permiso'
        ELSE 'Desconocido'
    END AS "Impacto Ambiental",
    main."TIPO PERMISO AMBIENTAL" AS "Tipo Permiso",
    main."PROVINCIA" || ' - ' || main."CANTON" || ' - ' || main."PARROQUIA" AS "Ubicación Geográfica",
    CASE
        WHEN snap.codigo_proyecto IS NOT NULL THEN 'SI'
        ELSE 'NO'
    END AS "Intersección SNAP",
    main."FECHA REGISTRO" AS "Fecha Registro"
FROM bi_dashboard.vm_unificado_sistemas_bi main
    LEFT JOIN snap_intersections snap ON main."CÓDIGO PROYECTO" = snap.codigo_proyecto
WHERE main."FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '10 years'
    AND main."ESTADO PROCESO" = 'Completado'
ORDER BY main."FECHA REGISTRO" ASC;


/*
 * Integrated BI Dashboard and SNAP Process Query
 * 
 * Source: bi_dashboard.vm_unificado_sistemas_bi (Local)
 * Remote: suia_bpms_enlisy_app (172.16.0.179) via dblink
 * 
 * Logic:
 * 1. Fetch detailed process/task info from remote BPM for projects with SNAP variables.
 * 2. Join with local BI dashboard data on Project Code.
 * 3. Filter by 'Completado' and last 10 years.
 */
WITH snap_details AS (
    SELECT *
    FROM dblink(
            'dbname=suia_bpms_enlisy_app port=5632 host=172.16.0.179 user=postgres password=postgres',
            $$
            SELECT v.value AS codigoProyecto,
                t.processinstanceid,
                p.processname AS nombreProceso,
                CASE
                    WHEN p.status = 1 THEN 'En trámite'
                    WHEN p.status = 2 THEN 'Completado'
                    WHEN p.status = 3 THEN 'Abortado'
                    WHEN p.status = 4 THEN 'Abortado'
                    ELSE 'Abortado'
                END AS estadoProceso,
                p.start_date AS fechaInicioProceso,
                p.end_date AS fechaFinProceso,
                t.taskname AS nombreTarea,
                CASE
                    WHEN p.status = 1 THEN ta.status
                    ELSE t.status
                END AS estadoTarea,
                CASE
                    WHEN p.status = 1 THEN ta.activationtime
                    ELSE t.createddate
                END AS fechaInicioTarea,
                CASE
                    WHEN p.status = 1 THEN NULL
                    ELSE t.enddate
                END AS fechaFinTarea,
                CASE
                    WHEN p.status = 1 THEN COALESCE(ta.actualowner_id, ta.createdby_id)
                    ELSE t.userid
                END AS usuarioTarea
            FROM variableinstancelog v
                LEFT JOIN processinstancelog p ON p.processinstanceid = v.processinstanceid
                LEFT JOIN bamtasksummary t ON t.processinstanceid = p.processinstanceid
                LEFT JOIN task ta ON p.processinstanceid = ta.processinstanceid
                AND ta.id = t.taskid
                LEFT JOIN (
                    SELECT DISTINCT ON (te.taskid) te.id,
                        te.taskid,
                        te.userid,
                        te.logtime
                    FROM taskevent te
                    WHERE te.type = 'COMPLETED'
                ) te ON te.taskid = t.taskid
            WHERE v.variableid IN ('tramite', 'numero_tramite')
                AND p.status IN (1, 2)
                AND EXISTS (
                    SELECT 1
                    FROM variableinstancelog snap
                    WHERE snap.processinstanceid = p.processinstanceid
                        AND snap.variableid ILIKE '%snap%'
                ) $$
        ) AS remote_data(
            codigoProyecto text,
            processinstanceid bigint,
            nombreProceso text,
            estadoProceso text,
            fechaInicioProceso timestamp,
            fechaFinProceso timestamp,
            nombreTarea text,
            estadoTarea text,
            fechaInicioTarea timestamp,
            fechaFinTarea timestamp,
            usuarioTarea text
        )
)
SELECT main."CÓDIGO ACTIVIDAD" AS "Código CIIU",
    main."ACTIVIDAD ECONÓMICA" AS "Actividad Económica",
    main."CÓDIGO PROYECTO" AS "Código de Proyecto",
    main."NOMBRE PROYECTO" AS "Nombre Proyecto",
    main."ESTADO PROCESO" AS "Estado",
    CASE
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Licencia%' THEN 'Medio/Alto Impacto'
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Registro%' THEN 'Bajo Impacto'
        WHEN main."TIPO PERMISO AMBIENTAL" ILIKE '%Certificado%' THEN 'No Requiere Permiso'
        ELSE 'Desconocido'
    END AS "Impacto Ambiental",
    main."TIPO PERMISO AMBIENTAL" AS "Tipo Permiso",
    main."PROVINCIA" || ' - ' || main."CANTON" || ' - ' || main."PARROQUIA" AS "Ubicación Geográfica",
    CASE
        WHEN snap.codigoProyecto IS NOT NULL THEN 'SI'
        ELSE 'NO'
    END AS "Intersección SNAP",
    main."FECHA REGISTRO" AS "Fecha Registro",
    -- Detailed SNAP Columns
    snap.nombreProceso AS "Nombre Proceso SNAP",
    snap.estadoProceso AS "Estado Proceso SNAP",
    snap.nombreTarea AS "Nombre Tarea SNAP",
    snap.estadoTarea AS "Estado Tarea SNAP",
    snap.fechaInicioTarea AS "Fecha Inicio Tarea SNAP",
    snap.fechaFinTarea AS "Fecha Fin Tarea SNAP",
    snap.usuarioTarea AS "Usuario Tarea SNAP"
FROM bi_dashboard.vm_unificado_sistemas_bi main
    LEFT JOIN snap_details snap ON main."CÓDIGO PROYECTO" = snap.codigoProyecto
WHERE main."FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '10 years'
    AND main."ESTADO PROCESO" = 'Completado'
ORDER BY main."FECHA REGISTRO" ASC;



/*
 * Query for Environmental Regularization Matrix
 * Based on materialized view: bi_dashboard.vm_unificado_sistemas_bi
 * 
 * Filters:
 * - Last 10 years based on FECHA REGISTRO
 * - Completed status (ESTADO PROCESO = 'Completado')
 * 
 * Columns:
 * - Código CIIU, Actividad Económica
 * - Nombre Proyecto
 * - Estado, Impacto Ambiental (Derived from type), Tipo Permiso
 * - Ubicación Geográfica (Provincia, Cantón, Parroquia)
 * - Intersección SNAP
 * - Fecha Registro
 */
SELECT "CÓDIGO ACTIVIDAD" AS "Código CIIU",
    "ACTIVIDAD ECONÓMICA" AS "Actividad Económica",
    "CÓDIGO PROYECTO" as "Código de Proyecto",
    "NOMBRE PROYECTO" AS "Nombre Proyecto",
    "ESTADO PROCESO" AS "Estado",
    CASE
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Licencia%' THEN 'Medio/Alto Impacto'
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Registro%' THEN 'Bajo Impacto'
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Certificado%' THEN 'No Requiere Permiso'
        ELSE 'Desconocido'
    END AS "Impacto Ambiental",
    "TIPO PERMISO AMBIENTAL" AS "Tipo Permiso",
    "PROVINCIA" || ' - ' || "CANTON" || ' - ' || "PARROQUIA" AS "Ubicación Geográfica",
    "INTERSECTA CON" AS "Intersección SNAP",
    "FECHA REGISTRO" AS "Fecha Registro"
FROM bi_dashboard.vm_unificado_sistemas_bi
WHERE "FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '10 years'
    AND "ESTADO PROCESO" = 'Completado'
ORDER BY "FECHA REGISTRO" ASC;
