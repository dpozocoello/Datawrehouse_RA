-- [v1.4 EXPERT] Comprehensive Political Geography Normalization
-- Final Resolution: 100% of Areas (75/75 manual inferences for missing gelo_id)
-- Procesa el total de Direcciones Zonales, Oficinas Técnicas y Planta Central.
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_area() RETURNS void AS $$ BEGIN
INSERT INTO dw.dim_area (
        id_area,
        nombre_area,
        abreviatura_area,
        id_area_padre,
        zona,
        campus,
        provincia,
        canton,
        parroquia,
        estado_area
    ) WITH RECURSIVE geo_hierarchy AS (
        SELECT s.area_id,
            g.gelo_id,
            g.gelo_name,
            g.gelo_parent_id,
            g.gelo_codification_inec,
            1 as depth
        FROM stg.suia_areas_bi s
            JOIN stg.geographical_locations_bi g ON s.gelo_id = g.gelo_id
        UNION ALL
        SELECT gh.area_id,
            p.gelo_id,
            p.gelo_name,
            p.gelo_parent_id,
            p.gelo_codification_inec,
            gh.depth + 1
        FROM geo_hierarchy gh
            JOIN stg.geographical_locations_bi p ON gh.gelo_parent_id = p.gelo_id
    ),
    pivoted_geo AS (
        SELECT area_id,
            MAX(CASE WHEN depth = 1 THEN gelo_name END) as l1,
            MAX(CASE WHEN depth = 2 THEN gelo_name END) as l2,
            MAX(CASE WHEN depth = 3 THEN gelo_name END) as l3,
            MAX(CASE WHEN depth = 4 THEN gelo_name END) as l4,
            MAX(CASE WHEN depth = 5 THEN gelo_name END) as l5,
            MAX(CASE WHEN depth = 1 THEN gelo_codification_inec END) as inec_l1,
            MAX(CASE WHEN depth = 2 THEN gelo_codification_inec END) as inec_l2,
            MAX(CASE WHEN depth = 3 THEN gelo_codification_inec END) as inec_l3,
            MAX(CASE WHEN depth = 4 THEN gelo_codification_inec END) as inec_l4,
            MAX(CASE WHEN depth = 5 THEN gelo_codification_inec END) as inec_l5
        FROM geo_hierarchy
        GROUP BY area_id
    ),
    resolved_geo AS (
        SELECT area_id,
            CASE
                WHEN l5 = 'ECUADOR' THEN l4
                WHEN l4 = 'ECUADOR' THEN l3
                WHEN l3 = 'ECUADOR' THEN l2
                WHEN l2 = 'ECUADOR' THEN l1
                ELSE COALESCE(l1, 'N/A')
            END as prov_raw,
            CASE
                WHEN l5 = 'ECUADOR' THEN inec_l4
                WHEN l4 = 'ECUADOR' THEN inec_l3
                WHEN l3 = 'ECUADOR' THEN inec_l2
                WHEN l2 = 'ECUADOR' THEN inec_l1
                ELSE NULL
            END as inec_prov,
            CASE
                WHEN l5 = 'ECUADOR' THEN l3
                WHEN l4 = 'ECUADOR' THEN l2
                WHEN l3 = 'ECUADOR' THEN l1
                ELSE 'N/A'
            END as cant,
            CASE
                WHEN l5 = 'ECUADOR' THEN l2
                WHEN l4 = 'ECUADOR' THEN l1
                ELSE 'N/A'
            END as parr
        FROM pivoted_geo
    ),
    expert_geo AS (
        SELECT rg.area_id,
            COALESCE(
                i.nombre_provincia,
                CASE
                    WHEN rg.inec_prov = '90' AND rg.prov_raw ILIKE '%SALITRE%' THEN 'GUAYAS'
                    ELSE 'N/A'
                END
            ) as prov_final,
            rg.cant,
            rg.parr
        FROM resolved_geo rg
            LEFT JOIN ref.inec_dpa_2024 i ON rg.inec_prov = i.codigo_provincia
    ),
    final_geo AS (
        SELECT s.area_id,
            s.area_name,
            s.area_abbreviation,
            s.area_parent_id,
            'ZONA ' || s.zone_id::text as zona_str,
            s.area_campus,
            COALESCE(eg.prov_final, 'N/A') as prov_res,
            COALESCE(eg.cant, 'N/A') as cant_res,
            COALESCE(eg.parr, 'N/A') as parr_res,
            s.area_status
        FROM stg.suia_areas_bi s
            LEFT JOIN expert_geo eg ON s.area_id = eg.area_id
    )
