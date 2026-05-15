-- DROP FUNCTION coa_mae.sp_rcoa_bi_v1_4_1(text);

CREATE OR REPLACE FUNCTION coa_mae.sp_rcoa_bi_v1_4_1(p_codigo_proyecto text DEFAULT NULL::text)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    TRUNCATE TABLE coa_mae.tmp_rcoa_bi;
    INSERT INTO coa_mae.tmp_rcoa_bi
    SELECT DISTINCT
        pp."CÓDIGO PROYECTO",
        pp."NOMBRE PROYECTO",
        pp."RESUMEN PROYECTO",
        pp."DIRECCIÓN PROYECTO",
        pp."FECHA REGISTRO",
        pp."CÓDIGO ACTIVIDAD",
        pp."ACTIVIDAD ECONÓMICA",
        pp."CED/RUC PROPONENTE",
        pp."NOMBRE PROPONENTE",
        pp."ÁREA RESPONSABLE PROYECTO",
        pp."TIPO SECTOR",
        pp."TIPO PERMISO AMBIENTAL",
        pp."TIPO ENTE",
        pp."PROVINCIA",
        pp."CANTON",
        pp."PARROQUIA",
        pp."PROCESO",
        pp."ESTADO PROCESO",
        pp."FECHA INICIO PROCESO",
        pp."FECHA FIN PROCESO",
        pp."TAREA",
        pp."ESTADO TAREA",
        pp."FECHA INICIO TAREA",
        pp."FECHA FIN TAREA",
        pp."USUARIO TAREA",
        pp."ESTADO PROYECTO",
        pp."INTERSECTA CON",
        pp."AREAS PROTEGIDAS",
        pp."SISTEMA",
        pp."NOMBRE ZONA",
        pp."FINALIZADO CON RESOLUCION",
        pp."NUMERO RESOLUCION",
        pp."FECHA RESOLUCION",
        pp."ID AREA",
        pp."ESTADO TRÁMITE",
        pp."SUPERFICIE PROYECTO",
        CURRENT_TIMESTAMP                                           AS "FECHA_CARGA_DATOS",
        pp."INTERSECTA"

    FROM (
        SELECT DISTINCT
            yy."CÓDIGO PROYECTO",
            yy."NOMBRE PROYECTO",
            yy."RESUMEN PROYECTO",
            yy."DIRECCIÓN PROYECTO",
            yy."FECHA REGISTRO",
            yy."TIPO SECTOR",
            yy."TIPO PERMISO AMBIENTAL",
            yy."ACTIVIDAD ECONÓMICA",
            yy."CÓDIGO ACTIVIDAD",
            yy."ÁREA RESPONSABLE PROYECTO",
            yy."TIPO ENTE",
            yy."PROVINCIA",
            yy."CANTON",
            yy."PARROQUIA",
            yy."PROCESO",
            yy."ESTADO PROCESO",
            yy."FECHA INICIO PROCESO",
            yy."FECHA FIN PROCESO",
            yy."FECHA ESTADO PROYECTO",
            yy."TAREA",
            yy."ESTADO TAREA",
            yy."FECHA INICIO TAREA",
            yy."FECHA FIN TAREA",
            yy."USUARIO TAREA",
            yy."CED/RUC PROPONENTE",
            yy."NOMBRE PROPONENTE",
            yy."ESTADO PROYECTO",
            yy."INTERSECTA CON",
            yy."AREAS PROTEGIDAS",
            'RCOA'::text                                            AS "SISTEMA",
            yy."NOMBRE ZONA",
            yy."FINALIZADO CON RESOLUCION",
            yy."NUMERO RESOLUCION",
            yy."FECHA RESOLUCION",
            yy."ID AREA",
            yy."SUPERFICIE PROYECTO",
            CASE
                WHEN yy."ESTADO PROYECTO" = 'Completado'
                                                                    THEN 'FINALIZADO EXITO'
                WHEN yy."ESTADO PROYECTO" = 'Completado No Favorable'
                                                                    THEN 'FINALIZADO NO FAVORABLE'
                WHEN (
                    yy."ESTADO PROYECTO" = 'En trámite'
                    AND yy."TIPO PERMISO AMBIENTAL" LIKE '%Licen%'
                    AND yy."FECHA REGISTRO" >= '2021-10-12'
                    AND yy."PROCESO" = 'Estudio Impacto Ambiental'
                    AND yy."ESTADO PROCESO" = 'Completado'
                )                                                   THEN 'PROCESO FISICO'
                WHEN (
                    yy."ESTADO PROYECTO" = 'En trámite'
                    AND yy."TIPO PERMISO AMBIENTAL" LIKE '%Regist%'
                    AND yy."FECHA REGISTRO" >= '2023-06-02'
                    AND yy."TIPO SECTOR" IN ('Minería', 'Hidrocarburos')
                    AND yy."PROCESO" IN ('Registro Ambiental')
                )                                                   THEN 'DIGITALIZACION'
                ELSE 'EN TRÁMITE'
            END                                                     AS "ESTADO TRÁMITE",
            yy."INTERSECTA"

        FROM (
            SELECT DISTINCT
                x."CÓDIGO PROYECTO",
                x."NOMBRE PROYECTO",
                x."RESUMEN PROYECTO",
                x."DIRECCIÓN PROYECTO",
                x."FECHA REGISTRO",
                x."TIPO SECTOR",
                x."TIPO PERMISO AMBIENTAL",
                x."ACTIVIDAD ECONÓMICA",
                x."CÓDIGO ACTIVIDAD",
                x."ÁREA RESPONSABLE PROYECTO",
                x."TIPO ENTE",
                x."PROVINCIA",
                x."CANTON",
                x."PARROQUIA",
                CASE
                    WHEN y.nombreproceso = 'Registro ambiental v2' THEN 'Registro Ambiental'
                    ELSE y.nombreproceso
                END                                                 AS "PROCESO",
                y.estadoproceso                                     AS "ESTADO PROCESO",
                y.fechainicioproceso::timestamp without time zone   AS "FECHA INICIO PROCESO",
                y.fechafinproceso::timestamp without time zone      AS "FECHA FIN PROCESO",
                CASE
                    WHEN y.estadoproceso = 'Completado'
                        THEN y.fechafinproceso::timestamp without time zone
                    WHEN y.estadoproceso = 'En trámite'
                        THEN x."FECHA REGISTRO"::timestamp without time zone
                    ELSE NULL::timestamp without time zone
                END                                                 AS "FECHA ESTADO PROYECTO",
                x."CED/RUC PROPONENTE",
                x."NOMBRE PROPONENTE",
                x.area_id,
                y.nombretarea                                       AS "TAREA",
                CASE
                    WHEN y.estadotarea LIKE 'Completed%'            THEN 'Completado'
                    WHEN y.estadotarea = ANY (ARRAY['Created','InProgress','Ready','Reserved'])
                                                                    THEN 'En trámite'
                    ELSE y.estadotarea
                END                                                 AS "ESTADO TAREA",
                y.fechainiciotarea::timestamp without time zone     AS "FECHA INICIO TAREA",
                y.fechafintarea::timestamp without time zone        AS "FECHA FIN TAREA",
                y.usuariotarea                                      AS "USUARIO TAREA",
                x."ESTADO PROYECTO",
                ic.intersecta_con                                   AS "INTERSECTA CON",
                x."AREAS PROTEGIDAS",
                x."NOMBRE ZONA",
                x."FINALIZADO CON RESOLUCION",
                x."NUMERO RESOLUCION",
                x."FECHA RESOLUCION",
                x."ID AREA",
                x."SUPERFICIE PROYECTO",
                x.prco_categorizacion,
                x.prco_waste_generation,
                x.prco_waste_management,
                x.prco_vegetable_verture,
                x.prco_chemical_substances,
                x.prco_chemical_substances_transport,
                x.prco_enviromental_impact,
                NULL::text                                          AS "INTERSECTA"

            FROM (
                SELECT
                    a.prco_id,
                    a.prco_cua::text                                AS "CÓDIGO PROYECTO",
                    a.prco_name::text                               AS "NOMBRE PROYECTO",
                    a.prco_description::text                        AS "RESUMEN PROYECTO",
                    a.prco_address::text                            AS "DIRECCIÓN PROYECTO",
                    a.prco_cua_date::date                           AS "FECHA REGISTRO",
                    coalesce(og.orga_name_organization,
                             c.peop_name)::text                     AS "NOMBRE PROPONENTE",
                    coalesce(og.orga_ruc,
                             c.peop_pin)::text                      AS "CED/RUC PROPONENTE",
                    ci.caci_name::text                              AS "ACTIVIDAD ECONÓMICA",
                    ci.caci_code::text                              AS "CÓDIGO ACTIVIDAD",
                    ct.sety_name::text                              AS "TIPO SECTOR",
                    ar.area_name::text                              AS "ÁREA RESPONSABLE PROYECTO",
                    at.arty_name::text                              AS "TIPO ENTE",
                    CASE
                        WHEN a.prco_categorizacion = 1              THEN 'Certificado Ambiental'
                        WHEN a.prco_categorizacion = 2              THEN 'Registro Ambiental'
                        WHEN a.prco_categorizacion = 3              THEN 'Licencia Ambiental'
                        WHEN a.prco_categorizacion = 4              THEN 'Licencia Ambiental'
                        ELSE NULL
                    END                                             AS "TIPO PERMISO AMBIENTAL",
                    gl3.gelo_name::text                             AS "PROVINCIA",
                    gl2.gelo_name::text                             AS "CANTON",
                    gl1.gelo_name::text                             AS "PARROQUIA",
                    ar.area_id,
                    CASE
                        WHEN a.prco_project_finished IS TRUE
                         AND (
                             a.prco_viability_favorable IS FALSE
                             OR (
                                 e.prin_final_result_eia_cata_id IS NOT NULL
                                 AND e.prin_final_result_eia_cata_id != 8
                             )
                         )                                          THEN 'Completado No Favorable'
                        WHEN a.prco_project_finished IS TRUE
                         AND a.prco_viability_favorable IS NOT FALSE THEN 'Completado'
                        ELSE 'En trámite'
                    END                                             AS "ESTADO PROYECTO",
                    CASE
                        WHEN rec.enre_number_resolution IS NOT NULL THEN 'Finalizado con Resolución'
                        WHEN reg.enre_number_resolution IS NOT NULL THEN 'Finalizado con Resolución'
                        WHEN cer.pece_code IS NOT NULL              THEN 'Finalizado con Resolución'
                        ELSE NULL
                    END                                             AS "FINALIZADO CON RESOLUCION",
                    coalesce(
                        coalesce(rec.enre_number_resolution,
                                 reg.enre_number_resolution),
                        cer.pece_code
                    )::text                                         AS "NUMERO RESOLUCION",
                    coalesce(
                        rec.enre_creation_date,
                        reg.enre_creation_date,
                        cer.pece_creation_date
                    )::timestamp without time zone                  AS "FECHA RESOLUCION",
                    ar.area_id                                      AS "ID AREA",
                    a.prco_surface::double precision                AS "SUPERFICIE PROYECTO",
                    CASE
                        WHEN z1.zone_public_name IS NULL THEN 'N/A'
                        ELSE z1.zone_public_name::text
                    END                                             AS "NOMBRE ZONA",
                    string_agg(
                        DISTINCT concat(
                            aa.inpr_layer_description::text, ' | ',
                            regexp_replace(
                                b_1.dein_geometry_name::text,
                                '[^a-zA-Z0-9 ]', '', 'g'
                            )
                        ),
                        ' ; '
                    )                                               AS "AREAS PROTEGIDAS",
                    a.prco_categorizacion,
                    a.prco_waste_generation,
                    a.prco_waste_management,
                    a.prco_vegetable_verture,
                    a.prco_chemical_substances,
                    a.prco_chemical_substances_transport,
                    a.prco_enviromental_impact

                FROM coa_mae.project_licencing_coa a
                    JOIN  users bb
                               ON bb.user_id = a.user_id
                    JOIN  people c
                               ON c.peop_id = bb.peop_id
                    LEFT  JOIN organizations og
                               ON og.orga_ruc::text = bb.user_name::text
                    JOIN  coa_mae.project_licencing_coa_location b
                               ON b.prco_id = a.prco_id
                              AND b.prlo_status IS TRUE
                    LEFT  JOIN coa_mae.project_licencing_coa_ciuu lc
                               ON lc.prco_id = b.prco_id
                              AND lc.prli_primary IS TRUE
                              AND lc.prli_status IS TRUE
                              AND b.prlo_primary IS TRUE
                    JOIN  coa_mae.catalog_ciuu ci
                               ON ci.caci_id = lc.caci_id
                    JOIN  geographical_locations gl1
                               ON b.gelo_id = gl1.gelo_id
                    JOIN  geographical_locations gl2
                               ON gl1.gelo_parent_id = gl2.gelo_id
                    JOIN  geographical_locations gl3
                               ON gl2.gelo_parent_id = gl3.gelo_id
                    JOIN  coa_mae.project_licencing_coa_ciuu pci
                               ON pci.prco_id = a.prco_id
                              AND pci.prli_primary IS TRUE
                              AND pci.prli_status IS TRUE
                    JOIN  coa_mae.catalog_ciuu ciu
                               ON ciu.caci_id = pci.caci_id
                    JOIN  suia_iii.sector_types ct
                               ON ct.sety_id = ci.sety_id
                    LEFT  JOIN areas ar
                               ON ar.area_id = a.area_id
                    LEFT  JOIN areas_types at
                               ON at.arty_id = ar.arty_id
                    LEFT  JOIN areas z
                               ON ar.area_parent_id = z.area_id
                    LEFT  JOIN zones z1
                               ON z1.zone_id = z.zone_id
                    LEFT  JOIN coa_mae.intersections_project_licencing_coa aa
                               ON aa.prco_id = a.prco_id
                              AND aa.laye_id IN (2,3,4,11)
                              AND aa.inpr_status IS TRUE
                    LEFT  JOIN coa_mae.details_intersection_project_licencing_coa b_1
                               ON aa.inpr_id = b_1.inpr_id
                              AND b_1.dein_status IS TRUE
                    LEFT  JOIN payments.unique_transaction_number utn
                               ON a.prco_cua = utn.nut_project_code
                    LEFT  JOIN coa_emission_environmental_resolution.environmental_resolution rec
                               ON a.prco_id = rec.prco_id
                              AND rec.enre_status IS TRUE
                    LEFT  JOIN coa_environmental_record.environmental_record reg
                               ON reg.prco_id = a.prco_id
                              AND reg.enre_status IS TRUE
                    LEFT  JOIN coa_environmental_certificate.project_environmental_certificate cer
                               ON cer.prco_id = a.prco_id
                              AND cer.pece_status IS TRUE
                    LEFT  JOIN coa_environmental_impact_study.project_information e
                               ON e.prco_id = a.prco_id
                              AND e.prin_status IS TRUE

                WHERE a.prco_status IS TRUE
                  AND a.prco_categorizacion = ANY (ARRAY[1,2,3,4])
                  AND a.prco_registration_status IS TRUE
                  AND (p_codigo_proyecto IS NULL
                       OR a.prco_cua::text = p_codigo_proyecto)

                GROUP BY
                    a.prco_id,
                    a.prco_cua,
                    a.prco_name,
                    a.prco_description,
                    a.prco_address,
                    a.prco_cua_date,
                    coalesce(og.orga_name_organization, c.peop_name),
                    coalesce(og.orga_ruc, c.peop_pin),
                    ci.caci_name,
                    ci.caci_code,
                    ct.sety_name,
                    ar.area_name,
                    at.arty_name,
                    a.prco_categorizacion,
                    gl3.gelo_name,
                    gl2.gelo_name,
                    gl1.gelo_name,
                    ar.area_id,
                    a.prco_project_finished,
                    a.prco_viability_favorable,
                    e.prin_final_result_eia_cata_id,
                    rec.enre_number_resolution,
                    reg.enre_number_resolution,
                    cer.pece_code,
                    rec.enre_creation_date,
                    reg.enre_creation_date,
                    cer.pece_creation_date,
                    a.prco_surface,
                    z1.zone_public_name,
                    a.prco_waste_generation,
                    a.prco_waste_management,
                    a.prco_vegetable_verture,
                    a.prco_chemical_substances,
                    a.prco_chemical_substances_transport,
                    a.prco_enviromental_impact

            ) x
            LEFT JOIN LATERAL (
                SELECT string_agg(
                    concat(
                        cic.cein_viability_intersection, '   ',
                        cic.cein_other_intersection
                    ),
                    ' ; ' ORDER BY concat(
                        cic.cein_viability_intersection, '   ',
                        cic.cein_other_intersection
                    )
                ) AS intersecta_con
                FROM coa_mae.certificate_intersection_coa cic
                WHERE cic.prco_id = x.prco_id
                  AND cic.cein_status IS TRUE
            ) ic ON TRUE
            LEFT JOIN (
                SELECT
                    t1.codigoproyecto,
                    t1.processinstanceid,
                    t1.nombreproceso,
                    t1.estadoproceso,
                    t1.fechainicioproceso,
                    t1.fechafinproceso,
                    t1.nombretarea,
                    t1.estadotarea,
                    t1.fechainiciotarea,
                    t1.fechafintarea,
                    t1.usuariotarea
                FROM dblink(
                    'dbname=suia_bpms_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres'::text,
                    '
select distinct
    v.value             codigoProyecto,
    t.processinstanceid processinstanceid,
    p.processname       nombreProceso,
    CASE
        WHEN p.status = 1 THEN ''En trámite''
        WHEN p.status = 2 THEN ''Completado''
        WHEN p.status = 3 THEN ''Abortado''
        WHEN p.status = 4 THEN ''Abortado''
        WHEN p.status = 5 THEN ''Abortado''
        ELSE ''Abortado''
    END                 estadoProceso,
    p.start_date        fechaInicioProceso,
    p.end_date          fechaFinProceso,
    coalesce(t.taskname, ta.name) nombreTarea,
    case when p.status = ''1'' then ta.status      else t.status    end estadoTarea,
    case when p.status = ''1'' then activationtime else t.createddate end fechaInicioTarea,
    case when p.status = ''1'' then logtime        else t.enddate   end fechaFinTarea,
    case when p.status = ''1'' then coalesce(actualowner_id, createdby_id)
                                else t.userid end usuarioTarea
from variableinstancelog v
    left  join processinstancelog p  on p.processinstanceid = v.processinstanceid
    left  join bamtasksummary t      on t.processinstanceid = p.processinstanceid
    left  join task ta               on p.processinstanceid = ta.processinstanceid
                                    and ta.id = t.taskid
    left  join (
        select distinct on (te.taskid) te.id, te.taskid, te.userid, te.logtime
        from taskevent te where te.type = ''COMPLETED''
    ) te on te.taskid = t.taskid
where user_identity not like ''%msit%''
  and user_identity not like ''%admin%''
  and v.variableid = ''tramite''
  and p.status in (1, 2)
'::text
                ) t1 (
                    codigoproyecto      text,
                    processinstanceid   text,
                    nombreproceso       text,
                    estadoproceso       text,
                    fechainicioproceso  timestamp without time zone,
                    fechafinproceso     timestamp without time zone,
                    nombretarea         text,
                    estadotarea         text,
                    fechainiciotarea    timestamp without time zone,
                    fechafintarea       timestamp without time zone,
                    usuariotarea        text
                )
                GROUP BY
                    t1.codigoproyecto,   t1.processinstanceid, t1.nombreproceso,
                    t1.estadoproceso,    t1.fechainicioproceso, t1.fechafinproceso,
                    t1.nombretarea,      t1.estadotarea,
                    t1.fechainiciotarea, t1.fechafintarea,      t1.usuariotarea
            ) y ON y.codigoproyecto = x."CÓDIGO PROYECTO"

            ORDER BY x."CÓDIGO PROYECTO", y.fechainiciotarea DESC
        ) yy
    ) pp;
END;
$function$
;
