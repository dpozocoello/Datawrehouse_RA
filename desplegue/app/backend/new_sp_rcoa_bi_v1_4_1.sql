CREATE OR REPLACE FUNCTION coa_mae.sp_rcoa_bi_v1_4_1() RETURNS void LANGUAGE plpgsql AS $function$ BEGIN truncate table coa_mae.tmp_rcoa_bi;
INSERT INTO coa_mae.tmp_rcoa_bi
SELECT DISTINCT pp."CÓDIGO PROYECTO",
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
    CURRENT_TIMESTAMP AS "FECHA_CARGA_DATOS",
    "INTERSECTA"
FROM (
        SELECT DISTINCT yy."CÓDIGO PROYECTO",
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
            'RCOA'::text AS "SISTEMA",
            yy."NOMBRE ZONA",
            yy."FINALIZADO CON RESOLUCION",
            yy."NUMERO RESOLUCION",
            yy."FECHA RESOLUCION",
            yy."ID AREA",
            yy."SUPERFICIE PROYECTO",
            CASE
                WHEN "ESTADO PROYECTO" = 'Completado' THEN 'FINALIZADO EXITO'::text
                WHEN "ESTADO PROYECTO" = 'Completado No Favorable' THEN 'FINALIZADO NO FAVORABLE'::text
                WHEN (
                    "ESTADO PROYECTO" = 'En trámite'
                    AND "TIPO PERMISO AMBIENTAL" like '%Licen%'
                    AND "FECHA REGISTRO" >= '2021-10-12'
                    and "PROCESO" = 'Estudio Impacto Ambiental'
                    and "ESTADO PROCESO" = 'Completado'
                ) THEN 'PROCESO FISICO'::text
                WHEN "ESTADO PROYECTO" = 'En trámite'
                AND "TIPO PERMISO AMBIENTAL" like '%Regist%'
                AND "FECHA REGISTRO" >= '2023-06-02'
                and "TIPO SECTOR" in ('Minería', 'Hidrocarburos')
                and "PROCESO" in ('Registro Ambiental') THEN 'DIGITALIZACION'::text
                ELSE 'EN TRÁMITE'::text
            END AS "ESTADO TRÁMITE",
            prco_waste_generation,
            prco_waste_management,
            prco_vegetable_verture,
            prco_chemical_substances,
            prco_chemical_substances_transport,
            prco_enviromental_impact,
            "INTERSECTA"
        FROM (
                SELECT DISTINCT x."CÓDIGO PROYECTO",
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
                        WHEN y.nombreproceso = 'Registro ambiental v2'::text THEN 'Registro Ambiental'::text
                        ELSE y.nombreproceso
                    END AS "PROCESO",
                    y.estadoproceso AS "ESTADO PROCESO",
                    y.fechainicioproceso AS "FECHA INICIO PROCESO",
                    y.fechafinproceso AS "FECHA FIN PROCESO",
                    CASE
                        WHEN y.estadoproceso = 'Completado'::text THEN y.fechafinproceso
                        WHEN y.estadoproceso = 'En trámite'::text THEN x."FECHA REGISTRO"
                        ELSE NULL::timestamp without time zone
                    END AS "FECHA ESTADO PROYECTO",
                    x."CED/RUC PROPONENTE",
                    x."NOMBRE PROPONENTE",
                    x.area_id,
                    y.nombretarea AS "TAREA",
                    CASE
                        WHEN y.estadotarea ~~ 'Completed%'::text THEN 'Completado'::text
                        WHEN y.estadotarea = ANY (
                            ARRAY ['Created'::text, 'InProgress'::text, 'Ready'::text, 'Reserved'::text]
                        ) THEN 'En trámite'::text
                        ELSE y.estadotarea
                    END AS "ESTADO TAREA",
                    y.fechainiciotarea AS "FECHA INICIO TAREA",
                    y.fechafintarea AS "FECHA FIN TAREA",
                    y.usuariotarea AS "USUARIO TAREA",
                    x."ESTADO PROYECTO",
                    x."INTERSECTA CON",
                    x."AREAS PROTEGIDAS",
                    x."NOMBRE ZONA",
                    x."FINALIZADO CON RESOLUCION",
                    x."NUMERO RESOLUCION",
                    x."FECHA RESOLUCION",
                    x."ID AREA",
                    x."SUPERFICIE PROYECTO",
                    x.prco_categorizacion,
                    prco_waste_generation,
                    prco_waste_management,
                    prco_vegetable_verture,
                    prco_chemical_substances,
                    prco_chemical_substances_transport,
                    prco_enviromental_impact,
                    NULL "INTERSECTA"
                FROM (
                        SELECT DISTINCT a.prco_cua AS "CÓDIGO PROYECTO",
                            a.prco_name AS "NOMBRE PROYECTO",
                            a.prco_description AS "RESUMEN PROYECTO",
                            a.prco_address AS "DIRECCIÓN PROYECTO",
                            a.prco_cua_date AS "FECHA REGISTRO",
                            CASE
                                WHEN a.prco_registration_status IS TRUE THEN 'SI FINALIZO EL REGISTRO DEL PROYECTO'::text
                                WHEN a.prco_registration_status IS FALSE THEN 'NO FINALIZO EL REGISTRO DEL PROYECTO'::text
                                ELSE ''::text
                            END AS "FINALIZO EL REGISTRO",
                            coalesce(og.orga_name_organization, c.peop_name) "NOMBRE PROPONENTE",
                            coalesce(og.orga_ruc, c.peop_pin) AS "CED/RUC PROPONENTE",
                            ci.caci_name AS "ACTIVIDAD ECONÓMICA",
                            ci.caci_code AS "CÓDIGO ACTIVIDAD",
                            ct.sety_name AS "TIPO SECTOR",
                            ar.area_name AS "ÁREA RESPONSABLE PROYECTO",
                            at.arty_name AS "TIPO ENTE",
                            CASE
                                WHEN a.prco_categorizacion = 1 THEN 'Certificado Ambiental'::text
                                WHEN a.prco_categorizacion = 2 THEN 'Registro Ambiental'::text
                                WHEN a.prco_categorizacion = 3 THEN 'Licencia Ambiental'::text
                                WHEN a.prco_categorizacion = 4 THEN 'Licencia Ambiental'::text
                                ELSE NULL::text
                            END AS "TIPO PERMISO AMBIENTAL",
                            at.arty_name AS "ENTE RESPONSABLE",
                            gl3.gelo_name AS "PROVINCIA",
                            gl2.gelo_name AS "CANTON",
                            gl1.gelo_name AS "PARROQUIA",
                            ar.area_id,
                            CASE
                                WHEN a.prco_project_finished IS TRUE
                                and (
                                    a.prco_viability_favorable is false
                                    or (
                                        e.prin_final_result_eia_cata_id is not null
                                        and e.prin_final_result_eia_cata_id != 8
                                    )
                                ) then 'Completado No Favorable'::text
                                WHEN a.prco_project_finished IS TRUE
                                and prco_viability_favorable is not false THEN 'Completado'::text
                                ELSE 'En trámite'::text
                            END AS "ESTADO PROYECTO",
                            case
                                when rec.enre_number_resolution is not null then 'Finalizado con Resolución'::text
                                when reg.enre_number_resolution is not null then 'Finalizado con Resolución'::text
                                when cer.pece_code is not null then 'Finalizado con Resolución'::text
                                else null
                            end "FINALIZADO CON RESOLUCION",
                            coalesce(
                                coalesce(
                                    rec.enre_number_resolution,
                                    reg.enre_number_resolution
                                ),
                                cer.pece_code
                            ) "NUMERO RESOLUCION",
                            coalesce(
                                rec.enre_creation_date,
                                reg.enre_creation_date,
                                cer.pece_creation_date
                            ) "FECHA RESOLUCION",
                            ar.area_id "ID AREA",
                            a.prco_surface "SUPERFICIE PROYECTO",
                            (
                                SELECT string_agg(
                                        concat(
                                            certificate_intersection_coa.cein_viability_intersection,
                                            '   ',
                                            certificate_intersection_coa.cein_other_intersection
                                        ),
                                        ' ; '::text
                                        ORDER BY (
                                                concat(
                                                    certificate_intersection_coa.cein_viability_intersection,
                                                    '   ',
                                                    certificate_intersection_coa.cein_other_intersection
                                                )
                                            )
                                    ) AS string_agg
                                FROM coa_mae.certificate_intersection_coa
                                WHERE certificate_intersection_coa.prco_id = a.prco_id
                                    AND certificate_intersection_coa.cein_status IS TRUE
                            ) AS "INTERSECTA CON",
                            case
                                when z1.zone_public_name is null then 'N/A'
                                else z1.zone_public_name
                            end AS "NOMBRE ZONA",
                            (
                                string_agg(
                                    concat(
                                        aa.inpr_layer_description,
                                        ' | ',
                                        regexp_replace(b_1.dein_geometry_name, '[^a-zA-Z0-9 ]', '', 'g')
                                    ),
                                    ' ; '
                                )
                            ) AS "AREAS PROTEGIDAS",
                            prco_categorizacion,
                            prco_waste_generation,
                            prco_waste_management,
                            prco_vegetable_verture,
                            prco_chemical_substances,
                            prco_chemical_substances_transport,
                            prco_enviromental_impact
                        FROM coa_mae.project_licencing_coa a
                            JOIN users bb ON bb.user_id = a.user_id
                            JOIN people c ON c.peop_id = bb.peop_id
                            LEFT JOIN organizations og ON og.orga_ruc::text = bb.user_name::text
                            JOIN coa_mae.project_licencing_coa_location b ON b.prco_id = a.prco_id
                            AND b.prlo_status IS TRUE
                            LEFT JOIN coa_mae.project_licencing_coa_ciuu lc ON lc.prco_id = b.prco_id
                            AND lc.prli_primary is true
                            AND lc.prli_status IS TRUE
                            and b.prlo_primary is true
                            JOIN coa_mae.catalog_ciuu ci ON ci.caci_id = lc.caci_id
                            JOIN geographical_locations gl1 ON b.gelo_id = gl1.gelo_id
                            JOIN geographical_locations gl2 ON gl1.gelo_parent_id = gl2.gelo_id
                            JOIN geographical_locations gl3 ON gl2.gelo_parent_id = gl3.gelo_id
                            JOIN coa_mae.project_licencing_coa_ciuu pci ON pci.prco_id = a.prco_id
                            AND pci.prli_primary is true
                            AND pci.prli_status IS TRUE
                            JOIN coa_mae.catalog_ciuu ciu ON ciu.caci_id = pci.caci_id
                            JOIN suia_iii.sector_types ct ON ct.sety_id = ci.sety_id
                            LEFT JOIN areas ar ON ar.area_id = a.area_id
                            LEFT JOIN areas_types at ON at.arty_id = ar.arty_id
                            LEFT JOIN areas z ON ar.area_parent_id = z.area_id
                            LEFT JOIN zones z1 ON z1.zone_id = z.zone_id
                            left join coa_mae.intersections_project_licencing_coa aa on aa.prco_id = a.prco_id
                            AND aa.laye_id IN (2, 3, 4, 11)
                            and inpr_status is true
                            left JOIN coa_mae.details_intersection_project_licencing_coa b_1 ON aa.inpr_id = b_1.inpr_id
                            AND b_1.dein_status IS true
                            LEFT JOIN payments.unique_transaction_number utn ON a.prco_cua = utn.nut_project_code
                            left join coa_emission_environmental_resolution.environmental_resolution rec ON a.prco_id = rec.prco_id
                            and rec.enre_status is true
                            left join coa_environmental_record.environmental_record reg on reg.prco_id = a.prco_id
                            and reg.enre_status is true
                            left join coa_environmental_certificate.project_environmental_certificate cer on cer.prco_id = a.prco_id
                            and cer.pece_status is true
                            left join coa_environmental_impact_study.project_information e on e.prco_id = a.prco_id
                            and e.prin_status = true
                        WHERE a.prco_status IS TRUE
                            AND (a.prco_categorizacion = ANY (ARRAY [1, 2, 3, 4]))
                            AND prco_registration_status IS true
                        group by 1,
                            2,
                            3,
                            4,
                            5,
                            6,
                            7,
                            8,
                            9,
                            10,
                            11,
                            12,
                            13,
                            14,
                            15,
                            16,
                            17,
                            18,
                            19,
                            20,
                            21,
                            22,
                            23,
                            24,
                            25,
                            26,
                            27,
                            prco_categorizacion,
                            prco_waste_generation,
                            prco_waste_management,
                            prco_vegetable_verture,
                            prco_chemical_substances,
                            prco_chemical_substances_transport,
                            prco_enviromental_impact
                    ) x
                    LEFT JOIN (
                        SELECT t1.codigoproyecto,
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
 select 
   distinct v.value codigoProyecto, 
   t.processinstanceid processinstanceid, 
   p.processname as nombreProceso,
   CASE
 	WHEN p.status = 1 THEN ''En trámite''
 	WHEN p.status = 2 THEN ''Completado''
 	WHEN p.status = 3 THEN ''Abortado''
 	WHEN p.status = 4 THEN ''Abortado''
         WHEN p.status = 5 THEN ''Abortado''
 	ELSE ''Abortado''
   END as estadoProceso, 
   p.start_date  as fechaInicioProceso ,
   p.end_date as fechaFinProceso,
   coalesce(t.taskname, ta.name) nombreTarea,
   case when p.status = ''1'' then ta.status else t.status end as estadoTarea,  
   case when p.status = ''1'' then activationtime else t.createddate end as fechaInicioTarea, 
  case when p.status = ''1'' then logtime else t.enddate end as fechaFinTarea, 
  case when p.status = ''1'' then coalesce(actualowner_id, createdby_id) else t.userid end as usuarioTarea 
 from variableinstancelog v
   left join processinstancelog p on p.processinstanceid = v.processinstanceid
   left join bamtasksummary t on t.processinstanceid = p.processinstanceid 
   left join task ta on p.processinstanceid =ta.processinstanceid and ta.id = t.taskid 
       left join (
     select distinct on (te.taskid) te.id, te.taskid, te.userid, te.logtime  from taskevent te where te.type =''COMPLETED''  
   ) te on te.taskid =  t.taskid  
   where 
    user_identity not like ''%msit%''
    and user_identity not like ''%admin%''
    and v.variableid=''tramite''
  
    and p.status  in (1, 2)
 '::text
                            ) t1(
                                codigoproyecto text,
                                processinstanceid text,
                                nombreproceso text,
                                estadoproceso text,
                                fechainicioproceso timestamp without time zone,
                                fechafinproceso timestamp without time zone,
                                nombretarea text,
                                estadotarea text,
                                fechainiciotarea timestamp without time zone,
                                fechafintarea timestamp without time zone,
                                usuariotarea text
                            )
                        GROUP BY t1.codigoproyecto,
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
                    ) y ON y.codigoproyecto = x."CÓDIGO PROYECTO"::text
                ORDER BY x."CÓDIGO PROYECTO",
                    y.fechainiciotarea DESC
            ) yy
    ) pp;
END;
$function$;