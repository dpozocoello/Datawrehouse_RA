----SQL-01 — Verificar que el proyecto existe
-- Confirmar existencia y estado del proyecto antes de cualquier consulta
SELECT
    a.pren_id,
    a.pren_code          AS "CÓDIGO PROYECTO",
    a.pren_name          AS "NOMBRE PROYECTO",
    a.pren_status        AS "ACTIVO",
    a.pren_project_finalized AS "FINALIZADO",
    a.pren_register_date AS "FECHA REGISTRO",
    a.pren_area          AS "SUPERFICIE HA"
FROM suia_iii.projects_environmental_licensing a
WHERE a.pren_code = 'MAAE-RA-2020-368524';  -- ← reemplazar código

--SQL-02 — Todas las intersecciones activas del proyecto (campo «INTERSECTA CON»)
Reproduce exactamente lo que calcula el LEFT JOIN LATERAL ic en la función:
-- Equivale al LEFT JOIN LATERAL ic de la función
-- Retorna las capas con las que el proyecto tiene intersección activa
SELECT
    ip2.inpr_id,
    ip2.pren_id,
    ip2.inpr_layer_description   AS "CAPA",
    ip2.inpr_status              AS "ACTIVO",
    ip2.laye_id                  AS "ID CAPA",
    ip2.inpr_buffer_intersection AS "ES BUFFER"
FROM suia_iii.intersections_project ip2
JOIN suia_iii.projects_environmental_licensing a
     ON a.pren_id = ip2.pren_id
WHERE a.pren_code = 'MAAE-RA-2023-123456'  -- ← reemplazar código
  AND ip2.inpr_status IS TRUE
ORDER BY ip2.inpr_layer_description;

Para obtener el valor concatenado exacto como lo almacena la función:
-- Valor exacto del campo INTERSECTA CON para un proyecto
SELECT
    a.pren_code,
    STRING_AGG(
        ip2.inpr_layer_description::text,
        '  '  -- separador 2 espacios
        ORDER BY ip2.inpr_layer_description
    ) AS "INTERSECTA CON"
FROM suia_iii.projects_environmental_licensing a
JOIN suia_iii.intersections_project ip2
     ON ip2.pren_id = a.pren_id
    AND ip2.inpr_status IS TRUE
WHERE a.pren_code = 'MAAE-RA-2023-123456'  -- ← reemplazar código
GROUP BY a.pren_code;

--SQL-03 — Áreas protegidas con detalle geométrico (campo «AREAS PROTEGIDAS»)
--Reproduce el JOIN ip + dip con los filtros de laye_id y buffer:
-- Detalle de áreas protegidas (capas 2, 3, 4, 11 / sin buffer)
SELECT
    a.pren_code                   AS "CÓDIGO PROYECTO",
    ip.laye_id                    AS "ID CAPA",
    ip.inpr_layer_description     AS "NOMBRE CAPA",
    ip.inpr_buffer_intersection   AS "ES BUFFER",
    dip.dein_geometry_name        AS "NOMBRE ÁREA GEOMÉTRICA",
    REGEXP_REPLACE(
        dip.dein_geometry_name,
        '[^a-zA-Z0-9 ]', '', 'g'
    )                             AS "NOMBRE ÁREA LIMPIO"
FROM suia_iii.projects_environmental_licensing a
JOIN suia_iii.intersections_project ip
     ON ip.pren_id = a.pren_id
    AND ip.laye_id IN (2, 3, 4, 11)          -- capas de áreas protegidas
    AND ip.inpr_buffer_intersection IS FALSE  -- sin buffer
JOIN suia_iii.details_intersection_project dip
     ON dip.inpr_id = ip.inpr_id
WHERE a.pren_code = 'MAAE-RA-2023-123456'   -- ← reemplazar código
ORDER BY ip.laye_id, dip.dein_geometry_name;

Para obtener el valor concatenado exacto como lo almacena la función:
-- Valor exacto del campo AREAS PROTEGIDAS para un proyecto
SELECT
    a.pren_code,
    STRING_AGG(
        CONCAT(
            ip.inpr_layer_description,
            ' | ',
            REGEXP_REPLACE(dip.dein_geometry_name, '[^a-zA-Z0-9 ]', '', 'g')
        ),
        ' ; '
        ORDER BY ip.laye_id
    ) AS "AREAS PROTEGIDAS"
