-- SQL para generar la Matriz de Regularización Ambiental (Todos los Estados) con Intersección SNAP
-- Filtrado para los últimos 2 años
-- Este script realiza un JOIN entre el BI Dashboard local y la base de datos remota usando dblink.
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
    main."ÁREA RESPONSABLE PROYECTO" AS "ÁREA RESPONSABLE PROYECTO",
    -- Determinamos si el proyecto interseca con SNAP
    CASE
        WHEN snap.project_code IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS "Intersección SNAP",
    main."FECHA REGISTRO" AS "Fecha Registro"
FROM bi_dashboard.vm_unificado_sistemas_bi main
    LEFT JOIN dblink(
        'dbname=suia_bpms_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
        $$
        SELECT DISTINCT v_proj.value as project_code
        FROM variableinstancelog v_snap
            JOIN variableinstancelog v_proj ON v_snap.processinstanceid = v_proj.processinstanceid
        WHERE v_snap.variableid ILIKE '%SNAP%'
            AND v_proj.variableid IN ('tramite', 'numero_tramite') $$
    ) AS snap(project_code text) ON main."CÓDIGO PROYECTO" = snap.project_code
WHERE main."FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '2 years';

-------------------------------

SELECT 
    main."CÓDIGO ACTIVIDAD" AS "Código CIIU",
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
    main."ÁREA RESPONSABLE PROYECTO" AS "ÁREA RESPONSABLE PROYECTO",
    -- Determinamos si el proyecto interseca con SNAP
    CASE WHEN snap.project_code IS NOT NULL THEN TRUE ELSE FALSE END AS "Intersección SNAP",
    main."FECHA REGISTRO" AS "Fecha Registro"
FROM bi_dashboard.vm_unificado_sistemas_bi main
LEFT JOIN dblink(
    'dbname=suia_bpms_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
    $$
    SELECT DISTINCT v_proj.value as project_code
    FROM variableinstancelog v_snap
    JOIN variableinstancelog v_proj ON v_snap.processinstanceid = v_proj.processinstanceid
    WHERE v_snap.variableid ILIKE '%SNAP%'
        AND v_proj.variableid IN ('tramite', 'numero_tramite') $$
) AS snap(project_code text) ON main."CÓDIGO PROYECTO" = snap.project_code
WHERE main."FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '2 years';