SELECT f.area_id,
    f.area_name,
    f.area_abbreviation,
    f.area_parent_id,
    f.zona_str,
    f.area_campus,
    -- [v1.4 EXPERT INFERENCE ENGINE] Final fallback for ALL 75 areas without gelo_id
    CASE 
        WHEN f.prov_res = 'N/A' THEN
            CASE 
            WHEN f.area_id = 1115 THEN 'AZUAY' -- OFICINA TÉCNICA URDANETA OÑA
            WHEN f.area_id = 1261 THEN 'PICHINCHA' -- OFICINA TÉCNICA DZ 10
            WHEN f.area_id = 555 THEN 'PICHINCHA' -- CONELEC
            WHEN f.area_id = 1080 THEN 'MANABÍ' -- DIRECCIÓN ZONAL 4
            WHEN f.area_id = 1081 THEN 'ESMERALDAS' -- DIRECCIÓN ZONAL 2
            WHEN f.area_id = 178 THEN 'PICHINCHA' -- UNIDAD ENTE ACREDITADO SECRETARIA DEL AMBIENTE
            WHEN f.area_id = 1 THEN 'ZONAS NO DELIMITADAS' -- UNIDAD ENTE ACREDITADO MUNICIPIO DE GUAYAQUIL
            WHEN f.area_id = 1062 THEN 'LOJA' -- Ordenamiento Ambiental Integral en la Cuenca del Río Puyango.
            WHEN f.area_id = 1258 THEN 'CHIMBORAZO' -- OFICINA TÉCNICA DZ 3
            WHEN f.area_id = 1257 THEN 'GUAYAS' -- OFICINA TÉCNICA DZ 8
            WHEN f.area_id = 1256 THEN 'IMBABURA' -- OFICINA TÉCNICA DZ 1
            WHEN f.area_id = 1253 THEN 'NAPO' -- OFICINA TÉCNICA DZ 2
            WHEN f.area_id = 1252 THEN 'MANABI' -- OFICINA TÉCNICA DZ 4
            WHEN f.area_id = 1255 THEN 'LOJA' -- OFICINA TÉCNICA DZ 7
            WHEN f.area_id = 1254 THEN 'GUAYAS' -- OFICINA TÉCNICA DZ 5
            WHEN f.area_id = 1259 THEN 'AZUAY' -- OFICINA TÉCNICA DZ 6
            WHEN f.area_id = 1260 THEN 'PICHINCHA' -- OFICINA TÉCNICA DZ 9
            WHEN f.area_id = 1082 THEN 'GUAYAS' -- DIRECCIÓN ZONAL 5
            WHEN f.area_id = 1083 THEN 'LOJA' -- DIRECCIÓN ZONAL 7
            WHEN f.area_id = 1084 THEN 'IMBABURA' -- DIRECCIÓN ZONAL 1 
            WHEN f.area_id = 1085 THEN 'NAPO' -- DIRECCIÓN ZONAL 8 
            WHEN f.area_id = 1086 THEN 'CHIMBORAZO' -- DIRECCIÓN ZONAL 3
            WHEN f.area_id = 1087 THEN 'AZUAY' -- DIRECCIÓN ZONAL 6
            WHEN f.area_id = 1088 THEN 'SUCUMBIOS' -- DIRECCIÓN ZONAL 9
            WHEN f.area_id = 1089 THEN 'ZAMORA CHINCHIPE' -- DIRECCIÓN ZONAL 10
            WHEN f.area_id = 1139 THEN 'PICHINCHA' -- DIRECCIÓN DE REGULARIZACIÓN AMBIENTAL
            WHEN f.area_id = 1124 THEN 'COTOPAXI' -- OFICINA TÉCNICA LATACUNGA
            WHEN f.area_id = 1090 THEN 'MANABÍ' -- OFICINA TÉCNICA PEDERNALES
            WHEN f.area_id = 1092 THEN 'MANABÍ' -- OFICINA TÉCNICA PORTOVIEJO
            WHEN f.area_id = 1095 THEN 'ESMERALDAS' -- OFICINA TÉCNICA ELOY ALFARO
            WHEN f.area_id = 1129 THEN 'AZUAY' -- OFICINA TÉCNICA CUENCA
            WHEN f.area_id = 1106 THEN 'GUAYAS' -- OFICINA TÉCNICA GUAYAQUIL
            WHEN f.area_id = 1251 THEN 'LOJA' -- OFICINA TÉCNICA ZAPOTILLO
            WHEN f.area_id = 1094 THEN 'ESMERALDAS' -- OFICINA TÉCNICA ESMERALDAS
            WHEN f.area_id = 1091 THEN 'MANABÍ' -- OFICINA TÉCNICA CHONE
            WHEN f.area_id = 1093 THEN 'MANABÍ' -- OFICINA TÉCNICA JIPIJAPA
            WHEN f.area_id = 1098 THEN 'ESMERALDAS' -- OFICINA TÉCNICA MUISNE
            WHEN f.area_id = 239 THEN 'MANABÍ' -- UNIDAD ENTE ACREDITADO GOBIERNO PROVINCIAL DE PICHINCHA
            WHEN f.area_id = 244 THEN 'AZUAY' -- UNIDAD ENTE ACREDITADO GOBIERNO AUTÓNOMO DESENTRALIZADO DE CUENCA
            WHEN f.area_id = 1107 THEN 'GUAYAS' -- OFICINA TÉCNICA NARANJAL
            WHEN f.area_id = 1112 THEN 'LOJA' -- OFICINA TÉCNICA PUYANGO
            WHEN f.area_id = 1097 THEN 'ESMERALDAS' -- OFICINA TÉCNICA QUININDÉ
            WHEN f.area_id = 1113 THEN 'LOJA' -- OFICINA TÉCNICA CATAMAYO
            WHEN f.area_id = 1127 THEN 'MORONA SANTIAGO' -- OFICINA TÉCNICA MORONA
            WHEN f.area_id = 1096 THEN 'ESMERALDAS' -- OFICINA TÉCNICA SAN LORENZO
            WHEN f.area_id = 1099 THEN 'SANTO DOMINGO DE LOS TSACHILAS' -- OFICINA TÉCNICA SANTO DOMINGO
            WHEN f.area_id = 1101 THEN 'PICHINCHA' -- OFICINA TÉCNICA CAYAMBE
            WHEN f.area_id = 1100 THEN 'PICHINCHA' -- OFICINA TÉCNICA SAN MIGUEL DE LOS BANCOS
            WHEN f.area_id = 1103 THEN 'PICHINCHA' -- OFICINA TÉCNICA MEJÍA
            WHEN f.area_id = 1102 THEN 'PICHINCHA' -- OFICINA TÉCNICA QUITO
            WHEN f.area_id = 1117 THEN 'CARCHI' -- OFICINA TÉCNICA TULCAN
            WHEN f.area_id = 1118 THEN 'IMBABURA' -- OFICINA TÉCNICA IBARRA
            WHEN f.area_id = 1120 THEN 'NAPO' -- OFICINA TÉCNICA TENA
            WHEN f.area_id = 1119 THEN 'ORELLANA' -- OFICINA TÉCNICA ORELLANA
            WHEN f.area_id = 1126 THEN 'PASTAZA' -- OFICINA TÉCNICA PASTAZA
            WHEN f.area_id = 1123 THEN 'TUNGURAHUA' -- OFICINA TÉCNICA AMBATO
            WHEN f.area_id = 1121 THEN 'CHIMBORAZO' -- OFICINA TÉCNICA ALAUSÍ
            WHEN f.area_id = 1130 THEN 'CAÑAR' -- OFICINA TÉCNICA AZOGUES
            WHEN f.area_id = 1122 THEN 'CHIMBORAZO' -- OFICINA TÉCNICA RIOBAMBA
            WHEN f.area_id = 1125 THEN 'COTOPAXI' -- OFICINA TÉCNICA LA MANÁ
            WHEN f.area_id = 1104 THEN 'SANTA ELENA' -- OFICINA TÉCNICA SANTA ELENA
            WHEN f.area_id = 1108 THEN 'LOS RIOS' -- OFICINA TÉCNICA BABAHOYO
            WHEN f.area_id = 1109 THEN 'LOS RIOS' -- OFICINA TÉCNICA QUEVEDO
            WHEN f.area_id = 1105 THEN 'BOLIVAR' -- OFICINA TÉCNICA GUARANDA
            WHEN f.area_id = 1116 THEN 'AZUAY' -- OFICINA TÉCNICA SANTA ISABEL
            WHEN f.area_id = 1114 THEN 'LOJA' -- OFICINA TÉCNICA MACARÁ
            WHEN f.area_id = 1110 THEN 'EL ORO' -- OFICINA TÉCNICA MACHALA
            WHEN f.area_id = 1111 THEN 'EL ORO' -- OFICINA TÉCNICA ZARUMA
            WHEN f.area_id = 1131 THEN 'CAÑAR' -- OFICINA TÉCNICA CAÑAR
            WHEN f.area_id = 1128 THEN 'MORONA SANTIAGO' -- OFICINA TÉCNICA TAISHA
            WHEN f.area_id = 1132 THEN 'SUCUMBIOS' -- OFICINA TÉCNICA LAGO AGRIO
            WHEN f.area_id = 1134 THEN 'ZAMORA CHINCHIPE' -- OFICINA TÉCNICA PALANDA
            WHEN f.area_id = 1133 THEN 'ZAMORA CHINCHIPE' -- OFICINA TÉCNICA ZAMORA
            WHEN f.area_id = 1135 THEN 'MORONA SANTIAGO' -- OFICINA TÉCNICA GUALAQUIZA
            WHEN f.area_id = 1136 THEN 'LOJA' -- OFICINA TÉCNICA LOJA

                ELSE 'N/A'
            END
        ELSE f.prov_res
    END as provincia,
    CASE 
        WHEN f.prov_res = 'N/A' THEN
            CASE 
            WHEN f.area_id = 1115 THEN 'OÑA'
            WHEN f.area_id = 1261 THEN 'QUITO'
            WHEN f.area_id = 555 THEN 'QUITO'
            WHEN f.area_id = 1080 THEN 'PORTOVIEJO'
            WHEN f.area_id = 1081 THEN 'ESMERALDAS'
            WHEN f.area_id = 178 THEN 'QUITO'
            WHEN f.area_id = 1 THEN 'ZONAS NO DELIMITADAS'
            WHEN f.area_id = 1062 THEN 'PUYANGO'
            WHEN f.area_id = 1258 THEN 'RIOBAMBA'
            WHEN f.area_id = 1257 THEN 'GUAYAQUIL'
            WHEN f.area_id = 1256 THEN 'IBARRA'
            WHEN f.area_id = 1253 THEN 'TENA'
            WHEN f.area_id = 1252 THEN 'PORTOVIEJO'
            WHEN f.area_id = 1255 THEN 'LOJA'
            WHEN f.area_id = 1254 THEN 'GUAYAQUIL'
            WHEN f.area_id = 1259 THEN 'CUENCA'
            WHEN f.area_id = 1260 THEN 'QUITO'
            WHEN f.area_id = 1082 THEN 'GUAYAQUIL'
            WHEN f.area_id = 1083 THEN 'LOJA'
            WHEN f.area_id = 1084 THEN 'IBARRA'
            WHEN f.area_id = 1085 THEN 'TENA'
            WHEN f.area_id = 1086 THEN 'RIOBAMBA'
            WHEN f.area_id = 1087 THEN 'CUENCA'
            WHEN f.area_id = 1088 THEN 'LAGO AGRIO'
            WHEN f.area_id = 1089 THEN 'CHINCHIPE'
            WHEN f.area_id = 1139 THEN 'QUITO'
            WHEN f.area_id = 1124 THEN 'LATACUNGA'
            WHEN f.area_id = 1090 THEN 'PEDERNALES'
            WHEN f.area_id = 1092 THEN 'PORTOVIEJO'
            WHEN f.area_id = 1095 THEN 'ELOY ALFARO'
            WHEN f.area_id = 1129 THEN 'CUENCA'
            WHEN f.area_id = 1106 THEN 'GUAYAQUIL'
            WHEN f.area_id = 1251 THEN 'ZAPOTILLO'
            WHEN f.area_id = 1094 THEN 'ESMERALDAS'
            WHEN f.area_id = 1091 THEN 'CHONE'
            WHEN f.area_id = 1093 THEN 'JIPIJAPA'
            WHEN f.area_id = 1098 THEN 'MUISNE'
            WHEN f.area_id = 239 THEN 'PICHINCHA'
            WHEN f.area_id = 244 THEN 'CUENCA'
            WHEN f.area_id = 1107 THEN 'NARANJAL'
            WHEN f.area_id = 1112 THEN 'PUYANGO'
            WHEN f.area_id = 1097 THEN 'QUININDE'
            WHEN f.area_id = 1113 THEN 'CATAMAYO'
            WHEN f.area_id = 1127 THEN 'MORONA'
            WHEN f.area_id = 1096 THEN 'SAN LORENZO'
            WHEN f.area_id = 1099 THEN 'SANTO DOMINGO'
            WHEN f.area_id = 1101 THEN 'CAYAMBE'
            WHEN f.area_id = 1100 THEN 'SAN MIGUEL DE LOS BANCOS'
            WHEN f.area_id = 1103 THEN 'MEJIA'
            WHEN f.area_id = 1102 THEN 'QUITO'
            WHEN f.area_id = 1117 THEN 'TULCAN'
            WHEN f.area_id = 1118 THEN 'IBARRA'
            WHEN f.area_id = 1120 THEN 'TENA'
            WHEN f.area_id = 1119 THEN 'ORELLANA'
            WHEN f.area_id = 1126 THEN 'PASTAZA'
            WHEN f.area_id = 1123 THEN 'AMBATO'
            WHEN f.area_id = 1121 THEN 'ALAUSI'
            WHEN f.area_id = 1130 THEN 'AZOGUES'
            WHEN f.area_id = 1122 THEN 'RIOBAMBA'
            WHEN f.area_id = 1125 THEN 'LA MANÁ'
            WHEN f.area_id = 1104 THEN 'SANTA ELENA'
            WHEN f.area_id = 1108 THEN 'BABAHOYO'
            WHEN f.area_id = 1109 THEN 'QUEVEDO'
            WHEN f.area_id = 1105 THEN 'GUARANDA'
            WHEN f.area_id = 1116 THEN 'SANTA ISABEL'
            WHEN f.area_id = 1114 THEN 'MACARA'
            WHEN f.area_id = 1110 THEN 'MACHALA'
            WHEN f.area_id = 1111 THEN 'ZARUMA'
            WHEN f.area_id = 1131 THEN 'CAÑAR'
            WHEN f.area_id = 1128 THEN 'TAISHA'
            WHEN f.area_id = 1132 THEN 'LAGO AGRIO'
            WHEN f.area_id = 1134 THEN 'PALANDA'
            WHEN f.area_id = 1133 THEN 'ZAMORA'
            WHEN f.area_id = 1135 THEN 'GUALAQUIZA'
            WHEN f.area_id = 1136 THEN 'LOJA'

                ELSE 'N/A'
            END
        ELSE f.cant_res
    END as canton,
    f.parr_res as parroquia,
    CASE
        WHEN f.area_status THEN 'ACTIVO'
        ELSE 'INACTIVO'
    END as estado_area
FROM final_geo f
ON CONFLICT (id_area) DO UPDATE
SET nombre_area = EXCLUDED.nombre_area,
    abreviatura_area = EXCLUDED.abreviatura_area,
    id_area_padre = EXCLUDED.id_area_padre,
    zona = EXCLUDED.zona,
    campus = EXCLUDED.campus,
    provincia = EXCLUDED.provincia,
    canton = EXCLUDED.canton,
    parroquia = EXCLUDED.parroquia,
    estado_area = EXCLUDED.estado_area,
    fecha_carga = NOW();

IF NOT EXISTS (SELECT 1 FROM dw.dim_area WHERE id_area = 0) THEN
    INSERT INTO dw.dim_area (id_area, nombre_area, estado_area, provincia, canton, parroquia)
    VALUES (0, 'AREA NO DEFINIDA', 'N/A', 'N/A', 'N/A', 'N/A');
END IF;

RAISE NOTICE 'Dimensión Areas (v1.4 Expert Normalization [75 Fallbacks]) cargada exitosamente';
END;
$$ LANGUAGE plpgsql;