FROM suia_iii.projects_environmental_licensing a
JOIN suia_iii.intersections_project ip
     ON ip.pren_id = a.pren_id
    AND ip.laye_id IN (2, 3, 4, 11)
    AND ip.inpr_buffer_intersection IS FALSE
JOIN suia_iii.details_intersection_project dip
     ON dip.inpr_id = ip.inpr_id
WHERE a.pren_code = 'MAAE-RA-2023-123456'  -- ← reemplazar código
GROUP BY a.pren_code;

--SQL-04 — Todas las capas disponibles (diagnóstico)
Útil para saber qué valores de laye_id existen y qué significan las capas 2, 3, 4 y 11:
-- Ver todas las capas SIG disponibles en el sistema
-- Permite identificar qué son las capas 2, 3, 4, 11
SELECT DISTINCT
    ip.laye_id,
    ip.inpr_layer_description,
    COUNT(*) AS total_proyectos_intersectan
FROM suia_iii.intersections_project ip
WHERE ip.inpr_status IS TRUE
GROUP BY ip.laye_id, ip.inpr_layer_description
ORDER BY ip.laye_id;

--SQL-05 — Consulta integral de intersecciones (ambos campos en una sola consulta)
Replica el resultado final que la función almacena en tmp_coa_bi para los campos de intersección:
-- Consulta integral: reproduce ambos campos de intersección
-- como los calcularía la función sp_coa_bi_v1_4_1()
SELECT
    a.pren_code                    AS "CÓDIGO PROYECTO",
    a.pren_name                    AS "NOMBRE PROYECTO",
    -- Campo 1: INTERSECTA CON (todas las capas activas)
    ic.intersecta_con              AS "INTERSECTA CON",
    -- Campo 2: AREAS PROTEGIDAS (capas 2,3,4,11 con detalle geométrico)
    ap.areas_protegidas            AS "AREAS PROTEGIDAS"
FROM suia_iii.projects_environmental_licensing a

-- INTERSECTA CON: todas las capas activas
LEFT JOIN LATERAL (
    SELECT STRING_AGG(
               ip2.inpr_layer_description::text,
               '  ' ORDER BY ip2.inpr_layer_description
           ) AS intersecta_con
    FROM suia_iii.intersections_project ip2
    WHERE ip2.pren_id = a.pren_id
      AND ip2.inpr_status IS TRUE
) ic ON TRUE

-- AREAS PROTEGIDAS: capas específicas con detalle geométrico
LEFT JOIN LATERAL (
    SELECT STRING_AGG(
               CONCAT(
                   ip.inpr_layer_description, ' | ',
                   REGEXP_REPLACE(dip.dein_geometry_name,'[^a-zA-Z0-9 ]','','g')
               ),
               ' ; ' ORDER BY ip.laye_id
           ) AS areas_protegidas
    FROM suia_iii.intersections_project ip
    JOIN suia_iii.details_intersection_project dip
         ON dip.inpr_id = ip.inpr_id
    WHERE ip.pren_id = a.pren_id
      AND ip.laye_id IN (2, 3, 4, 11)
      AND ip.inpr_buffer_intersection IS FALSE
) ap ON TRUE

WHERE a.pren_status IS TRUE
  AND a.pren_code = 'MAAE-RA-2023-123456';  -- ← reemplazar código

--SQL-06 — Verificar resultado en la tabla destino (post-ejecución)
Para verificar que la función cargó correctamente los datos de intersección:
-- Verificar datos cargados en tmp_coa_bi para un proyecto específico
SELECT
    t."CÓDIGO PROYECTO",
    t."NOMBRE PROYECTO",
    t."INTERSECTA CON",
    t."AREAS PROTEGIDAS",
    t."ESTADO TRÁMITE",
    t."FECHA_CARGA_DATOS"
FROM suia_iii.tmp_coa_bi t
WHERE t."CÓDIGO PROYECTO" = 'MAAE-RA-2023-123456'  -- ← reemplazar código
ORDER BY t."FECHA_CARGA_DATOS" DESC;

