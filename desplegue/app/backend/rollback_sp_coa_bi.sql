CREATE OR REPLACE FUNCTION suia_iii.sp_coa_bi() RETURNS void LANGUAGE plpgsql AS $function$ BEGIN truncate table suia_iii.tmp_coa_bi;
INSERT INTO suia_iii.tmp_coa_bi
SELECT DISTINCT q."CÓDIGO PROYECTO",
    q."NOMBRE PROYECTO",
    q."RESUMEN PROYECTO",
    q."DIRECCIÓN PROYECTO",
    q."FECHA REGISTRO PROYECTO" AS "FECHA REGISTRO",
    q."CÓDIGO ACTIVIDAD",
    q."ACTIVIDAD ECONÓMICA",
    q."CI/RUC PROPONENTE" AS "CED/RUC PROPONENTE",
    q."PROPONENTE" AS "NOMBRE PROPONENTE",
    q."AREA RESPONSABLE" AS "ÁREA RESPONSABLE PROYECTO",
    q."SECTOR" AS "TIPO SECTOR",
    q."TIPO LICENCIA" AS "TIPO PERMISO AMBIENTAL",
    q."ENTE RESPONSABLE" AS "TIPO ENTE",
    q."PROVINCIA",
    q."CANTON",
    q."PARROQUIA",
    q."PROCESO",
    q."ESTADO PROCESO",
    q."FECHA INICIO PROCESO",
    q."FECHA FIN PROCESO",
    q."TAREA",
    q."ESTADO TAREA",
    q."FECHA INICIO TAREA",
    q."FECHA FIN TAREA",
    q."USUARIO TAREA",
    q."ESTADO PROYECTO",
    q."INTERSECTA CON",
    q."AREAS PROTEGIDAS",
    q."SISTEMA",
    q."NOMBRE ZONA",
    q."FINALIZADO CON RESOLUCION",
    q."NUMERO RESOLUCION",
    q."FECHA RESOLUCION",
    q."OBSERVADO",
    q."SUPERFICIE PROYECTO",
    q."ID AREA",
    CASE
        WHEN "ESTADO PROYECTO" = 'Completado'
        and q."OBSERVADO" is true THEN 'FINALIZADO NO FAVORABLE'::text
        WHEN "ESTADO PROYECTO" = 'Completado Digitalizado' THEN 'FINALIZADO DIGITALIZADO'::text
        WHEN "ESTADO PROYECTO" = 'Completado No Favorable' THEN 'FINALIZADO NO FAVORABLE'::text
        WHEN (
            "ESTADO PROYECTO" = 'En trámite'
            AND "TIPO LICENCIA" like '%Licen%'
            AND "FECHA REGISTRO PROYECTO" >= '2018-04-12 00:00:00'::timestamp without time zone
        ) THEN 'PROCESO FISICO'::text
        WHEN "ESTADO PROYECTO" = 'Completado' THEN 'FINALIZADO EXITO'::text
        ELSE 'EN TRÁMITE'::text
    END AS "ESTADO TRÁMITE",
    CURRENT_TIMESTAMP AS "FECHA_CARGA_DATOS",
    cate_code,
    CASE
        WHEN "Genera Residuos" = TRUE THEN 'SI'
        ELSE 'NO'
    END,
CASE
        WHEN "Gestion de residuos peligrosos" = TRUE THEN 'SI'
        ELSE 'NO'
    END,
CASE
        WHEN "utiliza sustancias quimicas" = TRUE THEN 'SI'
        ELSE 'NO'
    END,
    CASE
        WHEN "transporte de productos quimicos" = TRUE THEN 'SI'
        ELSE 'NO'
    END
