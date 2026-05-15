/*
 * Nuevas Funciones Versionadas: Biodiversidad v1.4.1
 * Autor: Antigravity AI
 * Descripción: Funciones segregadas que capturan SNAP, Patrimonio, Zonas Intangibles y Bosques Protectores.
 */
-- 1. Nueva Función: suia_iii.sp_coa_bi_v1_4_1()
CREATE OR REPLACE FUNCTION suia_iii.sp_coa_bi_v1_4_1() RETURNS void LANGUAGE plpgsql AS $function$ BEGIN truncate table suia_iii.tmp_coa_bi;
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
                                ' | ',
                                regexp_replace(dip.dein_geometry_name, '[^a-zA-Z0-9 ]', '', 'g')
                            ),
                            ' ; '::text
                            ORDER BY (ip.laye_id)
                        )
                    ) AS "AREAS PROTEGIDAS",
                    cte.cate_code,
                    ct.cacs_waste_generated as "Genera Residuos",
                    ct.cacs_manages_hazardous_waste as "Gestion de residuos peligrosos",
                    ct.cacs_uses_chemical_substances as "utiliza sustancias quimicas",
                    ct.cacs_transpor_hazardous_chemicals as "transporte de productos quimicos"
                FROM suia_iii.projects_environmental_licensing a
                    left join suia_iii.licensing l on a.pren_id = l.pren_id
                    left join suia_iii.technical_report_environmental_licensing_general r on r.lice_id = l.lice_id
                    left join suia_iii.catii_fapma ra on ra.pren_id = a.pren_id
                    left join suia_iii.mining_enviromental_record rm on rm.pren_id = a.pren_id
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
                    AND ip.laye_id IN (2, 3, 4, 11)
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
-- 2. Nueva Función: coa_mae.sp_rcoa_bi_v1_4_1()
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