FROM (
        SELECT DISTINCT x."CÓDIGO PROYECTO",
            x."NOMBRE PROYECTO",
            x."RESUMEN PROYECTO",
            x."DIRECCIÓN PROYECTO",
            x."FECHA REGISTRO PROYECTO",
            x."TIPO ORGANIZACIÓN",
            x."SECTOR",
            x."TIPO LICENCIA",
            x."CÓDIGO ACTIVIDAD",
            x."ACTIVIDAD ECONÓMICA",
            x."AREA RESPONSABLE",
            x."CATEGORÍA",
            x."ENTE RESPONSABLE",
            x."PROVINCIA",
            x."CANTON",
            x."PARROQUIA",
            x."CI/RUC PROPONENTE",
            x."PROPONENTE",
            x.area_id,
            y.nombreproceso AS "PROCESO",
            y.estadoproceso "ESTADO PROCESO",
            y.fechainicioproceso::date AS "FECHA INICIO PROCESO",
            y.fechafinproceso::date "FECHA FIN PROCESO",
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
            'COA'::text AS "SISTEMA",
            x."NOMBRE ZONA",
            x."FINALIZADO CON RESOLUCION",
            x."NUMERO RESOLUCION",
            x."FECHA RESOLUCION",
            x."OBSERVADO",
            x."SUPERFICIE PROYECTO",
            x."ID AREA",
            cate_code,
            "Genera Residuos",
            "Gestion de residuos peligrosos",
            "utiliza sustancias quimicas",
            "transporte de productos quimicos"
        FROM (
                SELECT DISTINCT a.pren_code AS "CÓDIGO PROYECTO",
                    a.pren_name AS "NOMBRE PROYECTO",
                    a.pren_resume AS "RESUMEN PROYECTO",
                    a.pren_address AS "DIRECCIÓN PROYECTO",
                    a.pren_register_date::date AS "FECHA REGISTRO PROYECTO",
                    ot.orty_name AS "TIPO ORGANIZACIÓN",
                    st.sety_name AS "SECTOR",
                    cte.cate_public_name AS "TIPO LICENCIA",
                    ct.cacs_code AS "CÓDIGO ACTIVIDAD",
                    ct.cacs_description AS "ACTIVIDAD ECONÓMICA",
                    ar.area_name AS "AREA RESPONSABLE",
                    cte.cate_description AS "CATEGORÍA",
                    at.arty_name AS "ENTE RESPONSABLE",
                    coalesce(gl3.gelo_name::text, gl6.gelo_name) AS "PROVINCIA",
                    coalesce(gl2.gelo_name, gl5.gelo_name) AS "CANTON",
                    coalesce(gl1.gelo_name, gl4.gelo_name) AS "PARROQUIA",
                    b.user_name AS "CI/RUC PROPONENTE",
                    a.pren_immediate_environmental_certificate,
                    a.pren_project_finished,
                    a.pren_registro_ambiental_imediato,
                    coalesce(og.orga_name_organization, c.peop_name) "PROPONENTE",
                    a.area_id,
                    pl.prlo_id,
                    CASE
                        WHEN a.pren_project_finished IS TRUE
                        and dig.enaa_code is not null
                        and dig.enaa_status_finalized is true THEN 'Completado Digitalizado'::text
                        when a.pren_project_finished IS TRUE
                        and "VIABILIDAD FAVORABLE" = 'No favorable' then 'Completado No Favorable'::text
                        WHEN a.pren_project_finished IS TRUE THEN 'Completado'::text
                        ELSE 'En trámite'::text
                    END AS "ESTADO PROYECTO",
                    case
                        when (
                            lity_id = 1
                            and cc.ence_status = true
                        ) then 'Finalizado con Resolución'
                        when (
                            lity_id in (2, 5)
                            and (
                                rm.mien_finalized = true
                                or cafa_finalized = true
                            )
                        ) then 'Finalizado con Resolución'
                        when (
                            (
                                lity_id in (3, 4)
                                and trel_finalized = true
                                and trel_status = true
                            )
                        ) then 'Finalizado con Resolución'
                        else null
                    end "FINALIZADO CON RESOLUCION",
                    cafa_license_number "NUMERO RESOLUCION",
                    cafa_creation_date "FECHA RESOLUCION",
                    a.pren_tree_observations "OBSERVADO",
                    a.pren_area "SUPERFICIE PROYECTO",
                    (
                        SELECT string_agg(
                                intersections_project.inpr_layer_description::text,
                                '  '::text
                                ORDER BY 1::integer
                            ) AS string_agg
                        FROM suia_iii.intersections_project
                        WHERE intersections_project.pren_id = a.pren_id
                            AND intersections_project.inpr_status IS TRUE
                    ) AS "INTERSECTA CON",
                    case
                        when k.zone_public_name is null then 'N/A'
                        else k.zone_public_name
                    end AS "NOMBRE ZONA",
                    ar.area_id "ID AREA",
                    (
                        string_agg(
                            concat(
                                ip.inpr_layer_description,
                                '   ',
                                regexp_replace(dip.dein_geometry_name, '[^a-zA-Z0-9 ]', '', 'g')
                            ),
                            '  '::text
                            ORDER BY (
                                    concat(
                                        ip.inpr_layer_description,
                                        '   ',
                                        regexp_replace(dip.dein_geometry_name, '[^a-zA-Z0-9 ]', '', 'g')
                                    )
                                )
                        )
                    ) AS "AREAS PROTEGIDAS",
                    cate_code,
                    ct.cacs_waste_generated as "Genera Residuos",
                    ct.cacs_manages_hazardous_waste as "Gestion de residuos peligrosos",
                    ct.cacs_uses_chemical_substances as "utiliza sustancias quimicas",
                    ct.cacs_transpor_hazardous_chemicals as "transporte de productos quimicos"
                FROM suia_iii.projects_environmental_licensing a
                    left join suia_iii.licensing l on a.pren_id = l.pren_id
                    left join suia_iii.technical_report_environmental_licensing_general r on r.lice_id = l.lice_id
                    left join suia_iii.catii_fapma ra on ra.pren_id = a.pren_id
                    left join suia_iii.mining_enviromental_record rm on rm.pren_id = a.pren_id --mien_finalized
                    JOIN suia_iii.categories_catalog_system ct ON ct.cacs_id = a.cacs_id
                    LEFT JOIN suia_iii.environmental_certificates_registration cc ON a.pren_id = cc.pren_id
                    AND a.pren_project_finalized IS TRUE
                    AND cc.ence_status IS TRUE
                    LEFT JOIN suia_iii.sector_types st ON st.sety_id = a.sety_id
                    JOIN users b ON b.user_id = a.user_id
                    JOIN people c ON c.peop_id = b.peop_id
                    LEFT JOIN organizations og ON og.orga_ruc::text = b.user_name::text
                    LEFT JOIN areas ar ON ar.area_id = a.area_id
                    LEFT JOIN areas_types at ON at.arty_id = ar.arty_id
                    LEFT JOIN suia_iii.projects_locations pl ON pl.pren_id = a.pren_id
                    and pl.prlo_status is true
                    left JOIN geographical_locations gl1 ON pl.gelo_id = gl1.gelo_id
                    left JOIN geographical_locations gl2 ON gl1.gelo_parent_id = gl2.gelo_id
                    left JOIN geographical_locations gl3 ON gl2.gelo_parent_id = gl3.gelo_id
                    LEFT JOIN organizations_types ot ON ot.orty_id = og.tyor_id
                    JOIN suia_iii.categories cte ON cte.cate_id = ct.cate_id
                    LEFT JOIN areas z ON ar.area_parent_id = z.area_id
                    LEFT JOIN zones k ON k.zone_id = z.zone_id
                    left join suia_iii.mining_grants mg on mg.pren_id = a.pren_id
                    left join suia_iii.mining_grants_locations mgl on mgl.migr_id = mg.migr_id
                    left join geographical_locations gg on gg.gelo_id = mgl.gelo_id
                    left JOIN geographical_locations gl4 ON gg.gelo_id = gl4.gelo_id
                    left JOIN geographical_locations gl5 ON gl4.gelo_parent_id = gl5.gelo_id
                    left JOIN geographical_locations gl6 ON gl5.gelo_parent_id = gl6.gelo_id
                    LEFT JOIN suia_iii.intersections_project ip ON ip.pren_id = a.pren_id
                    AND ip.laye_id = 3
                    AND ip.inpr_buffer_intersection IS FALSE
                    LEFT JOIN suia_iii.details_intersection_project dip ON ip.inpr_id = dip.inpr_id
                    left join coa_digitalization_linkage.environmental_administrative_authorizations dig on dig.enaa_project_code = a.pren_code
                    and enaa_system = 4
                    and enaa_status is true
                    left join suia_iii.tmp_pronunciamientos pr on pr.codigo_proyecto = a.pren_code
                WHERE a.pren_status IS TRUE
                    AND pren_project_finalized is true
                    and pren_project_hidrocarbons is null
                    AND (ct.cate_id = ANY (ARRAY [1, 2, 3, 4]))
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
                    28,
                    29,
                    30,
                    31,
                    32,
                    cate_code,
                    ct.cacs_waste_generated,
                    ct.cacs_manages_hazardous_waste,
                    ct.cacs_uses_chemical_substances,
                    ct.cacs_transpor_hazardous_chemicals
                ORDER by 1,
                    pl.prlo_id asc
            ) x
            LEFT JOIN (
                SELECT t1.codigoproyecto,
                    t1.processinstanceid,
                    CASE
                        WHEN t1.nombreproceso = ANY (
                            ARRAY ['Registro ambiental v2'::text, 'Registro ambiental'::text]
                        ) THEN 'Registro Ambiental'::text
                        WHEN t1.nombreproceso = 'CertificadoAmbiental'::text THEN 'Certificado Ambiental'::text
                        ELSE t1.nombreproceso
                    END AS nombreproceso,
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
 	ELSE ''En trámite''
   END as estadoProceso, 
   p.start_date  as fechaInicioProceso ,
   p.end_date as fechaFinProceso,
   coalesce(t.taskname, ta.name) nombreTarea,
    case when p.status = ''1'' then ta.status else t.status end as estadoTarea,  
  case when p.status = ''1'' then activationtime else t.createddate end as fechaInicioTarea, 
  case when p.status = ''1'' then logtime else t.enddate end as fechaFinTarea, 
  case when p.status = ''1'' then coalesce(actualowner_id, createdby_id) else t.userid end as usuarioTarea  
 from variableinstancelog v
   inner join processinstancelog p on p.processinstanceid = v.processinstanceid
   left join bamtasksummary t on t.processinstanceid = p.processinstanceid  
   left join task ta on p.processinstanceid =ta.processinstanceid and ta.id = t.taskid   
   left join (
     select distinct on (te.taskid) te.id, te.taskid, te.userid, te.logtime  from taskevent te where te.type =''COMPLETED''  
   ) te on te.taskid =  t.taskid  
   where 
     user_identity not like ''%msit%''
   and user_identity not like ''%admin%''
   and v.variableid in (''tramite'' ,''codigoProyecto'') 
   and coalesce(t.taskname, ta.name) is not null
  and p.status in ( 1, 2 )
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
                union all
                (
                    select pren_code::text,
                        '0'::text processinstanceid,
                        "PROCESO",
                        "ESTADO PROCESO",
                        "FECHA INICIO PROCESO",
                        "FECHA FIN PROCESO",
                        "TAREA",
                        "ESTADO TAREA",
                        "FECHA INICIO TAREA",
                        "FECHA FIN TAREA",
                        null
                    from suia_iii.certificados_inmediatos_bpm cbp
                )
            ) y ON y.codigoproyecto = x."CÓDIGO PROYECTO"::text
        ORDER BY x."CÓDIGO PROYECTO",
            y.fechainiciotarea DESC
    ) q;
END;
$function$;