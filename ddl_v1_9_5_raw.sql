--
-- PostgreSQL database dump
--

\restrict jri35fG5TqrWxdPDt8w7rkqDhQ1pl5zd5wu05QydEh9EAY1PNsaoJIfkqpqfO3i

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: dashboard; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA dashboard;


--
-- Name: dw; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA dw;


--
-- Name: ref; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA ref;


--
-- Name: stg; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA stg;


--
-- Name: dblink; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS dblink WITH SCHEMA public;


--
-- Name: EXTENSION dblink; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION dblink IS 'connect to other PostgreSQL databases from within a database';


--
-- Name: get_waste_by_province(integer); Type: FUNCTION; Schema: dashboard; Owner: -
--

CREATE FUNCTION dashboard.get_waste_by_province(p_year integer) RETURNS TABLE(provincia text, total_generado numeric, total_entregado numeric, num_generadores bigint)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(NULLIF(TRIM(g.provincia), ''), 'No Definida') as provincia,
        SUM(f.quantity_generated) as total_generado,
        SUM(f.quantity_delivered) as total_entregado,
        COUNT(DISTINCT f.waste_generator_key) as num_generadores
    FROM dw.fact_waste_generation f
    JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
    WHERE f.record_year = p_year
    GROUP BY 1;
END;
$$;


--
-- Name: get_waste_kpi_integrated(integer, integer); Type: FUNCTION; Schema: dashboard; Owner: -
--

CREATE FUNCTION dashboard.get_waste_kpi_integrated(p_start_year integer, p_end_year integer) RETURNS TABLE(provincia text, canton text, zona_administrativa text, oficina_tecnica text, tipo_desecho text, anio integer, unidad text, total_generado numeric, total_entregado numeric, diferencia_gestion numeric, pct_entregado numeric, num_generadores bigint)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH ProyectoGeo AS (
        SELECT DISTINCT ON (v.codigo_proyecto)
            v.codigo_proyecto as cp, 
            v.provincia as pv, 
            v.canton as ct, 
            v.zona_administrativa as za, 
            v.oficina_tecnica as ot
        FROM dw.v_dashboard_regularizacion v
        ORDER BY v.codigo_proyecto, v.fecha_inicio_proceso DESC
    )
    SELECT
        COALESCE(NULLIF(TRIM(pg.pv),  ''), 'No Definida')::TEXT,
        COALESCE(NULLIF(TRIM(pg.ct),  ''), 'No Definido')::TEXT,
        COALESCE(NULLIF(TRIM(pg.za),  ''), 'N/A')::TEXT,
        COALESCE(NULLIF(TRIM(pg.ot),  ''), 'N/A')::TEXT,
        COALESCE(t.waste_name, 'Sin Clasificación')::TEXT,
        f.record_year::INTEGER,
        COALESCE(f.unit, 'u')::TEXT,
        SUM(f.quantity_generated)::NUMERIC,
        SUM(f.quantity_delivered)::NUMERIC,
        (SUM(f.quantity_generated) - SUM(f.quantity_delivered))::NUMERIC,
        ROUND(CASE WHEN SUM(f.quantity_generated) > 0 THEN (SUM(f.quantity_delivered) / SUM(f.quantity_generated)) * 100 ELSE 0 END, 2)::NUMERIC,
        COUNT(DISTINCT f.waste_generator_key)::BIGINT
    FROM dw.fact_waste_generation f
    JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN ProyectoGeo pg ON p.codigo_proyecto = pg.cp
    WHERE f.record_year BETWEEN p_start_year AND p_end_year
    GROUP BY 1, 2, 3, 4, 5, 6, 7;
END;
$$;


--
-- Name: sp_calcular_secuencia_pagos(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_calcular_secuencia_pagos() RETURNS void
    LANGUAGE plpgsql
    AS $$
            DECLARE rows_affected INTEGER;
            BEGIN 
                RAISE NOTICE 'Iniciando cálculo de secuencia por numero_tramite...';
                
                -- Calcular secuencia por tramit_number, ordenada por fecha y ID
                UPDATE dw.fact_pago fp
                SET secuencia_pago = sub.rn,
                    es_deposito_inicial = (sub.rn = 1),
                    monto_acumulado = sub.acum
                FROM (
                    SELECT id_fact_pago,
                        ROW_NUMBER() OVER (
                            PARTITION BY numero_tramite
                            ORDER BY sk_fecha_pago NULLS LAST,
                                id_fact_pago
                        ) AS rn,
                        SUM(monto_transaccion) OVER (
                            PARTITION BY numero_tramite
                            ORDER BY sk_fecha_pago NULLS LAST,
                                id_fact_pago
                        ) AS acum
                    FROM dw.fact_pago
                    WHERE numero_tramite IS NOT NULL
                ) sub
                WHERE fp.id_fact_pago = sub.id_fact_pago;
                
                GET DIAGNOSTICS rows_affected = ROW_COUNT;
                RAISE NOTICE 'Secuencias calculadas para % registros con numero_tramite.', rows_affected;
                
                -- Para pagos sin tramit_number (SUIA), marcar como depósito individual
                UPDATE dw.fact_pago
                SET secuencia_pago = 1,
                    es_deposito_inicial = true,
                    monto_acumulado = monto_transaccion
                WHERE numero_tramite IS NULL
                    AND secuencia_pago IS NULL;
                    
                GET DIAGNOSTICS rows_affected = ROW_COUNT;
                RAISE NOTICE 'Secuencias calculadas para % registros sin numero_tramite.', rows_affected;
                
                RAISE NOTICE 'Proceso completado exitosamente.';
            END;
            $$;


--
-- Name: sp_carga_dim_area(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_carga_dim_area() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN
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
$$;


--
-- Name: sp_carga_dim_pago(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_carga_dim_pago() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN -- Insertar tipos de pago desde JBPM (online_payments)
INSERT INTO dw.dim_pago (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
SELECT DISTINCT 'Online Payment',
    COALESCE(bank_code, 'N/A'),
    COALESCE(transaction_type, 'N/A'),
    'JBPM'
FROM stg.online_payments_bi
WHERE transaction_state = true ON CONFLICT (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    ) DO NOTHING;
-- Insertar tipos de pago desde SUIA (financial_transaction)
INSERT INTO dw.dim_pago (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    )
SELECT DISTINCT COALESCE(payment_type_desc, 'N/A'),
    'N/A',
    COALESCE(processname, 'N/A'),
    'SUIA_RCOA'
FROM stg.financial_transaction_bi
WHERE fitr_status = true ON CONFLICT (
        tipo_pago,
        bank_code,
        transaction_type,
        sistema_origen
    ) DO NOTHING;
RAISE NOTICE 'Dimension de pagos cargada: % registros',
(
    SELECT COUNT(1)
    FROM dw.dim_pago
);
END;
$$;


--
-- Name: sp_carga_dimensiones(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_carga_dimensiones() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN -- Dimension Tiempo (rango de 20 anios)
INSERT INTO dw.dim_tiempo (
        fecha,
        anio,
        mes,
        dia,
        trimestre,
        nombre_mes,
        dia_semana
    )
SELECT d::date,
    EXTRACT(
        YEAR
        FROM d
    ),
    EXTRACT(
        MONTH
        FROM d
    ),
    EXTRACT(
        DAY
        FROM d
    ),
    EXTRACT(
        QUARTER
        FROM d
    ),
    TO_CHAR(d, 'TMMonth'),
    TO_CHAR(d, 'TMDay')
FROM generate_series(
        '2005-01-01'::date,
        '2030-12-31'::date,
        '1 day'::interval
    ) d ON CONFLICT (fecha) DO NOTHING;
-- Dimension Proyecto
INSERT INTO dw.dim_proyecto (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        tipo_permiso_ambiental,
        tipo_sector,
        tipo_ente,
        sistema,
        estrategico
    )
SELECT DISTINCT codigo_proyecto,
    MAX(nombre_proyecto),
    MAX(resumen_proyecto),
    MAX(direccion_proyecto),
    MAX(tipo_permiso_ambiental),
    MAX(tipo_sector),
    MAX(tipo_ente),
    MAX(sistema),
    MAX(estrategico)
FROM stg.consolidado_proyectos
WHERE codigo_proyecto IS NOT NULL
GROUP BY codigo_proyecto ON CONFLICT (codigo_proyecto) DO
UPDATE
SET nombre_proyecto = EXCLUDED.nombre_proyecto,
    tipo_permiso_ambiental = EXCLUDED.tipo_permiso_ambiental,
    tipo_sector = EXCLUDED.tipo_sector;
-- Proyectos recuperados de tablas de pagos (JBPM)
INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto)
SELECT DISTINCT project_id,
    'Proyecto Recuperado (JBPM)'
FROM stg.online_payments_bi
WHERE project_id IS NOT NULL
    AND project_id != '' ON CONFLICT (codigo_proyecto) DO NOTHING;
-- Proyectos recuperados de tablas de pagos (SUIA)
INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto)
SELECT DISTINCT codigo_proyecto,
    'Proyecto Recuperado (SUIA)'
FROM stg.financial_transaction_bi
WHERE codigo_proyecto IS NOT NULL
    AND codigo_proyecto != '' ON CONFLICT (codigo_proyecto) DO NOTHING;
-- Dimension Proponente
INSERT INTO dw.dim_proponente (ced_ruc_proponente, nombre_proponente)
SELECT DISTINCT ced_ruc_proponente,
    MAX(nombre_proponente)
FROM stg.consolidado_proyectos
WHERE ced_ruc_proponente IS NOT NULL
GROUP BY ced_ruc_proponente ON CONFLICT (ced_ruc_proponente) DO
UPDATE
SET nombre_proponente = EXCLUDED.nombre_proponente;
-- Dimension Actividad
INSERT INTO dw.dim_actividad (codigo_actividad, actividad_economica)
SELECT DISTINCT codigo_actividad,
    MAX(actividad_economica)
FROM stg.consolidado_proyectos
WHERE codigo_actividad IS NOT NULL
GROUP BY codigo_actividad ON CONFLICT (codigo_actividad) DO
UPDATE
SET actividad_economica = EXCLUDED.actividad_economica;
-- Dimension Geografia
INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
SELECT DISTINCT COALESCE(provincia, 'N/A'),
    COALESCE(canton, 'N/A'),
    COALESCE(parroquia, 'N/A')
FROM stg.consolidado_proyectos ON CONFLICT (provincia, canton, parroquia) DO NOTHING;
-- Asegurar registro de Cuenca Matriz
INSERT INTO dw.dim_geografia (provincia, canton, parroquia)
VALUES ('AZUAY', 'CUENCA', 'CUENCA') ON CONFLICT (provincia, canton, parroquia) DO NOTHING;
-- Dimension Usuario
INSERT INTO dw.dim_usuario (usuario_tarea)
SELECT DISTINCT usuario_tarea
FROM stg.consolidado_proyectos
WHERE usuario_tarea IS NOT NULL ON CONFLICT (usuario_tarea) DO NOTHING;
-- Dimension Estado
INSERT INTO dw.dim_estado (estado_proceso, estado_proyecto, estado_tramite)
SELECT DISTINCT COALESCE(estado_proceso, 'N/A'),
    COALESCE(estado_proyecto, 'N/A'),
    COALESCE(estado_tramite, 'N/A')
FROM stg.consolidado_proyectos ON CONFLICT (estado_proceso, estado_proyecto, estado_tramite) DO NOTHING;
RAISE NOTICE 'Dimensiones cargadas exitosamente';
END;
$$;


--
-- Name: sp_carga_fact_pago(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_carga_fact_pago() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE row_count_a INT;
row_count_b INT;
row_count_c INT;
BEGIN -- 0. Tabla temporal de pagos unicos (Mejora performance significativamente)
CREATE TEMPORARY TABLE tmp_jbpm_unicos AS
SELECT DISTINCT ON (online_payment_id, project_id) online_payment_id,
    project_id,
    tramit_number,
    convenience_number,
    COALESCE(bank_code, 'N/A') as bank_code,
    payment_value,
    date_hour_transaction,
    COALESCE(transaction_type, 'N/A') as transaction_type
FROM stg.online_payments_bi
WHERE transaction_state = true
ORDER BY online_payment_id,
    project_id;
ANALYZE tmp_jbpm_unicos;
-- ══════════════════════════════════════════════════════════════════
-- PARTE A: Cargar pagos JBPM - Asociación DIRECTA por project_id
-- ══════════════════════════════════════════════════════════════════
INSERT INTO dw.fact_pago (
        sk_proyecto,
        sk_pago,
        sk_fecha_pago,
        monto_transaccion,
        monto_pagado,
        numero_transaccion,
        numero_tramite,
        origen,
        id_transaccion_origen
    )
SELECT dp.sk_proyecto,
    dpago.sk_pago,
    dt.sk_tiempo,
    op.payment_value,
    op.payment_value,
    op.convenience_number,
    op.tramit_number,
    'JBPM',
    'JBPM_' || op.online_payment_id::text
FROM tmp_jbpm_unicos op
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = op.bank_code
    AND dpago.transaction_type = op.transaction_type
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
GET DIAGNOSTICS row_count_a = ROW_COUNT;
RAISE NOTICE 'Parte A (Directos) completada: % filas',
row_count_a;
-- PARTE B (Removida por inconsistencia de datos: evitaba sobre-asociación por proponente)
-- ══════════════════════════════════════════════════════════════════
-- PARTE C: Cargar pagos SUIA (financial_transaction)
-- ══════════════════════════════════════════════════════════════════
INSERT INTO dw.fact_pago (
        sk_proyecto,
        sk_pago,
        sk_fecha_pago,
        monto_transaccion,
        monto_pagado,
        numero_transaccion,
        numero_tramite,
        tarea_bpm,
        proceso_bpm,
        origen,
        id_transaccion_origen
    )
SELECT DISTINCT ON (dp.sk_proyecto, ft.fitr_id) dp.sk_proyecto,
    dpago.sk_pago,
    dt.sk_tiempo,
    ft.fitr_transaction_amount,
    ft.fitr_paid_value,
    ft.fitr_transaction_number,
    NULL,
    ft.task_name,
    ft.processname,
    'SUIA_RCOA',
    'SUIA_' || ft.fitr_id::text
FROM stg.financial_transaction_bi ft
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = ft.codigo_proyecto
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = COALESCE(ft.payment_type_desc, 'N/A')
    AND dpago.bank_code = 'N/A'
    AND dpago.transaction_type = COALESCE(ft.processname, 'N/A')
    AND dpago.sistema_origen = 'SUIA_RCOA'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = ft.fitr_creation_date::date
WHERE ft.fitr_status = true ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO
UPDATE
SET monto_transaccion = EXCLUDED.monto_transaccion,
    monto_pagado = EXCLUDED.monto_pagado,
    fecha_carga = NOW();
GET DIAGNOSTICS row_count_c = ROW_COUNT;
RAISE NOTICE 'Parte C (SUIA) completada: % filas',
row_count_c;
DROP TABLE tmp_jbpm_unicos;
END;
$$;


--
-- Name: sp_carga_hechos(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_carga_hechos() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN TRUNCATE TABLE dw.fact_regularizacion;
INSERT INTO dw.fact_regularizacion (
        sk_proyecto,
        sk_proponente,
        sk_actividad,
        sk_geografia,
        sk_usuario,
        sk_estado,
        sk_fecha_registro,
        sk_area,
        interseccion_snap,
        areas_protegidas,
        superficie_proyecto,
        id_area,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        proceso,
        tarea,
        nombre_zona,
        finalizado_con_resolucion,
        numero_resolucion,
        fecha_resolucion,
        ente_acreditado,
        origen
    )
SELECT dp.sk_proyecto,
    dpp.sk_proponente,
    da.sk_actividad,
    dg.sk_geografia,
    du.sk_usuario,
    de.sk_estado,
    dt.sk_tiempo,
    COALESCE(darea.sk_area, 0),
    CASE
        WHEN snap.codigo_proyecto IS NOT NULL THEN 'SI'
        ELSE COALESCE(c.intersecta_con, 'NO')
    END,
    c.areas_protegidas,
    COALESCE(c.superficie_proyecto, 0),
    COALESCE(c.id_area, 0),
    c.fecha_inicio_proceso,
    c.fecha_fin_proceso,
    c.fecha_inicio_tarea,
    c.fecha_fin_tarea,
    c.proceso,
    c.tarea,
    c.nombre_zona,
    c.finalizado_con_resolucion,
    c.numero_resolucion,
    c.fecha_resolucion,
    c.ente_acreditado,
    c.origen
FROM stg.consolidado_proyectos c
    LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = c.codigo_proyecto
    LEFT JOIN dw.dim_proponente dpp ON dpp.ced_ruc_proponente = c.ced_ruc_proponente
    LEFT JOIN dw.dim_actividad da ON da.codigo_actividad = c.codigo_actividad
    LEFT JOIN dw.dim_geografia dg ON dg.provincia = COALESCE(c.provincia, 'N/A')
    AND dg.canton = COALESCE(c.canton, 'N/A')
    AND dg.parroquia = COALESCE(c.parroquia, 'N/A')
    LEFT JOIN dw.dim_usuario du ON du.usuario_tarea = c.usuario_tarea
    LEFT JOIN dw.dim_estado de ON de.estado_proceso = COALESCE(c.estado_proceso, 'N/A')
    AND de.estado_proyecto = COALESCE(c.estado_proyecto, 'N/A')
    AND de.estado_tramite = COALESCE(c.estado_tramite, 'N/A')
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = c.fecha_registro
    LEFT JOIN stg.jbpm_snap_variables snap ON snap.codigo_proyecto = c.codigo_proyecto
    LEFT JOIN dw.dim_area darea ON darea.id_area = c.id_area;
-- Cargar proyectos recuperados que no estan en el consolidado
INSERT INTO dw.fact_regularizacion (
        sk_proyecto,
        sk_proponente,
        sk_geografia,
        sk_actividad,
        sk_fecha_registro,
        sk_area,
        origen
    )
SELECT dp.sk_proyecto,
    0,
    0,
    0,
    0,
    0,
    'RECUPERADO'
FROM dw.dim_proyecto dp
WHERE NOT EXISTS (
        SELECT 1
        FROM dw.fact_regularizacion fr
        WHERE fr.sk_proyecto = dp.sk_proyecto
    );
RAISE NOTICE 'Fact table cargada: % filas',
(
    SELECT COUNT(1)
    FROM dw.fact_regularizacion
);
END;
$$;


--
-- Name: sp_carga_proyecto_geografia(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_carga_proyecto_geografia() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN -- Truncar y recargar
    TRUNCATE TABLE dw.fact_proyecto_geografia;
-- Insertar todas las combinaciones únicas proyecto ↔ geografía
INSERT INTO dw.fact_proyecto_geografia (sk_proyecto, sk_geografia, es_principal)
SELECT DISTINCT f.sk_proyecto,
    f.sk_geografia,
    false -- Se marca como principal abajo
FROM dw.fact_regularizacion f
WHERE f.sk_geografia IS NOT NULL ON CONFLICT (sk_proyecto, sk_geografia) DO NOTHING;
-- Marcar la primera ubicación (por orden de tarea más reciente) como principal
-- Esto replica el criterio de DISTINCT ON usado en las consultas actuales
UPDATE dw.fact_proyecto_geografia fpg
SET es_principal = true
FROM (
        SELECT DISTINCT ON (f.sk_proyecto) f.sk_proyecto,
            f.sk_geografia
        FROM dw.fact_regularizacion f
        WHERE f.sk_geografia IS NOT NULL
        ORDER BY f.sk_proyecto,
            f.fecha_fin_tarea DESC NULLS LAST
    ) ppal
WHERE fpg.sk_proyecto = ppal.sk_proyecto
    AND fpg.sk_geografia = ppal.sk_geografia;
RAISE NOTICE 'Bridge proyecto-geografia: % registros (% proyectos)',
(
    SELECT COUNT(1)
    FROM dw.fact_proyecto_geografia
),
(
    SELECT COUNT(DISTINCT sk_proyecto)
    FROM dw.fact_proyecto_geografia
);
END;
$$;


--
-- Name: sp_carga_puente_ambiental(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_carga_puente_ambiental() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN -- Limpieza previa para carga total
    TRUNCATE TABLE dw.bridge_interseccion_ambiental;
INSERT INTO dw.bridge_interseccion_ambiental (sk_proyecto, sk_capa, detalle_interseccion) WITH split_layers AS (
        SELECT dp.sk_proyecto,
            -- Extraer Nombre de Capa (ej: SNAP) y Detalle (ej: Yasuní)
            TRIM(SPLIT_PART(s.layer_segment, '|', 1)) as layer_name,
            TRIM(SPLIT_PART(s.layer_segment, '|', 2)) as area_detail
        FROM stg.consolidado_proyectos cp
            JOIN dw.dim_proyecto dp ON cp.codigo_proyecto = dp.codigo_proyecto
            CROSS JOIN LATERAL unnest(string_to_array(cp.areas_protegidas, ' ; ')) as s(layer_segment)
        WHERE cp.areas_protegidas IS NOT NULL
            AND cp.areas_protegidas <> ''
    )
SELECT sl.sk_proyecto,
    COALESCE(da.sk_capa, 0) as sk_capa,
    COALESCE(sl.area_detail, 'N/A') as area_detail
FROM split_layers sl
    LEFT JOIN dw.dim_capa_ambiental da ON UPPER(TRIM(sl.layer_name)) = UPPER(TRIM(da.nombre_capa))
WHERE sl.layer_name <> '' ON CONFLICT (sk_proyecto, sk_capa, detalle_interseccion) DO NOTHING;
RAISE NOTICE 'Tabla puente de biodiversidad cargada exitosamente.';
END;
$$;


--
-- Name: sp_consolidar_staging(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_consolidar_staging() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN TRUNCATE TABLE stg.consolidado_proyectos;
-- RCOA
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        nombre_zona,
        finalizado_con_resolucion,
        numero_resolucion,
        fecha_resolucion,
        ente_acreditado,
        estado_tramite,
        id_area,
        superficie_proyecto,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    nombre_zona,
    finalizado_con_resolucion,
    numero_resolucion,
    fecha_resolucion,
    '',
    estado_tramite,
    id_area,
    superficie_proyecto,
    '',
    origen
FROM stg.suia_rcoa_bi;
-- COA
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        nombre_zona,
        finalizado_con_resolucion,
        numero_resolucion,
        fecha_resolucion,
        ente_acreditado,
        estado_tramite,
        id_area,
        superficie_proyecto,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    nombre_zona,
    finalizado_con_resolucion,
    numero_resolucion,
    fecha_resolucion,
    '',
    estado_tramite,
    id_area,
    superficie_proyecto,
    '',
    origen
FROM stg.suia_coa_bi;
-- JBPM SECTOR
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        ente_acreditado,
        estado_tramite,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    ente_acreditado,
    estado_tramite,
    estrategico,
    origen
FROM stg.jbpm_sector_bi;
-- JBPM 4 CATEGORIAS
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        areas_protegidas,
        sistema,
        ente_acreditado,
        estado_tramite,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    areas_protegidas,
    sistema,
    ente_acreditado,
    estado_tramite,
    estrategico,
    origen
FROM stg.jbpm_4cat_bi;
-- JBPM HIDROCARBUROS
INSERT INTO stg.consolidado_proyectos (
        codigo_proyecto,
        nombre_proyecto,
        resumen_proyecto,
        direccion_proyecto,
        fecha_registro,
        codigo_actividad,
        actividad_economica,
        ced_ruc_proponente,
        nombre_proponente,
        area_responsable_proyecto,
        tipo_sector,
        tipo_permiso_ambiental,
        tipo_ente,
        provincia,
        canton,
        parroquia,
        proceso,
        estado_proceso,
        fecha_inicio_proceso,
        fecha_fin_proceso,
        tarea,
        estado_tarea,
        fecha_inicio_tarea,
        fecha_fin_tarea,
        usuario_tarea,
        estado_proyecto,
        intersecta_con,
        ente_acreditado,
        estado_tramite,
        id_area,
        estrategico,
        origen
    )
SELECT codigo_proyecto,
    nombre_proyecto,
    resumen_proyecto,
    direccion_proyecto,
    fecha_registro,
    codigo_actividad,
    actividad_economica,
    ced_ruc_proponente,
    nombre_proponente,
    area_responsable_proyecto,
    tipo_sector,
    tipo_permiso_ambiental,
    tipo_ente,
    provincia,
    canton,
    parroquia,
    proceso,
    estado_proceso,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    tarea,
    estado_tarea,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    usuario_tarea,
    estado_proyecto,
    intersecta_con,
    ente_acreditado,
    estado_tramite,
    id_area,
    estrategico,
    origen
FROM stg.jbpm_hidro_bi;
RAISE NOTICE 'Consolidado STG completado: % filas',
(
    SELECT COUNT(1)
    FROM stg.consolidado_proyectos
);
END;
$$;


--
-- Name: sp_etl_chemical_all(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_etl_chemical_all() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    v_start_time TIMESTAMP := NOW();
    v_log_id INTEGER;
    v_pre_count_imp INTEGER;
    v_post_count_imp INTEGER;
BEGIN
    -- 1. Initialize Log
    RAISE NOTICE 'Initializing Log...';
    INSERT INTO dw.etl_process_log (process_name, execution_mode, status, start_time)
    VALUES ('Chemical ETL', 'FULL', 'RUNNING', v_start_time)
    RETURNING id INTO v_log_id;
    RAISE NOTICE 'Log ID created: %', v_log_id;

    -- 2. Dimensional Integrity (Key 0)
    RAISE NOTICE 'Setting Dimensional Integrity...';
    INSERT INTO dw.dim_chemical_substance (chemical_key, chemical_id, substance_name)
    VALUES (0, -1, 'N/A') ON CONFLICT (chemical_key) DO NOTHING;

    INSERT INTO dw.dim_chemical_importer (importer_key, importer_id, importer_name)
    VALUES (0, -1, 'N/A') ON CONFLICT (importer_key) DO NOTHING;

    -- 3. Sync Virtual Projects from Chemical Registrations (Tier 3)
    RAISE NOTICE 'Syncing Virtual Projects...';
    INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto, sistema)
    SELECT DISTINCT 
        COALESCE(chsr_code, 'REG-CHSR-' || chsr_id), 
        'REGISTRO SUSTANCIA: ' || COALESCE(chsr_code, 'ID ' || chsr_id), 
        'COA_IMPORT_REG'
    FROM stg.stg_chemical_sustances_records
    ON CONFLICT (codigo_proyecto) DO NOTHING;

    -- 4. Optimized Project Mapping Cache
    RAISE NOTICE 'Building Optimized Mapping Cache...';
    
    -- 4.1 Tier 1: Direct Mapping Lookup
    CREATE TEMP TABLE tmp_t1_lookup AS
    WITH target_suffixes AS (
        SELECT DISTINCT RIGHT(m.prco_cua, 11) as suffix
        FROM stg.stg_chemical_sustances_records r
        JOIN stg.stg_project_mapping m ON r.prco_id = m.prco_id
        WHERE m.prco_cua IS NOT NULL
    )
    SELECT DISTINCT ON (RIGHT(codigo_proyecto, 11))
        RIGHT(codigo_proyecto, 11) as suffix,
        sk_proyecto
    FROM dw.dim_proyecto
    WHERE RIGHT(codigo_proyecto, 11) IN (SELECT suffix FROM target_suffixes)
    ORDER BY RIGHT(codigo_proyecto, 11), sk_proyecto DESC;

    -- 4.2 Tier 2: RUC Mapping Lookup
    CREATE TEMP TABLE tmp_t2_lookup AS
    SELECT DISTINCT ON (dp2.ced_ruc_proponente)
        dp2.ced_ruc_proponente as ruc,
        fr.sk_proyecto
    FROM dw.fact_regularizacion fr
    JOIN dw.dim_proponente dp2 ON fr.sk_proponente = dp2.sk_proponente
    WHERE dp2.ced_ruc_proponente IN (SELECT DISTINCT chsr_identification_rep_legal FROM stg.stg_chemical_sustances_records)
    ORDER BY dp2.ced_ruc_proponente, fr.sk_proyecto DESC;

    -- 4.3 Final Mapping Assemble
    CREATE TEMP TABLE tmp_chemical_project_map AS
    SELECT 
        r.chsr_id,
        COALESCE(
            t1.sk_proyecto, -- Tier 1
            t2.sk_proyecto, -- Tier 2
            dp_v.sk_proyecto, -- Tier 3: Virtual
            0 -- N/A
        ) as resolved_sk_proyecto
    FROM stg.stg_chemical_sustances_records r
    LEFT JOIN stg.stg_project_mapping m ON r.prco_id = m.prco_id
    LEFT JOIN tmp_t1_lookup t1 ON RIGHT(m.prco_cua, 11) = t1.suffix
    LEFT JOIN tmp_t2_lookup t2 ON r.chsr_identification_rep_legal = t2.ruc
    LEFT JOIN dw.dim_proyecto dp_v ON dp_v.codigo_proyecto = COALESCE(r.chsr_code, 'REG-CHSR-' || r.chsr_id);

    CREATE INDEX idx_tmp_chsr ON tmp_chemical_project_map(chsr_id);
    DROP TABLE tmp_t1_lookup;
    DROP TABLE tmp_t2_lookup;

    -- 5. Sync Dimensions (Importadores)
    INSERT INTO dw.dim_chemical_importer (importer_id, importer_name, identification, registration_code)
    SELECT DISTINCT 
        chsr_id, chsr_name_rep_legal, chsr_identification_rep_legal, chsr_substance_registration
    FROM stg.stg_chemical_sustances_records
    ON CONFLICT (importer_id) DO UPDATE SET
        importer_name = EXCLUDED.importer_name,
        identification = EXCLUDED.identification,
        registration_code = EXCLUDED.registration_code,
        date_update = NOW();

    -- 6. LOAD FACT_CHEMICAL_IMPORT
    WITH import_data AS (
        SELECT 
            COALESCE(tpm.resolved_sk_proyecto, 0) as sk_proyecto,
            COALESCE((SELECT chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = ir.dach_id ORDER BY chemical_key DESC LIMIT 1), 0) as chemical_key,
            COALESCE((SELECT importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = ir.chsr_id ORDER BY importer_key DESC LIMIT 1), 0) as importer_key,
            COALESCE((SELECT sk_tiempo FROM dw.dim_tiempo dt WHERE dt.fecha = CAST(ir.inre_begin_authorization_date AS DATE) LIMIT 1), 0) as sk_tiempo,
            COALESCE((SELECT sk_geografia FROM dw.dim_geografia dg WHERE dg.sk_geografia = dr.gelo_id LIMIT 1), 0) as geo_location_key,
            COALESCE(ir.inre_document_autorizes, 'REQ-' || ir.inre_id) as document_number,
            ir.inre_processing_code,
            ir.inre_authorization,
            dr.deir_available_space, dr.deir_net_weight, dr.deir_gross_weight
        FROM stg.stg_import_request ir
        JOIN stg.stg_detail_import_request dr ON ir.inre_id = dr.inre_id
        LEFT JOIN tmp_chemical_project_map tpm ON ir.chsr_id = tpm.chsr_id
    )
    INSERT INTO dw.fact_chemical_import (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
        quantity_authorized, net_weight, gross_weight, import_status, 
        processing_code, document_number, source_system
    )
    SELECT 
        sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
        SUM(deir_available_space), SUM(deir_net_weight), SUM(deir_gross_weight),
        MAX(CASE WHEN inre_authorization THEN 'AUTORIZADO' ELSE 'PENDIENTE' END),
        MAX(inre_processing_code), document_number, 'COA_IMPORT'
    FROM import_data
    GROUP BY sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key, document_number
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number) 
    DO UPDATE SET
        quantity_authorized = EXCLUDED.quantity_authorized,
        net_weight = EXCLUDED.net_weight,
        gross_weight = EXCLUDED.gross_weight;

    -- 7. LOAD FACT_CHEMICAL_MOVEMENT
    DROP TABLE IF EXISTS tmp_movement_pre;
    CREATE TEMP TABLE tmp_movement_pre AS
    WITH movement_data AS (
        SELECT 
            COALESCE(tpm.resolved_sk_proyecto, 0) as sk_proyecto,
            COALESCE((SELECT ds.chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = m.geca_id ORDER BY chemical_key DESC LIMIT 1), 0) as chemical_key,
            COALESCE((SELECT di.importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = d.chsr_id ORDER BY importer_key DESC LIMIT 1), 0) as importer_key,
            0 as sk_tiempo,
            COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id) as invoice_number,
            m.chsm_entry, m.chsm_exit, m.chsm_operator
        FROM stg.stg_chemical_substances_movements m
        JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
        LEFT JOIN tmp_chemical_project_map tpm ON d.chsr_id = tpm.chsr_id
    )
    SELECT 
        sk_proyecto, chemical_key, importer_key, sk_tiempo, 
        SUM(chsm_entry) as q_entry, SUM(chsm_exit) as q_exit, invoice_number, MAX(chsm_operator) as operator
    FROM movement_data
    GROUP BY sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number;

    -- Diagnostic: Check for duplicates in the aggregated set
    IF (SELECT count(*) FROM (SELECT 1 FROM tmp_movement_pre GROUP BY sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number HAVING count(*) > 1) s) > 0 THEN
        RAISE EXCEPTION 'Internal Collision: Aggregated Movements are NOT unique for the Target Key!';
    END IF;

    INSERT INTO dw.fact_chemical_movement (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, 
        quantity_entry, quantity_exit, invoice_number, operator_name
    )
    SELECT * FROM tmp_movement_pre
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number)
    DO UPDATE SET
        quantity_entry = EXCLUDED.quantity_entry,
        quantity_exit = EXCLUDED.quantity_exit,
        operator_name = EXCLUDED.operator_name;

    -- 8. LOAD FACT_CHEMICAL_DECLARATION
    RAISE NOTICE 'Loading Detailed Declarations...';
    INSERT INTO dw.fact_chemical_declaration (
        sk_proyecto, importer_key, sk_tiempo, 
        initial_quantity, final_quantity, is_on_time, 
        declaration_year, declaration_month
    )
    SELECT 
        COALESCE(tpm.resolved_sk_proyecto, 0) as sk_proyecto,
        COALESCE(di.importer_key, 0) as importer_key,
        COALESCE(dt.sk_tiempo, 0) as sk_tiempo,
        SUM(d.chsd_starting_amount), SUM(d.chsd_end_quantity), 
        BOOL_OR(COALESCE(d.chsd_declaration_on_time::boolean, false)),
        d.chsd_year, d.chsd_month
    FROM stg.stg_chemical_substances_declaration d
    LEFT JOIN tmp_chemical_project_map tpm ON d.chsr_id = tpm.chsr_id
    LEFT JOIN dw.dim_chemical_importer di ON di.importer_id = d.chsr_id
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = CAST(CONCAT(d.chsd_year, '-', d.chsd_month, '-01') AS DATE)
    GROUP BY 1, 2, 3, 7, 8
    ON CONFLICT (sk_proyecto, importer_key, sk_tiempo, declaration_year, declaration_month)
    DO UPDATE SET
        initial_quantity = EXCLUDED.initial_quantity,
        final_quantity = EXCLUDED.final_quantity,
        is_on_time = EXCLUDED.is_on_time;

    -- 9. LOAD FACT_CHEMICAL_APPLICATION (Pesticides)
    INSERT INTO dw.fact_chemical_application (
        sk_proyecto, chemical_key, sk_tiempo, dose, dose_unit, usage_year
    )
    SELECT 
        COALESCE(dp.sk_proyecto, 0),
        COALESCE(ds.chemical_key, 0),
        COALESCE(dt.sk_tiempo, 0),
        1, 'REGISTRO', EXTRACT(YEAR FROM NOW())
    FROM stg.stg_detail_pesticide_project dpp
    JOIN stg.stg_pesticide_project pp ON dpp.chpe_id = pp.chpe_id
    LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = pp.chpe_proyect_code
    LEFT JOIN dw.dim_chemical_substance ds ON ds.chemical_id = dpp.pqa_id
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = CURRENT_DATE;

    DROP TABLE tmp_chemical_project_map;

    -- 10. Metrics & Completion
    SELECT COUNT(*) INTO v_post_count_imp FROM dw.fact_chemical_import;
    
    UPDATE dw.etl_process_log 
    SET end_time = NOW(), status = 'SUCCESS', rows_inserted = (v_post_count_imp - v_pre_count_imp)
    WHERE id = v_log_id;

EXCEPTION WHEN OTHERS THEN
    DECLARE
        v_msg TEXT;
        v_detail TEXT;
        v_hint TEXT;
        v_context TEXT;
    BEGIN
        GET STACKED DIAGNOSTICS 
            v_msg = MESSAGE_TEXT,
            v_detail = PG_EXCEPTION_DETAIL,
            v_hint = PG_EXCEPTION_HINT,
            v_context = PG_EXCEPTION_CONTEXT;
            
        IF v_log_id IS NOT NULL THEN
            UPDATE dw.etl_process_log 
            SET end_time = NOW(), 
                status = 'ERROR', 
                error_message = v_msg || ' | ' || v_context
            WHERE id = v_log_id;
        END IF;
    END;
    RAISE;
END;
$$;


--
-- Name: sp_etl_chemical_test(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_etl_chemical_test() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- 1. Create Project Mapping Cache
    DROP TABLE IF EXISTS tmp_chemical_project_map;
    CREATE TEMP TABLE tmp_chemical_project_map AS
    WITH base AS (
        SELECT 
            r.chsr_id,
            COALESCE(m.prco_cua, 'N/A') as direct_cua,
            r.chsr_identification_rep_legal as ruc,
            r.chsr_code
        FROM stg.stg_chemical_sustances_records r
        LEFT JOIN stg.stg_project_mapping m ON m.prco_id = r.prco_id
    )
    SELECT 
        b.chsr_id,
        COALESCE(
            (SELECT dp1.sk_proyecto FROM dw.dim_proyecto dp1 
             WHERE RIGHT(dp1.codigo_proyecto, 11) = RIGHT(b.direct_cua, 11) 
             ORDER BY dp1.sk_proyecto DESC LIMIT 1),
            (SELECT fr.sk_proyecto FROM dw.fact_regularizacion fr
             JOIN dw.dim_proponente dp2 ON fr.sk_proponente = dp2.sk_proponente
             WHERE dp2.ced_ruc_proponente = b.ruc 
             ORDER BY fr.sk_proyecto DESC LIMIT 1),
            (SELECT dp3.sk_proyecto FROM dw.dim_proyecto dp3 
             WHERE dp3.codigo_proyecto = COALESCE(b.chsr_code, 'REG-CHSR-' || b.chsr_id) 
             LIMIT 1),
            0
        ) as resolved_sk_proyecto
    FROM base b;

    -- 2. Fact Import
    INSERT INTO dw.fact_chemical_import (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
        quantity_authorized, net_weight, gross_weight, import_status, 
        processing_code, document_number, source_system
    )
    SELECT 
        COALESCE(tpm.resolved_sk_proyecto, 0),
        COALESCE((SELECT ds.chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = ir.dach_id ORDER BY chemical_key DESC LIMIT 1), 0),
        COALESCE((SELECT di.importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = ir.chsr_id ORDER BY importer_key DESC LIMIT 1), 0),
        0, -- Time 0
        COALESCE((SELECT sk_geografia FROM dw.dim_geografia dg WHERE dg.sk_geografia = dr.gelo_id LIMIT 1), 0),
        SUM(dr.deir_available_space), SUM(dr.deir_net_weight), SUM(dr.deir_gross_weight),
        MAX(CASE WHEN ir.inre_authorization THEN 'AUTORIZADO' ELSE 'PENDIENTE' END),
        ir.inre_processing_code, 
        COALESCE(ir.inre_document_autorizes, 'REQ-' || ir.inre_id), 
        'COA_IMPORT'
    FROM stg.stg_import_request ir
    JOIN stg.stg_detail_import_request dr ON ir.inre_id = dr.inre_id
    LEFT JOIN tmp_chemical_project_map tpm ON ir.chsr_id = tpm.chsr_id
    GROUP BY 1, 2, 3, 4, 5, 10, 11, 12
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number) 
    DO UPDATE SET
        quantity_authorized = EXCLUDED.quantity_authorized,
        net_weight = EXCLUDED.net_weight,
        gross_weight = EXCLUDED.gross_weight;

    -- 3. Fact Movement
    INSERT INTO dw.fact_chemical_movement (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, 
        quantity_entry, quantity_exit, invoice_number, operator_name
    )
    SELECT 
        COALESCE(tpm.resolved_sk_proyecto, 0),
        COALESCE((SELECT ds.chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = m.achs_id ORDER BY chemical_key DESC LIMIT 1), 0),
        COALESCE((SELECT di.importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = d.chsr_id ORDER BY importer_key DESC LIMIT 1), 0),
        0,
        SUM(m.chsm_entry), SUM(m.chsm_exit), 
        COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id), 
        MAX(m.chsm_operator)
    FROM stg.stg_chemical_substances_movements m
    JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
    LEFT JOIN tmp_chemical_project_map tpm ON d.chsr_id = tpm.chsr_id
    GROUP BY 1, 2, 3, 4, 7
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number)
    DO UPDATE SET
        quantity_entry = EXCLUDED.quantity_entry,
        quantity_exit = EXCLUDED.quantity_exit;

END;
$$;


--
-- Name: sp_etl_waste_chemical(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_etl_waste_chemical() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    v_start_time TIMESTAMP := NOW();
    v_log_id INTEGER;
    v_pre_count INTEGER;
    v_post_count INTEGER;
BEGIN
    -- 1. Initialize Log
    INSERT INTO dw.etl_process_log (process_name, execution_mode, status, start_time)
    VALUES ('Waste Chemical ETL', 'PROCEDURE_V2', 'RUNNING', v_start_time);
    
    v_log_id := lastval();

    -- 2. Pre-counts
    SELECT COUNT(*) INTO v_pre_count FROM dw.fact_waste_generation;

    -- 3. Dimension Defaults (N/A)
    INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
    SELECT 0, 'N/A', 'SIN DEFINIR (HUÉRFANO)'
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_proyecto WHERE sk_proyecto = 0)
    ON CONFLICT DO NOTHING;

    INSERT INTO dw.dim_geografia (sk_geografia, provincia, canton, parroquia)
    SELECT 0, 'N/A', 'N/A', 'SIN DEFINIR'
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_geografia WHERE sk_geografia = 0)
    ON CONFLICT DO NOTHING;

    INSERT INTO dw.dim_waste_type (waste_type_key, cawa_id, waste_name)
    SELECT 0, 0, 'SIN DEFINIR'
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_waste_type WHERE waste_type_key = 0)
    ON CONFLICT DO NOTHING;

    INSERT INTO dw.dim_dangerous_waste (dangerous_waste_key, dw_id, description)
    SELECT 0, 0, 'N/A'
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_dangerous_waste WHERE dangerous_waste_key = 0)
    ON CONFLICT DO NOTHING;

    INSERT INTO dw.dim_dangerous_classification (danger_class_key, class_id, description)
    SELECT 0, 0, 'N/A'
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_dangerous_classification WHERE danger_class_key = 0)
    ON CONFLICT DO NOTHING;

    -- 4. Generator Dimension Sync
    INSERT INTO dw.dim_waste_generator (
        waste_generator_id, generator_name, generator_type, ruc_generator, province, canton, 
        date_add, date_update, effective_from, is_current
    )
    SELECT 
        waste_generator_id, 
        LEFT(generator_name, 500),
        LEFT(generator_type, 200),
        ruc_generator, 
        LEFT(province, 100), 
        LEFT(canton, 100), 
        date_add, date_update, CURRENT_TIMESTAMP, TRUE
    FROM (SELECT DISTINCT ON (waste_generator_id) * FROM stg.stg_waste_generator ORDER BY waste_generator_id, date_update DESC NULLS LAST) s
    ON CONFLICT (waste_generator_id) DO UPDATE SET 
        generator_name = EXCLUDED.generator_name,
        generator_type = EXCLUDED.generator_type,
        ruc_generator = EXCLUDED.ruc_generator,
        province = EXCLUDED.province,
        canton = EXCLUDED.canton,
        date_update = EXCLUDED.date_update;

    -- 5. Fact Transformation (Step 1: Resolver & Deduplicate to TMP)
    DROP TABLE IF EXISTS stg.tmp_final_waste_batch;
    CREATE TABLE stg.tmp_final_waste_batch AS
    WITH resolved_stg AS (
        SELECT 
            stg.*,
            COALESCE(
                pm.prco_cua,
                CASE WHEN stg.source_system = 'COA' THEN stg.project_code ELSE 'SN-PROY' END
            ) as final_project_code
        FROM stg.stg_fact_waste_generation stg
        LEFT JOIN stg.stg_project_mapping pm ON (stg.source_system = 'RCOA' AND stg.lp_prco_id = pm.prco_id)
    )
    SELECT DISTINCT ON (COALESCE(dp.sk_proyecto, 0), dwg.waste_generator_key, dt.sk_tiempo, COALESCE(dwt.waste_type_key, 0))
        COALESCE(dp.sk_proyecto, 0) as sk_proyecto,
        dwg.waste_generator_key,
        dt.sk_tiempo,
        COALESCE(dwt.waste_type_key, 0) as waste_type_key,
        COALESCE(ddw.dangerous_waste_key, 0) as dangerous_waste_key,
        COALESCE(ddc.danger_class_key, 0) as danger_class_key,
        COALESCE(dp.sk_geografia, 0) as geo_location_key,
        LEAST(COALESCE(stg.quantity_generated, 0), 999999999999.999) as q_gen,
        LEAST(COALESCE(stg.quantity_delivered, 0), 999999999999.999) as q_del,
        LEAST(COALESCE(stg.quantity_stored, 0), 999999999999.999) as q_sto,
        LEFT(stg.unit, 50) as unit, 
        stg.record_year::int as ryear,
        stg.source_system as ssys
    FROM resolved_stg stg
    LEFT JOIN stg.tmp_dim_proyecto_optimized dp ON dp.codigo_proyecto = stg.final_project_code
    JOIN dw.dim_waste_generator dwg ON dwg.waste_generator_id = stg.waste_generator_id
    JOIN dw.dim_tiempo dt ON dt.fecha = DATE(stg.date_generated)
    LEFT JOIN dw.dim_waste_type dwt ON dwt.cawa_id = stg.waste_type_id::int
    LEFT JOIN dw.dim_dangerous_waste ddw ON ddw.dw_id = stg.dangerous_waste_id::int
    LEFT JOIN dw.dim_dangerous_classification ddc ON ddc.class_id = stg.danger_class_id::int
    ORDER BY 1,2,3,4, stg.record_year DESC;

    -- 6. Fact Transformation (Step 2: UPSERT from TMP)
    INSERT INTO dw.fact_waste_generation (
        sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key, dangerous_waste_key, 
        danger_class_key, geo_location_key, quantity_generated, quantity_delivered, 
        quantity_stored, unit, record_year, source_system
    )
    SELECT * FROM stg.tmp_final_waste_batch
    ON CONFLICT (sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key) 
    DO UPDATE SET
        quantity_generated = EXCLUDED.quantity_generated,
        quantity_delivered = EXCLUDED.quantity_delivered,
        quantity_stored = EXCLUDED.quantity_stored,
        unit = EXCLUDED.unit,
        record_year = EXCLUDED.record_year,
        source_system = EXCLUDED.source_system;

    -- 7. Finalization Metrics
    SELECT COUNT(*) INTO v_post_count FROM dw.fact_waste_generation;
    
    UPDATE dw.etl_process_log 
    SET end_time = NOW(), status = 'SUCCESS', rows_inserted = (v_post_count - v_pre_count)
    WHERE id = v_log_id;

    DROP TABLE IF EXISTS stg.tmp_final_waste_batch;

EXCEPTION WHEN OTHERS THEN
    IF v_log_id IS NOT NULL THEN
        UPDATE dw.etl_process_log 
        SET end_time = NOW(), status = 'ERROR', error_message = SQLERRM
        WHERE id = v_log_id;
    END IF;
    RAISE;
END;
$$;


--
-- Name: sp_orquestar_extraccion_remota(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_orquestar_extraccion_remota() RETURNS void
    LANGUAGE plpgsql
    AS $$ BEGIN -- 1. Disparar extracción SUIA III (v1.4.1)
    PERFORM *
FROM dblink(
        'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
        'SELECT 1 FROM suia_iii.sp_coa_bi_v1_4_1()'
    ) AS t(ret integer);
-- 2. Disparar extracción COA MAE (v1.4.1)
PERFORM *
FROM dblink(
        'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
        'SELECT 1 FROM coa_mae.sp_rcoa_bi_v1_4_1()'
    ) AS t(ret integer);
RAISE NOTICE 'Extracciones remotas v1.4.1 disparadas exitosamente.';
END;
$$;


--
-- Name: sp_test_etapa(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.sp_test_etapa() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE row_count_a INT;
row_count_b INT;
BEGIN RAISE NOTICE 'Iniciando PRUEBA ETAPA...';
CREATE TEMP TABLE tmp_jbpm_unicos ON COMMIT DROP AS
SELECT DISTINCT ON (online_payment_id, project_id) online_payment_id,
    project_id,
    tramit_number,
    convenience_number,
    COALESCE(bank_code, 'N/A') as bank_code,
    payment_value,
    date_hour_transaction,
    COALESCE(transaction_type, 'N/A') as transaction_type
FROM stg.online_payments_bi
WHERE transaction_state = true
ORDER BY online_payment_id,
    project_id;
-- PARTE A: Solo para proyectos de ETAPA en staging
INSERT INTO dw.fact_pago (
        sk_proyecto,
        sk_pago,
        sk_fecha_pago,
        monto_transaccion,
        monto_pagado,
        numero_transaccion,
        numero_tramite,
        origen,
        id_transaccion_origen
    )
SELECT dp.sk_proyecto,
    dpago.sk_pago,
    dt.sk_tiempo,
    op.payment_value,
    op.payment_value,
    op.convenience_number,
    op.tramit_number,
    'JBPM',
    'JBPM_' || op.online_payment_id::text
FROM tmp_jbpm_unicos op
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
    INNER JOIN dw.fact_regularizacion fr ON fr.sk_proyecto = dp.sk_proyecto
    INNER JOIN dw.dim_pago dpago ON dpago.tipo_pago = 'Online Payment'
    AND dpago.bank_code = op.bank_code
    AND dpago.transaction_type = op.transaction_type
    AND dpago.sistema_origen = 'JBPM'
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
WHERE fr.sk_proponente = 6385 ON CONFLICT DO NOTHING;
GET DIAGNOSTICS row_count_a = ROW_COUNT;
RAISE NOTICE 'Prueba A (ETAPA Directo): % filas',
row_count_a;
-- PARTE B: ReplicaciÃ³n solo ETAPA
INSERT INTO dw.fact_pago (
        sk_proyecto,
        sk_pago,
        sk_fecha_pago,
        monto_transaccion,
        monto_pagado,
        numero_transaccion,
        numero_tramite,
        origen,
        id_transaccion_origen
    ) WITH payment_owners AS (
        SELECT DISTINCT ON (op.online_payment_id) fr.sk_proponente,
            op.online_payment_id,
            op.project_id as orig_project_id,
            dpago.sk_pago,
            dt.sk_tiempo,
            op.payment_value,
            op.convenience_number,
            op.tramit_number
        FROM tmp_jbpm_unicos op
            INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = op.project_id
            INNER JOIN dw.fact_regularizacion fr ON fr.sk_proyecto = dp.sk_proyecto
            INNER JOIN dw.dim_pago dpago ON dpago.sk_pago = (
                SELECT sk_pago
                FROM dw.dim_pago
                WHERE tipo_pago = 'Online Payment'
                    AND bank_code = op.bank_code
                    AND transaction_type = op.transaction_type
                    AND sistema_origen = 'JBPM'
                LIMIT 1
            )
            LEFT JOIN dw.dim_tiempo dt ON dt.fecha = op.date_hour_transaction::date
        WHERE fr.sk_proponente = 6385
    )
SELECT fr_all.sk_proyecto,
    po.sk_pago,
    po.sk_tiempo,
    po.payment_value,
    po.payment_value,
    po.convenience_number,
    po.tramit_number,
    'JBPM',
    'JBPM_' || po.online_payment_id::text
FROM payment_owners po
    INNER JOIN dw.fact_regularizacion fr_all ON fr_all.sk_proponente = po.sk_proponente
    INNER JOIN dw.dim_proyecto dp_all ON dp_all.sk_proyecto = fr_all.sk_proyecto
WHERE dp_all.codigo_proyecto != po.orig_project_id ON CONFLICT (sk_proyecto, id_transaccion_origen, origen) DO NOTHING;
GET DIAGNOSTICS row_count_b = ROW_COUNT;
RAISE NOTICE 'Prueba B (ETAPA Indirecto): % filas',
row_count_b;
END;
$$;


--
-- Name: test_func(); Type: FUNCTION; Schema: dw; Owner: -
--

CREATE FUNCTION dw.test_func() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE 
    v_id INTEGER;
BEGIN
    INSERT INTO dw.etl_process_log (process_name, status)
    VALUES ('test', 'success')
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_logs; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.audit_logs (
    log_id integer NOT NULL,
    user_id integer,
    action character varying(255) NOT NULL,
    module character varying(100),
    details jsonb,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ip_address character varying(45)
);


--
-- Name: audit_logs_log_id_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.audit_logs_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.audit_logs_log_id_seq OWNED BY dw.audit_logs.log_id;


--
-- Name: bridge_interseccion_ambiental; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.bridge_interseccion_ambiental (
    sk_proyecto integer NOT NULL,
    sk_capa integer NOT NULL,
    detalle_interseccion text NOT NULL
);


--
-- Name: dim_actividad; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_actividad (
    sk_actividad integer NOT NULL,
    codigo_actividad text,
    actividad_economica text
);


--
-- Name: dim_actividad_sk_actividad_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_actividad_sk_actividad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_actividad_sk_actividad_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_actividad_sk_actividad_seq OWNED BY dw.dim_actividad.sk_actividad;


--
-- Name: dim_area; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_area (
    sk_area integer NOT NULL,
    id_area integer,
    nombre_area character varying(255),
    abreviatura_area character varying(255),
    id_area_padre integer,
    zona character varying(100),
    campus character varying(255),
    estado_area character varying(20),
    fecha_carga timestamp without time zone DEFAULT now(),
    provincia character varying(100),
    canton character varying(100),
    parroquia character varying(100)
);


--
-- Name: dim_area_sk_area_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_area_sk_area_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_area_sk_area_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_area_sk_area_seq OWNED BY dw.dim_area.sk_area;


--
-- Name: dim_capa_ambiental; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_capa_ambiental (
    sk_capa integer NOT NULL,
    id_layer_origen integer,
    nombre_capa character varying(200),
    descripcion_capa text,
    categoria character varying(50),
    fecha_carga timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: dim_capa_ambiental_sk_capa_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_capa_ambiental_sk_capa_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_capa_ambiental_sk_capa_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_capa_ambiental_sk_capa_seq OWNED BY dw.dim_capa_ambiental.sk_capa;


--
-- Name: dim_chemical_importer; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_chemical_importer (
    importer_key integer NOT NULL,
    importer_id bigint NOT NULL,
    importer_name character varying(500),
    identification character varying(50),
    registration_code character varying(255),
    is_current boolean DEFAULT true,
    date_add timestamp without time zone DEFAULT now(),
    date_update timestamp without time zone
);


--
-- Name: dim_chemical_importer_importer_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_chemical_importer_importer_key_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_chemical_importer_importer_key_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_chemical_importer_importer_key_seq OWNED BY dw.dim_chemical_importer.importer_key;


--
-- Name: dim_chemical_storage; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_chemical_storage (
    storage_key bigint NOT NULL,
    storage_id bigint NOT NULL,
    storage_type character varying(200),
    capacity numeric(15,3),
    unit character varying(50),
    location_description character varying(1000)
);


--
-- Name: dim_chemical_storage_storage_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_chemical_storage_storage_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_chemical_storage_storage_key_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_chemical_storage_storage_key_seq OWNED BY dw.dim_chemical_storage.storage_key;


--
-- Name: dim_chemical_substance; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_chemical_substance (
    chemical_key bigint NOT NULL,
    chemical_id bigint NOT NULL,
    substance_name character varying(500),
    cas_number character varying(100),
    classification character varying(200),
    chemical_type character varying(100),
    effective_from timestamp without time zone,
    effective_to timestamp without time zone,
    is_current boolean DEFAULT true
);


--
-- Name: dim_chemical_substance_chemical_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_chemical_substance_chemical_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_chemical_substance_chemical_key_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_chemical_substance_chemical_key_seq OWNED BY dw.dim_chemical_substance.chemical_key;


--
-- Name: dim_dangerous_classification; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_dangerous_classification (
    danger_class_key bigint NOT NULL,
    class_id bigint NOT NULL,
    danger_level character varying(50),
    description character varying(500)
);


--
-- Name: dim_dangerous_classification_danger_class_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_dangerous_classification_danger_class_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_dangerous_classification_danger_class_key_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_dangerous_classification_danger_class_key_seq OWNED BY dw.dim_dangerous_classification.danger_class_key;


--
-- Name: dim_dangerous_waste; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_dangerous_waste (
    dangerous_waste_key bigint NOT NULL,
    dw_id bigint NOT NULL,
    dangerous_code character varying(100),
    description character varying(1000),
    regulation_reference character varying(500),
    is_current boolean DEFAULT true
);


--
-- Name: dim_dangerous_waste_dangerous_waste_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_dangerous_waste_dangerous_waste_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_dangerous_waste_dangerous_waste_key_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_dangerous_waste_dangerous_waste_key_seq OWNED BY dw.dim_dangerous_waste.dangerous_waste_key;


--
-- Name: dim_estado; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_estado (
    sk_estado integer NOT NULL,
    estado_proceso text,
    estado_proyecto text,
    estado_tramite text
);


--
-- Name: dim_estado_sk_estado_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_estado_sk_estado_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_estado_sk_estado_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_estado_sk_estado_seq OWNED BY dw.dim_estado.sk_estado;


--
-- Name: dim_geografia; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_geografia (
    sk_geografia integer NOT NULL,
    provincia character varying(255),
    canton character varying(255),
    parroquia character varying(255),
    sk_padre integer,
    nivel character varying(20) DEFAULT 'PARROQUIA'::character varying
);


--
-- Name: dim_geografia_sk_geografia_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_geografia_sk_geografia_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_geografia_sk_geografia_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_geografia_sk_geografia_seq OWNED BY dw.dim_geografia.sk_geografia;


--
-- Name: dim_intersection; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_intersection (
    sk_intersection integer NOT NULL,
    sk_proyecto integer,
    certificate_code character varying(100),
    certificate_date timestamp without time zone,
    html_location text,
    html_layers text,
    dictamen_final text,
    is_current boolean DEFAULT true,
    effective_from timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: dim_intersection_bak_20260401; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_intersection_bak_20260401 (
    sk_intersection integer,
    sk_proyecto integer,
    certificate_code character varying(100),
    certificate_date timestamp without time zone,
    html_location text,
    html_layers text,
    dictamen_final text,
    is_current boolean,
    effective_from timestamp without time zone
);


--
-- Name: dim_intersection_sk_intersection_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_intersection_sk_intersection_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_intersection_sk_intersection_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_intersection_sk_intersection_seq OWNED BY dw.dim_intersection.sk_intersection;


--
-- Name: dim_pago; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_pago (
    sk_pago integer NOT NULL,
    tipo_pago character varying(100),
    bank_code character varying(50),
    transaction_type character varying(100),
    sistema_origen character varying(50)
);


--
-- Name: dim_pago_sk_pago_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_pago_sk_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_pago_sk_pago_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_pago_sk_pago_seq OWNED BY dw.dim_pago.sk_pago;


--
-- Name: dim_process_flow; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_process_flow (
    sk_process_flow integer NOT NULL,
    process_name character varying(255),
    process_type character varying(100),
    process_status character varying(100)
);


--
-- Name: dim_process_flow_sk_process_flow_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_process_flow_sk_process_flow_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_process_flow_sk_process_flow_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_process_flow_sk_process_flow_seq OWNED BY dw.dim_process_flow.sk_process_flow;


--
-- Name: dim_proponente; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_proponente (
    sk_proponente integer NOT NULL,
    ced_ruc_proponente character varying(255),
    nombre_proponente text
);


--
-- Name: dim_proponente_sk_proponente_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_proponente_sk_proponente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_proponente_sk_proponente_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_proponente_sk_proponente_seq OWNED BY dw.dim_proponente.sk_proponente;


--
-- Name: dim_proyecto; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_proyecto (
    sk_proyecto integer NOT NULL,
    codigo_proyecto character varying(255),
    nombre_proyecto text,
    resumen_proyecto text,
    direccion_proyecto text,
    tipo_permiso_ambiental character varying(255),
    tipo_sector character varying(255),
    tipo_ente text,
    sistema character varying(255),
    estrategico text,
    area_responsable text
);


--
-- Name: dim_proyecto_sk_proyecto_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_proyecto_sk_proyecto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_proyecto_sk_proyecto_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_proyecto_sk_proyecto_seq OWNED BY dw.dim_proyecto.sk_proyecto;


--
-- Name: dim_tiempo; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_tiempo (
    sk_tiempo integer NOT NULL,
    fecha date,
    anio integer,
    mes integer,
    dia integer,
    trimestre integer,
    nombre_mes character varying(20),
    dia_semana character varying(15)
);


--
-- Name: dim_tiempo_sk_tiempo_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_tiempo_sk_tiempo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_tiempo_sk_tiempo_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_tiempo_sk_tiempo_seq OWNED BY dw.dim_tiempo.sk_tiempo;


--
-- Name: dim_usuario; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_usuario (
    sk_usuario integer NOT NULL,
    usuario_tarea character varying(255)
);


--
-- Name: dim_usuario_sk_usuario_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_usuario_sk_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_usuario_sk_usuario_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_usuario_sk_usuario_seq OWNED BY dw.dim_usuario.sk_usuario;


--
-- Name: dim_waste_generator; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_waste_generator (
    waste_generator_key bigint NOT NULL,
    waste_generator_id bigint NOT NULL,
    generator_name character varying(500),
    generator_type character varying(200),
    province character varying(100),
    canton character varying(100),
    codigo character varying(100),
    effective_from timestamp without time zone,
    effective_to timestamp without time zone,
    is_current boolean DEFAULT true,
    date_add timestamp without time zone,
    date_update timestamp without time zone,
    ruc_generator character varying
);


--
-- Name: dim_waste_generator_waste_generator_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_waste_generator_waste_generator_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_waste_generator_waste_generator_key_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_waste_generator_waste_generator_key_seq OWNED BY dw.dim_waste_generator.waste_generator_key;


--
-- Name: dim_waste_type; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_waste_type (
    waste_type_key bigint NOT NULL,
    cawa_id bigint NOT NULL,
    waste_key_code character varying(100),
    waste_name character varying(1000),
    waste_status boolean
);


--
-- Name: dim_waste_type_waste_type_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.dim_waste_type_waste_type_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dim_waste_type_waste_type_key_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.dim_waste_type_waste_type_key_seq OWNED BY dw.dim_waste_type.waste_type_key;


--
-- Name: etl_process_log; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.etl_process_log (
    id integer NOT NULL,
    process_name character varying(100) NOT NULL,
    start_time timestamp without time zone DEFAULT now(),
    end_time timestamp without time zone,
    status character varying(20),
    rows_inserted integer DEFAULT 0,
    rows_updated integer DEFAULT 0,
    error_message text,
    execution_mode character varying(20)
);


--
-- Name: etl_process_log_id_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.etl_process_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: etl_process_log_id_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.etl_process_log_id_seq OWNED BY dw.etl_process_log.id;


--
-- Name: fact_chemical_application; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_chemical_application (
    sk_proyecto bigint NOT NULL,
    chemical_key bigint NOT NULL,
    sk_tiempo bigint NOT NULL,
    storage_key bigint,
    geo_location_key bigint,
    dose numeric(15,3),
    dose_unit character varying(50),
    application_method character varying(200),
    area_covered numeric(15,3),
    usage_year integer
);


--
-- Name: fact_chemical_declaration; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_chemical_declaration (
    sk_proyecto bigint NOT NULL,
    importer_key bigint NOT NULL,
    sk_tiempo bigint NOT NULL,
    initial_quantity numeric(15,3),
    final_quantity numeric(15,3),
    is_on_time boolean,
    declaration_year integer,
    declaration_month integer
);


--
-- Name: fact_chemical_import; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_chemical_import (
    sk_proyecto bigint NOT NULL,
    chemical_key bigint NOT NULL,
    importer_key bigint NOT NULL,
    sk_tiempo bigint NOT NULL,
    geo_location_key bigint,
    quantity_authorized numeric(15,3),
    net_weight numeric(15,3),
    gross_weight numeric(15,3),
    import_status character varying(50),
    processing_code character varying(100),
    document_number character varying(100),
    source_system character varying(50)
);


--
-- Name: fact_chemical_movement; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_chemical_movement (
    sk_proyecto bigint NOT NULL,
    chemical_key bigint NOT NULL,
    importer_key bigint NOT NULL,
    sk_tiempo bigint NOT NULL,
    quantity_entry numeric(15,3),
    quantity_exit numeric(15,3),
    invoice_number character varying(100),
    operator_name character varying(500)
);


--
-- Name: fact_pago; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_pago (
    id_fact_pago integer NOT NULL,
    sk_proyecto integer,
    sk_pago integer,
    sk_fecha_pago integer,
    monto_transaccion numeric(20,2),
    monto_pagado numeric(20,2),
    numero_transaccion character varying(255),
    numero_tramite character varying(255),
    tarea_bpm character varying(255),
    proceso_bpm character varying(255),
    origen character varying(50),
    id_transaccion_origen character varying(255),
    fecha_carga timestamp without time zone DEFAULT now(),
    secuencia_pago integer,
    es_deposito_inicial boolean DEFAULT false,
    monto_acumulado numeric(20,2)
);


--
-- Name: fact_pago_id_fact_pago_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.fact_pago_id_fact_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fact_pago_id_fact_pago_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.fact_pago_id_fact_pago_seq OWNED BY dw.fact_pago.id_fact_pago;


--
-- Name: fact_payment_traceability; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_payment_traceability (
    id_payment_trace integer NOT NULL,
    sk_proyecto integer NOT NULL,
    sk_pago integer NOT NULL,
    sk_tiempo integer NOT NULL,
    id_online_payment_historical bigint,
    retired_value numeric(15,2),
    value_updated numeric(15,2),
    delta_value numeric(15,2),
    update_date timestamp without time zone,
    description text,
    fecha_carga timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: fact_payment_traceability_id_payment_trace_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.fact_payment_traceability_id_payment_trace_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fact_payment_traceability_id_payment_trace_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.fact_payment_traceability_id_payment_trace_seq OWNED BY dw.fact_payment_traceability.id_payment_trace;


--
-- Name: fact_project_environmental_impact; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_project_environmental_impact (
    sk_proyecto bigint NOT NULL,
    sk_tiempo bigint NOT NULL,
    total_waste_volume numeric(15,3),
    total_dangerous_waste_volume numeric(15,3),
    total_chemical_dose numeric(15,3),
    environmental_risk_score numeric(10,2)
);


--
-- Name: fact_proyecto_geografia; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_proyecto_geografia (
    sk_proyecto integer NOT NULL,
    sk_geografia integer NOT NULL,
    es_principal boolean DEFAULT false,
    fecha_carga timestamp without time zone DEFAULT now()
);


--
-- Name: fact_regularizacion; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_regularizacion (
    id_fact integer NOT NULL,
    sk_proyecto integer,
    sk_proponente integer,
    sk_actividad integer,
    sk_geografia integer,
    sk_usuario integer,
    sk_estado integer,
    sk_fecha_registro integer,
    interseccion_snap text DEFAULT 'NO'::character varying,
    areas_protegidas text,
    superficie_proyecto double precision,
    id_area integer,
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone,
    fecha_inicio_tarea timestamp without time zone,
    fecha_fin_tarea timestamp without time zone,
    proceso text,
    tarea text,
    nombre_zona character varying(500),
    finalizado_con_resolucion character varying(500),
    numero_resolucion character varying(500),
    fecha_resolucion timestamp without time zone,
    ente_acreditado text,
    origen character varying(50),
    fecha_carga timestamp without time zone DEFAULT now(),
    sk_area integer
);


--
-- Name: fact_regularizacion_id_fact_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.fact_regularizacion_id_fact_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fact_regularizacion_id_fact_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.fact_regularizacion_id_fact_seq OWNED BY dw.fact_regularizacion.id_fact;


--
-- Name: fact_waste_generation; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_waste_generation (
    sk_proyecto bigint NOT NULL,
    waste_generator_key bigint NOT NULL,
    sk_tiempo bigint NOT NULL,
    waste_type_key bigint NOT NULL,
    dangerous_waste_key bigint,
    danger_class_key bigint,
    geo_location_key bigint,
    quantity_generated numeric(15,3),
    quantity_delivered numeric(15,3),
    quantity_stored numeric(15,3),
    unit character varying(50),
    record_year integer,
    source_system character varying(50)
);


--
-- Name: v_dashboard_regularizacion; Type: VIEW; Schema: dw; Owner: -
--

CREATE VIEW dw.v_dashboard_regularizacion AS
 SELECT f.id_fact,
    f.origen,
    p.codigo_proyecto,
    p.nombre_proyecto,
    p.tipo_permiso_ambiental,
    p.tipo_sector,
    p.tipo_ente,
    p.sistema,
    p.estrategico,
    prop.ced_ruc_proponente,
    prop.nombre_proponente,
    act.codigo_actividad,
    act.actividad_economica,
    geo.provincia,
    geo.canton,
    geo.parroquia,
    COALESCE(da.nombre_area, 'N/A'::character varying) AS oficina_tecnica,
    COALESCE(da.zona, 'N/A'::character varying) AS zona_administrativa,
    COALESCE(da.campus, 'N/A'::character varying) AS sede_campus,
    u.usuario_tarea,
    est.estado_proceso,
    est.estado_proyecto,
    est.estado_tramite,
    t.fecha AS fecha_registro,
    t.anio AS anio_registro,
    t.nombre_mes AS mes_registro,
    t.trimestre AS trimestre_registro,
    f.interseccion_snap,
    f.areas_protegidas,
    f.superficie_proyecto,
    f.id_area,
    f.fecha_inicio_proceso,
    f.fecha_fin_proceso,
    (EXTRACT(epoch FROM (f.fecha_fin_proceso - f.fecha_inicio_proceso)) / (86400)::numeric) AS duracion_proceso_dias,
    f.fecha_inicio_tarea,
    f.fecha_fin_tarea,
    (EXTRACT(epoch FROM (f.fecha_fin_tarea - f.fecha_inicio_tarea)) / (3600)::numeric) AS duracion_tarea_horas,
    f.finalizado_con_resolucion,
    f.numero_resolucion,
    f.fecha_resolucion,
        CASE
            WHEN ((f.finalizado_con_resolucion IS NOT NULL) AND ((f.finalizado_con_resolucion)::text <> ''::text)) THEN 1
            ELSE 0
        END AS es_resolucion
   FROM ((((((((dw.fact_regularizacion f
     LEFT JOIN dw.dim_proyecto p ON ((f.sk_proyecto = p.sk_proyecto)))
     LEFT JOIN dw.dim_proponente prop ON ((f.sk_proponente = prop.sk_proponente)))
     LEFT JOIN dw.dim_actividad act ON ((f.sk_actividad = act.sk_actividad)))
     LEFT JOIN dw.dim_geografia geo ON ((f.sk_geografia = geo.sk_geografia)))
     LEFT JOIN dw.dim_usuario u ON ((f.sk_usuario = u.sk_usuario)))
     LEFT JOIN dw.dim_estado est ON ((f.sk_estado = est.sk_estado)))
     LEFT JOIN dw.dim_tiempo t ON ((f.sk_fecha_registro = t.sk_tiempo)))
     LEFT JOIN dw.dim_area da ON ((f.sk_area = da.sk_area)));


--
-- Name: mv_dashboard_regularizacion; Type: MATERIALIZED VIEW; Schema: dw; Owner: -
--

CREATE MATERIALIZED VIEW dw.mv_dashboard_regularizacion AS
 SELECT id_fact,
    origen,
    codigo_proyecto,
    nombre_proyecto,
    tipo_permiso_ambiental,
    tipo_sector,
    tipo_ente,
    sistema,
    estrategico,
    ced_ruc_proponente,
    nombre_proponente,
    codigo_actividad,
    actividad_economica,
    provincia,
    canton,
    parroquia,
    oficina_tecnica,
    zona_administrativa,
    sede_campus,
    usuario_tarea,
    estado_proceso,
    estado_proyecto,
    estado_tramite,
    fecha_registro,
    anio_registro,
    mes_registro,
    trimestre_registro,
    interseccion_snap,
    areas_protegidas,
    superficie_proyecto,
    id_area,
    fecha_inicio_proceso,
    fecha_fin_proceso,
    duracion_proceso_dias,
    fecha_inicio_tarea,
    fecha_fin_tarea,
    duracion_tarea_horas,
    finalizado_con_resolucion,
    numero_resolucion,
    fecha_resolucion,
    es_resolucion
   FROM dw.v_dashboard_regularizacion
  WITH NO DATA;


--
-- Name: roles; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.roles (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL,
    description text
);


--
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.roles_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.roles_role_id_seq OWNED BY dw.roles.role_id;


--
-- Name: users; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.users (
    user_id integer NOT NULL,
    username character varying(100) NOT NULL,
    password_hash text NOT NULL,
    full_name character varying(200),
    role_id integer,
    status character varying(20) DEFAULT 'Active'::character varying,
    last_login timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    failed_attempts integer DEFAULT 0,
    locked_until timestamp without time zone,
    must_change_password boolean DEFAULT false
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

CREATE SEQUENCE dw.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: dw; Owner: -
--

ALTER SEQUENCE dw.users_user_id_seq OWNED BY dw.users.user_id;


--
-- Name: jbpm_4cat_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.jbpm_4cat_bi (
    codigo_proyecto character varying(255),
    nombre_proyecto text,
    resumen_proyecto text,
    direccion_proyecto character varying(255),
    fecha_registro date,
    codigo_actividad character varying(255),
    actividad_economica text,
    ced_ruc_proponente character varying(255),
    nombre_proponente text,
    area_responsable_proyecto text,
    tipo_sector character varying(255),
    tipo_permiso_ambiental character varying(255),
    tipo_ente text,
    provincia text,
    canton character varying(255),
    parroquia character varying(255),
    proceso character varying(255),
    estado_proceso text,
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone,
    tarea character varying(500),
    estado_tarea text,
    fecha_inicio_tarea timestamp without time zone,
    fecha_fin_tarea timestamp without time zone,
    usuario_tarea character varying(255),
    estado_proyecto text,
    intersecta_con text,
    areas_protegidas text,
    sistema text,
    ente_acreditado text,
    estado_tramite character varying(255),
    estrategico character varying(255),
    fecha_carga timestamp without time zone DEFAULT now(),
    origen character varying(50) DEFAULT 'JBPM_4CAT'::character varying
);


--
-- Name: jbpm_hidro_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.jbpm_hidro_bi (
    codigo_proyecto character varying(255),
    nombre_proyecto text,
    resumen_proyecto text,
    direccion_proyecto character varying(255),
    fecha_registro date,
    codigo_actividad character varying(255),
    actividad_economica character varying(255),
    ced_ruc_proponente character varying(255),
    nombre_proponente character varying(500),
    area_responsable_proyecto character varying(255),
    tipo_sector character varying(255),
    tipo_permiso_ambiental character varying(255),
    tipo_ente character varying(255),
    provincia character varying(255),
    canton character varying(255),
    parroquia character varying(255),
    proceso character varying(255),
    estado_proceso text,
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone,
    tarea character varying(500),
    estado_tarea text,
    fecha_inicio_tarea timestamp without time zone,
    fecha_fin_tarea timestamp without time zone,
    usuario_tarea text,
    estado_proyecto text,
    intersecta_con text,
    id_area integer,
    ente_acreditado text,
    estado_tramite character varying(255),
    estrategico text,
    fecha_carga timestamp without time zone DEFAULT now(),
    origen character varying(50) DEFAULT 'JBPM_HIDRO'::character varying
);


--
-- Name: jbpm_sector_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.jbpm_sector_bi (
    codigo_proyecto character varying(255),
    nombre_proyecto text,
    resumen_proyecto text,
    direccion_proyecto text,
    fecha_registro date,
    codigo_actividad character varying(255),
    actividad_economica text,
    ced_ruc_proponente character varying(255),
    nombre_proponente text,
    area_responsable_proyecto text,
    tipo_sector character varying(255),
    tipo_permiso_ambiental text,
    tipo_ente text,
    provincia text,
    canton character varying(255),
    parroquia character varying(255),
    proceso text,
    estado_proceso text,
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone,
    tarea character varying(500),
    estado_tarea text,
    fecha_inicio_tarea timestamp without time zone,
    fecha_fin_tarea timestamp without time zone,
    usuario_tarea character varying(255),
    estado_proyecto character varying(255),
    intersecta_con text,
    areas_protegidas text,
    sistema text,
    ente_acreditado text,
    estado_tramite text,
    estrategico text,
    fecha_carga timestamp without time zone DEFAULT now(),
    origen character varying(50) DEFAULT 'JBPM_SECTOR'::character varying
);


--
-- Name: suia_coa_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.suia_coa_bi (
    codigo_proyecto character varying(255),
    nombre_proyecto text,
    resumen_proyecto text,
    direccion_proyecto text,
    fecha_registro date,
    codigo_actividad text,
    actividad_economica text,
    ced_ruc_proponente character varying(255),
    nombre_proponente character varying(500),
    area_responsable_proyecto character varying(500),
    tipo_sector character varying(255),
    tipo_permiso_ambiental character varying(255),
    tipo_ente character varying(255),
    provincia character varying(255),
    canton character varying(255),
    parroquia character varying(255),
    proceso character varying(255),
    estado_proceso character varying(255),
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone,
    tarea character varying(500),
    estado_tarea character varying(255),
    fecha_inicio_tarea timestamp without time zone,
    fecha_fin_tarea timestamp without time zone,
    usuario_tarea character varying(255),
    estado_proyecto character varying(255),
    intersecta_con text,
    areas_protegidas text,
    sistema character varying(255),
    nombre_zona character varying(500),
    finalizado_con_resolucion character varying(500),
    numero_resolucion character varying(500),
    fecha_resolucion timestamp without time zone,
    id_area integer,
    estado_tramite character varying(500),
    superficie_proyecto double precision,
    fecha_carga timestamp without time zone DEFAULT now(),
    origen character varying(50) DEFAULT 'COA'::character varying
);


--
-- Name: suia_rcoa_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.suia_rcoa_bi (
    codigo_proyecto character varying(255),
    nombre_proyecto text,
    resumen_proyecto text,
    direccion_proyecto text,
    fecha_registro date,
    codigo_actividad text,
    actividad_economica text,
    ced_ruc_proponente character varying(255),
    nombre_proponente character varying(500),
    area_responsable_proyecto character varying(500),
    tipo_sector character varying(255),
    tipo_permiso_ambiental character varying(255),
    tipo_ente character varying(255),
    provincia character varying(255),
    canton character varying(255),
    parroquia character varying(255),
    proceso character varying(255),
    estado_proceso character varying(255),
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone,
    tarea character varying(500),
    estado_tarea character varying(255),
    fecha_inicio_tarea timestamp without time zone,
    fecha_fin_tarea timestamp without time zone,
    usuario_tarea character varying(255),
    estado_proyecto character varying(255),
    intersecta_con text,
    areas_protegidas text,
    sistema character varying(255),
    nombre_zona character varying(500),
    finalizado_con_resolucion character varying(500),
    numero_resolucion character varying(500),
    fecha_resolucion timestamp without time zone,
    id_area integer,
    estado_tramite character varying(500),
    superficie_proyecto double precision,
    fecha_carga timestamp without time zone DEFAULT now(),
    origen character varying(50) DEFAULT 'RCOA'::character varying
);


--
-- Name: v_integridad_dashboard; Type: VIEW; Schema: dw; Owner: -
--

CREATE VIEW dw.v_integridad_dashboard AS
 WITH cte_stg AS (
         SELECT 'RCOA'::text AS origen,
            count(*) AS registros_stg
           FROM stg.suia_rcoa_bi
        UNION ALL
         SELECT 'COA'::text AS text,
            count(*) AS count
           FROM stg.suia_coa_bi
        UNION ALL
         SELECT 'JBPM_SECTOR'::text AS text,
            count(*) AS count
           FROM stg.jbpm_sector_bi
        UNION ALL
         SELECT 'JBPM_4CAT'::text AS text,
            count(*) AS count
           FROM stg.jbpm_4cat_bi
        UNION ALL
         SELECT 'JBPM_HIDRO'::text AS text,
            count(*) AS count
           FROM stg.jbpm_hidro_bi
        ), cte_fact AS (
         SELECT (f_1.origen)::text AS origen,
            count(*) AS registros_dw
           FROM dw.fact_regularizacion f_1
          GROUP BY (f_1.origen)::text
        )
 SELECT s.origen,
    s.registros_stg AS total_produccion,
    COALESCE(f.registros_dw, (0)::bigint) AS total_dwh,
    (s.registros_stg - COALESCE(f.registros_dw, (0)::bigint)) AS diferencia,
        CASE
            WHEN (s.registros_stg = 0) THEN 100.00
            ELSE round((((COALESCE(f.registros_dw, (0)::bigint))::numeric / (s.registros_stg)::numeric) * (100)::numeric), 2)
        END AS porcentaje_integridad
   FROM (cte_stg s
     LEFT JOIN cte_fact f ON ((s.origen = f.origen)));


--
-- Name: tmp_recovered_projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tmp_recovered_projects (
    codigo_proyecto text,
    nombre_proyecto text,
    fecha_registro timestamp without time zone,
    sistema text
);


--
-- Name: vw_detalle_errores_carga; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.vw_detalle_errores_carga AS
 WITH todas_fuentes AS (
         SELECT 'RCOA'::text AS origen,
            suia_rcoa_bi.codigo_proyecto,
            suia_rcoa_bi.nombre_proyecto,
            suia_rcoa_bi.fecha_registro
           FROM stg.suia_rcoa_bi
        UNION ALL
         SELECT 'COA'::text AS origen,
            suia_coa_bi.codigo_proyecto,
            suia_coa_bi.nombre_proyecto,
            suia_coa_bi.fecha_registro
           FROM stg.suia_coa_bi
        UNION ALL
         SELECT 'JBPM_SECTOR'::text AS origen,
            jbpm_sector_bi.codigo_proyecto,
            jbpm_sector_bi.nombre_proyecto,
            jbpm_sector_bi.fecha_registro
           FROM stg.jbpm_sector_bi
        UNION ALL
         SELECT 'JBPM_4CAT'::text AS origen,
            jbpm_4cat_bi.codigo_proyecto,
            jbpm_4cat_bi.nombre_proyecto,
            jbpm_4cat_bi.fecha_registro
           FROM stg.jbpm_4cat_bi
        UNION ALL
         SELECT 'JBPM_HIDRO'::text AS origen,
            jbpm_hidro_bi.codigo_proyecto,
            jbpm_hidro_bi.nombre_proyecto,
            jbpm_hidro_bi.fecha_registro
           FROM stg.jbpm_hidro_bi
        )
 SELECT origen,
    codigo_proyecto,
    nombre_proyecto,
    fecha_registro,
    'Ausente en DWH'::text AS detalle_error
   FROM todas_fuentes f
  WHERE ((NOT (EXISTS ( SELECT 1
           FROM dw.dim_proyecto p
          WHERE ((p.codigo_proyecto)::text = (f.codigo_proyecto)::text)))) AND (nombre_proyecto <> 'Proyecto Recuperado (JBPM)'::text))
 LIMIT 2000;


--
-- Name: inec_dpa_2024; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.inec_dpa_2024 (
    codigo_provincia character(2) NOT NULL,
    nombre_provincia character varying(100) NOT NULL,
    descripcion character varying(255)
);


--
-- Name: consolidado_proyectos; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.consolidado_proyectos (
    codigo_proyecto character varying(255),
    nombre_proyecto text,
    resumen_proyecto text,
    direccion_proyecto text,
    fecha_registro date,
    codigo_actividad text,
    actividad_economica text,
    ced_ruc_proponente character varying(255),
    nombre_proponente text,
    area_responsable_proyecto text,
    tipo_sector character varying(255),
    tipo_permiso_ambiental character varying(255),
    tipo_ente text,
    provincia character varying(255),
    canton character varying(255),
    parroquia character varying(255),
    proceso text,
    estado_proceso text,
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone,
    tarea text,
    estado_tarea text,
    fecha_inicio_tarea timestamp without time zone,
    fecha_fin_tarea timestamp without time zone,
    usuario_tarea character varying(255),
    estado_proyecto text,
    intersecta_con text,
    areas_protegidas text,
    sistema character varying(255),
    nombre_zona character varying(500),
    finalizado_con_resolucion character varying(500),
    numero_resolucion character varying(500),
    fecha_resolucion timestamp without time zone,
    ente_acreditado text,
    estado_tramite text,
    id_area integer DEFAULT 0,
    superficie_proyecto double precision DEFAULT 0,
    estrategico text,
    origen character varying(50)
);


--
-- Name: financial_transaction_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.financial_transaction_bi (
    fitr_id integer,
    codigo_proyecto character varying(255),
    fitr_transaction_amount numeric(20,2),
    fitr_paid_value numeric(20,2),
    fitr_transaction_number character varying(255),
    fitr_payment_type integer,
    payment_type_desc character varying(100),
    fitr_creation_date timestamp without time zone,
    fitr_status boolean,
    task_name character varying(255),
    processname character varying(255),
    processinstanceid bigint,
    fecha_carga timestamp without time zone DEFAULT now(),
    origen character varying(50) DEFAULT 'SUIA_RCOA'::character varying
);


--
-- Name: geographical_locations_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.geographical_locations_bi (
    gelo_id integer,
    gelo_name character varying(255),
    gelo_parent_id integer,
    gelo_codification_inec character varying(50),
    fecha_carga timestamp without time zone DEFAULT now()
);


--
-- Name: jbpm_snap_variables; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.jbpm_snap_variables (
    codigo_proyecto text,
    processinstanceid bigint,
    nombre_proceso text,
    estado_proceso integer,
    fecha_inicio_proceso timestamp without time zone,
    fecha_fin_proceso timestamp without time zone
);


--
-- Name: online_payments_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.online_payments_bi (
    online_payment_id integer,
    project_id character varying(255),
    tramit_number character varying(255),
    convenience_number character varying(255),
    bank_code character varying(50),
    payment_value numeric(20,2),
    date_hour_transaction timestamp without time zone,
    transaction_type character varying(100),
    transaction_state boolean,
    fecha_carga timestamp without time zone DEFAULT now(),
    origen character varying(50) DEFAULT 'JBPM'::character varying
);


--
-- Name: online_payments_historical_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.online_payments_historical_bi (
    id_online_payment_historical bigint,
    description text,
    project_id text,
    retired_value double precision,
    sender_ip text,
    tramit_number text,
    update_date timestamp without time zone,
    value_updated double precision,
    online_payment_id bigint,
    enabled boolean,
    user_create text,
    user_modification text,
    date_create text,
    date_modification text,
    reactivate text,
    observations text
);


--
-- Name: stg_chemical_storage; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_chemical_storage (
    storage_id bigint,
    storage_type text,
    capacity text,
    unit text,
    location_description text
);


--
-- Name: stg_chemical_substance; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_chemical_substance (
    chemical_id bigint,
    substance_name text,
    cas_number text,
    classification text,
    chemical_type text
);


--
-- Name: stg_chemical_substances_declaration; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_chemical_substances_declaration (
    chsd_id bigint,
    chsr_id bigint,
    dach_id double precision,
    chsd_operator text,
    chsd_year bigint,
    chsd_unit text,
    chsd_starting_amount double precision,
    chsd_end_quantity double precision,
    chsd_declaration_on_time text,
    chsd_fine_statement double precision,
    geca_id_parameter_ci text,
    chsd_status boolean,
    chsd_status_date timestamp without time zone,
    chsd_creation_date timestamp without time zone,
    chsd_creator_user text,
    chsd_date_update timestamp without time zone,
    chsd_user_update text,
    chsd_observation_bd text,
    chsd_month bigint,
    chsd_declaration_status_geca_id double precision,
    chsd_pending_payment boolean,
    chsd_procedure_code text,
    chsd_date_observation_bd timestamp without time zone
);


--
-- Name: stg_chemical_substances_movements; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_chemical_substances_movements (
    chsm_id bigint,
    chsd_id bigint,
    geca_id bigint,
    chsm_invoice text,
    chsm_operator double precision,
    chsm_entry double precision,
    chsm_exit double precision,
    geca_id_presentation double precision,
    chsm_presentation_option text,
    chsm_finished_product text,
    chsm_packaging_quantity double precision,
    chsm_packaging_serial_number text,
    chsm_status boolean,
    chsm_observation_status text,
    chsm_review text,
    chsm_review_date text,
    chsm_creation_date timestamp without time zone,
    chsm_creator_user text,
    chsm_date_update timestamp without time zone,
    chsm_user_update text,
    chsm_observation_bd text,
    chsm_right text,
    chsm_description text,
    chsr_id double precision,
    inre_id double precision
);


--
-- Name: stg_chemical_sustances_records; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_chemical_sustances_records (
    chsr_id bigint,
    prco_id double precision,
    chsr_identification_rep_legal text,
    chsr_name_rep_legal text,
    chsr_substance_registration text,
    chsr_code text,
    chsr_valid_since timestamp without time zone,
    chsr_valid_until timestamp without time zone,
    chsr_status boolean
);


--
-- Name: stg_dangerous_classification; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_dangerous_classification (
    class_id bigint,
    danger_level text,
    description text
);


--
-- Name: stg_dangerous_waste; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_dangerous_waste (
    dw_id bigint,
    dangerous_code text,
    description text,
    regulation_reference text
);


--
-- Name: stg_detail_import_request; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_detail_import_request (
    deir_id bigint,
    inre_id bigint,
    deir_available_space double precision,
    deir_net_weight double precision,
    deir_gross_weight double precision,
    gelo_id double precision,
    achs_id double precision
);


--
-- Name: stg_detail_pesticide_project; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_detail_pesticide_project (
    depp_id bigint,
    chpe_id bigint,
    pqa_id bigint,
    fecha_carga timestamp without time zone DEFAULT now()
);


--
-- Name: stg_fact_chemical_application; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_fact_chemical_application (
    project_id double precision,
    chemical_id bigint,
    date_applied timestamp without time zone,
    storage_id text,
    location_id text,
    dose double precision,
    dose_unit text,
    application_method text,
    area_covered double precision,
    usage_year bigint
);


--
-- Name: stg_fact_waste_generation; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_fact_waste_generation (
    project_code text,
    lp_id_proyect double precision,
    lp_prco_id double precision,
    waste_generator_id bigint,
    date_generated timestamp without time zone,
    waste_type_id bigint,
    dangerous_waste_id text,
    danger_class_id text,
    location_id text,
    quantity_generated double precision,
    quantity_delivered double precision,
    quantity_stored double precision,
    unit text,
    record_year double precision,
    source_system text,
    project_id double precision
);


--
-- Name: stg_import_request; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_import_request (
    inre_id bigint,
    chsr_id bigint,
    mach_id double precision,
    dach_id double precision,
    inre_authorization boolean,
    inre_begin_authorization_date timestamp without time zone,
    inre_end_authorization_date timestamp without time zone,
    inre_processing_code text,
    inre_document_autorizes text,
    req_no text,
    inre_type text,
    inre_status boolean
);


--
-- Name: stg_intersection; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_intersection (
    project_code text,
    certificate_code text,
    certificate_date timestamp without time zone,
    html_location text,
    html_layers text,
    dictamen_final text
);


--
-- Name: stg_intersection_bak_20260401; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_intersection_bak_20260401 (
    project_code text,
    certificate_code text,
    certificate_date timestamp without time zone,
    html_location text,
    html_layers text,
    dictamen_final text
);


--
-- Name: stg_pesticide_project; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_pesticide_project (
    chpe_id bigint,
    chpe_proyect_code text,
    chpe_status boolean
);


--
-- Name: stg_products_pqa; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_products_pqa (
    pqa_id bigint,
    pqa_name text,
    pqa_registration_number text,
    pqa_toxicological_category text
);


--
-- Name: stg_project_mapping; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_project_mapping (
    prco_id bigint,
    prco_cua text
);


--
-- Name: stg_rgd_project_mapping; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_rgd_project_mapping (
    ware_id bigint,
    prco_id bigint,
    id_proyect bigint,
    wapr_description_system text
);


--
-- Name: stg_waste_generator; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_waste_generator (
    waste_generator_id bigint,
    generator_name text,
    generator_type text,
    ruc_generator text,
    identification_type text,
    province text,
    canton text,
    date_add timestamp without time zone,
    date_update timestamp without time zone
);


--
-- Name: stg_waste_type; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.stg_waste_type (
    cawa_id bigint,
    waste_key_code text,
    waste_name text,
    waste_status boolean
);


--
-- Name: suia_areas_bi; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.suia_areas_bi (
    area_id integer,
    area_name character varying(255),
    area_abbreviation character varying(255),
    area_parent_id integer,
    zone_id integer,
    area_status boolean,
    area_campus character varying(255),
    arty_id integer,
    fecha_carga timestamp without time zone DEFAULT now(),
    gelo_id integer
);


--
-- Name: tmp_dim_proyecto_optimized; Type: TABLE; Schema: stg; Owner: -
--

CREATE TABLE stg.tmp_dim_proyecto_optimized (
    sk_proyecto integer,
    codigo_proyecto character varying(255),
    sk_geografia integer
);


--
-- Name: audit_logs log_id; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.audit_logs ALTER COLUMN log_id SET DEFAULT nextval('dw.audit_logs_log_id_seq'::regclass);


--
-- Name: dim_actividad sk_actividad; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_actividad ALTER COLUMN sk_actividad SET DEFAULT nextval('dw.dim_actividad_sk_actividad_seq'::regclass);


--
-- Name: dim_area sk_area; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_area ALTER COLUMN sk_area SET DEFAULT nextval('dw.dim_area_sk_area_seq'::regclass);


--
-- Name: dim_capa_ambiental sk_capa; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_capa_ambiental ALTER COLUMN sk_capa SET DEFAULT nextval('dw.dim_capa_ambiental_sk_capa_seq'::regclass);


--
-- Name: dim_chemical_importer importer_key; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_importer ALTER COLUMN importer_key SET DEFAULT nextval('dw.dim_chemical_importer_importer_key_seq'::regclass);


--
-- Name: dim_chemical_storage storage_key; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_storage ALTER COLUMN storage_key SET DEFAULT nextval('dw.dim_chemical_storage_storage_key_seq'::regclass);


--
-- Name: dim_chemical_substance chemical_key; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_substance ALTER COLUMN chemical_key SET DEFAULT nextval('dw.dim_chemical_substance_chemical_key_seq'::regclass);


--
-- Name: dim_dangerous_classification danger_class_key; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_dangerous_classification ALTER COLUMN danger_class_key SET DEFAULT nextval('dw.dim_dangerous_classification_danger_class_key_seq'::regclass);


--
-- Name: dim_dangerous_waste dangerous_waste_key; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_dangerous_waste ALTER COLUMN dangerous_waste_key SET DEFAULT nextval('dw.dim_dangerous_waste_dangerous_waste_key_seq'::regclass);


--
-- Name: dim_estado sk_estado; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_estado ALTER COLUMN sk_estado SET DEFAULT nextval('dw.dim_estado_sk_estado_seq'::regclass);


--
-- Name: dim_geografia sk_geografia; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_geografia ALTER COLUMN sk_geografia SET DEFAULT nextval('dw.dim_geografia_sk_geografia_seq'::regclass);


--
-- Name: dim_intersection sk_intersection; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_intersection ALTER COLUMN sk_intersection SET DEFAULT nextval('dw.dim_intersection_sk_intersection_seq'::regclass);


--
-- Name: dim_pago sk_pago; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_pago ALTER COLUMN sk_pago SET DEFAULT nextval('dw.dim_pago_sk_pago_seq'::regclass);


--
-- Name: dim_process_flow sk_process_flow; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_process_flow ALTER COLUMN sk_process_flow SET DEFAULT nextval('dw.dim_process_flow_sk_process_flow_seq'::regclass);


--
-- Name: dim_proponente sk_proponente; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_proponente ALTER COLUMN sk_proponente SET DEFAULT nextval('dw.dim_proponente_sk_proponente_seq'::regclass);


--
-- Name: dim_proyecto sk_proyecto; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_proyecto ALTER COLUMN sk_proyecto SET DEFAULT nextval('dw.dim_proyecto_sk_proyecto_seq'::regclass);


--
-- Name: dim_tiempo sk_tiempo; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_tiempo ALTER COLUMN sk_tiempo SET DEFAULT nextval('dw.dim_tiempo_sk_tiempo_seq'::regclass);


--
-- Name: dim_usuario sk_usuario; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_usuario ALTER COLUMN sk_usuario SET DEFAULT nextval('dw.dim_usuario_sk_usuario_seq'::regclass);


--
-- Name: dim_waste_generator waste_generator_key; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_waste_generator ALTER COLUMN waste_generator_key SET DEFAULT nextval('dw.dim_waste_generator_waste_generator_key_seq'::regclass);


--
-- Name: dim_waste_type waste_type_key; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_waste_type ALTER COLUMN waste_type_key SET DEFAULT nextval('dw.dim_waste_type_waste_type_key_seq'::regclass);


--
-- Name: etl_process_log id; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.etl_process_log ALTER COLUMN id SET DEFAULT nextval('dw.etl_process_log_id_seq'::regclass);


--
-- Name: fact_pago id_fact_pago; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_pago ALTER COLUMN id_fact_pago SET DEFAULT nextval('dw.fact_pago_id_fact_pago_seq'::regclass);


--
-- Name: fact_payment_traceability id_payment_trace; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_payment_traceability ALTER COLUMN id_payment_trace SET DEFAULT nextval('dw.fact_payment_traceability_id_payment_trace_seq'::regclass);


--
-- Name: fact_regularizacion id_fact; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion ALTER COLUMN id_fact SET DEFAULT nextval('dw.fact_regularizacion_id_fact_seq'::regclass);


--
-- Name: roles role_id; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.roles ALTER COLUMN role_id SET DEFAULT nextval('dw.roles_role_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.users ALTER COLUMN user_id SET DEFAULT nextval('dw.users_user_id_seq'::regclass);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (log_id);


--
-- Name: bridge_interseccion_ambiental bridge_interseccion_ambiental_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.bridge_interseccion_ambiental
    ADD CONSTRAINT bridge_interseccion_ambiental_pkey PRIMARY KEY (sk_proyecto, sk_capa, detalle_interseccion);


--
-- Name: dim_actividad dim_actividad_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_actividad
    ADD CONSTRAINT dim_actividad_pkey PRIMARY KEY (sk_actividad);


--
-- Name: dim_area dim_area_id_area_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_area
    ADD CONSTRAINT dim_area_id_area_key UNIQUE (id_area);


--
-- Name: dim_area dim_area_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_area
    ADD CONSTRAINT dim_area_pkey PRIMARY KEY (sk_area);


--
-- Name: dim_capa_ambiental dim_capa_ambiental_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_capa_ambiental
    ADD CONSTRAINT dim_capa_ambiental_pkey PRIMARY KEY (sk_capa);


--
-- Name: dim_chemical_importer dim_chemical_importer_importer_id_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_importer
    ADD CONSTRAINT dim_chemical_importer_importer_id_key UNIQUE (importer_id);


--
-- Name: dim_chemical_importer dim_chemical_importer_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_importer
    ADD CONSTRAINT dim_chemical_importer_pkey PRIMARY KEY (importer_key);


--
-- Name: dim_chemical_storage dim_chemical_storage_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_storage
    ADD CONSTRAINT dim_chemical_storage_pkey PRIMARY KEY (storage_key);


--
-- Name: dim_chemical_substance dim_chemical_substance_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_substance
    ADD CONSTRAINT dim_chemical_substance_pkey PRIMARY KEY (chemical_key);


--
-- Name: dim_dangerous_classification dim_dangerous_classification_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_dangerous_classification
    ADD CONSTRAINT dim_dangerous_classification_pkey PRIMARY KEY (danger_class_key);


--
-- Name: dim_dangerous_waste dim_dangerous_waste_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_dangerous_waste
    ADD CONSTRAINT dim_dangerous_waste_pkey PRIMARY KEY (dangerous_waste_key);


--
-- Name: dim_estado dim_estado_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_estado
    ADD CONSTRAINT dim_estado_pkey PRIMARY KEY (sk_estado);


--
-- Name: dim_geografia dim_geografia_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_geografia
    ADD CONSTRAINT dim_geografia_pkey PRIMARY KEY (sk_geografia);


--
-- Name: dim_intersection dim_intersection_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_intersection
    ADD CONSTRAINT dim_intersection_pkey PRIMARY KEY (sk_intersection);


--
-- Name: dim_intersection dim_intersection_sk_proyecto_certificate_code_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_intersection
    ADD CONSTRAINT dim_intersection_sk_proyecto_certificate_code_key UNIQUE (sk_proyecto, certificate_code);


--
-- Name: dim_pago dim_pago_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_pago
    ADD CONSTRAINT dim_pago_pkey PRIMARY KEY (sk_pago);


--
-- Name: dim_process_flow dim_process_flow_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_process_flow
    ADD CONSTRAINT dim_process_flow_pkey PRIMARY KEY (sk_process_flow);


--
-- Name: dim_proponente dim_proponente_ced_ruc_proponente_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_proponente
    ADD CONSTRAINT dim_proponente_ced_ruc_proponente_key UNIQUE (ced_ruc_proponente);


--
-- Name: dim_proponente dim_proponente_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_proponente
    ADD CONSTRAINT dim_proponente_pkey PRIMARY KEY (sk_proponente);


--
-- Name: dim_proyecto dim_proyecto_codigo_proyecto_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_proyecto
    ADD CONSTRAINT dim_proyecto_codigo_proyecto_key UNIQUE (codigo_proyecto);


--
-- Name: dim_proyecto dim_proyecto_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_proyecto
    ADD CONSTRAINT dim_proyecto_pkey PRIMARY KEY (sk_proyecto);


--
-- Name: dim_tiempo dim_tiempo_fecha_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_tiempo
    ADD CONSTRAINT dim_tiempo_fecha_key UNIQUE (fecha);


--
-- Name: dim_tiempo dim_tiempo_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_tiempo
    ADD CONSTRAINT dim_tiempo_pkey PRIMARY KEY (sk_tiempo);


--
-- Name: dim_usuario dim_usuario_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_usuario
    ADD CONSTRAINT dim_usuario_pkey PRIMARY KEY (sk_usuario);


--
-- Name: dim_usuario dim_usuario_usuario_tarea_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_usuario
    ADD CONSTRAINT dim_usuario_usuario_tarea_key UNIQUE (usuario_tarea);


--
-- Name: dim_waste_generator dim_waste_generator_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_waste_generator
    ADD CONSTRAINT dim_waste_generator_pkey PRIMARY KEY (waste_generator_key);


--
-- Name: dim_waste_type dim_waste_type_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_waste_type
    ADD CONSTRAINT dim_waste_type_pkey PRIMARY KEY (waste_type_key);


--
-- Name: dim_chemical_storage dw_dim_chemical_storage_id_unique; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_storage
    ADD CONSTRAINT dw_dim_chemical_storage_id_unique UNIQUE (storage_id);


--
-- Name: dim_chemical_substance dw_dim_chemical_substance_id_unique; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_chemical_substance
    ADD CONSTRAINT dw_dim_chemical_substance_id_unique UNIQUE (chemical_id);


--
-- Name: dim_dangerous_classification dw_dim_dangerous_classification_id_unique; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_dangerous_classification
    ADD CONSTRAINT dw_dim_dangerous_classification_id_unique UNIQUE (class_id);


--
-- Name: dim_dangerous_waste dw_dim_dangerous_waste_id_unique; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_dangerous_waste
    ADD CONSTRAINT dw_dim_dangerous_waste_id_unique UNIQUE (dw_id);


--
-- Name: dim_waste_generator dw_dim_waste_generator_id_unique; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_waste_generator
    ADD CONSTRAINT dw_dim_waste_generator_id_unique UNIQUE (waste_generator_id);


--
-- Name: dim_waste_type dw_dim_waste_type_id_unique; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_waste_type
    ADD CONSTRAINT dw_dim_waste_type_id_unique UNIQUE (cawa_id);


--
-- Name: etl_process_log etl_process_log_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.etl_process_log
    ADD CONSTRAINT etl_process_log_pkey PRIMARY KEY (id);


--
-- Name: fact_pago fact_pago_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_pago
    ADD CONSTRAINT fact_pago_pkey PRIMARY KEY (id_fact_pago);


--
-- Name: fact_payment_traceability fact_payment_traceability_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_payment_traceability
    ADD CONSTRAINT fact_payment_traceability_pkey PRIMARY KEY (id_payment_trace);


--
-- Name: fact_project_environmental_impact fact_project_environmental_impact_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_project_environmental_impact
    ADD CONSTRAINT fact_project_environmental_impact_pkey PRIMARY KEY (sk_proyecto, sk_tiempo);


--
-- Name: fact_proyecto_geografia fact_proyecto_geografia_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_proyecto_geografia
    ADD CONSTRAINT fact_proyecto_geografia_pkey PRIMARY KEY (sk_proyecto, sk_geografia);


--
-- Name: fact_regularizacion fact_regularizacion_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_pkey PRIMARY KEY (id_fact);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- Name: roles roles_role_name_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.roles
    ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);


--
-- Name: dim_actividad uk_actividad; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_actividad
    ADD CONSTRAINT uk_actividad UNIQUE (codigo_actividad);


--
-- Name: dim_pago uk_dim_pago; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_pago
    ADD CONSTRAINT uk_dim_pago UNIQUE (tipo_pago, bank_code, transaction_type, sistema_origen);


--
-- Name: dim_estado uk_estado; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_estado
    ADD CONSTRAINT uk_estado UNIQUE (estado_proceso, estado_proyecto, estado_tramite);


--
-- Name: fact_pago uk_fact_pago_dedup; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_pago
    ADD CONSTRAINT uk_fact_pago_dedup UNIQUE (sk_proyecto, id_transaccion_origen, origen);


--
-- Name: dim_geografia uk_geo; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_geografia
    ADD CONSTRAINT uk_geo UNIQUE (provincia, canton, parroquia);


--
-- Name: fact_chemical_declaration unique_chemical_declaration; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_declaration
    ADD CONSTRAINT unique_chemical_declaration UNIQUE (sk_proyecto, importer_key, sk_tiempo, declaration_year, declaration_month);


--
-- Name: fact_chemical_import unique_chemical_import; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_import
    ADD CONSTRAINT unique_chemical_import UNIQUE (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number);


--
-- Name: fact_chemical_movement unique_chemical_movement; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_movement
    ADD CONSTRAINT unique_chemical_movement UNIQUE (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number);


--
-- Name: fact_waste_generation unique_waste_generation; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_waste_generation
    ADD CONSTRAINT unique_waste_generation UNIQUE (sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: inec_dpa_2024 inec_dpa_2024_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.inec_dpa_2024
    ADD CONSTRAINT inec_dpa_2024_pkey PRIMARY KEY (codigo_provincia);


--
-- Name: idx_bridge_capa; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_bridge_capa ON dw.bridge_interseccion_ambiental USING btree (sk_capa);


--
-- Name: idx_bridge_proyecto; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_bridge_proyecto ON dw.bridge_interseccion_ambiental USING btree (sk_proyecto);


--
-- Name: idx_dim_geo_nivel; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_dim_geo_nivel ON dw.dim_geografia USING btree (nivel);


--
-- Name: idx_dim_geo_padre; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_dim_geo_padre ON dw.dim_geografia USING btree (sk_padre);


--
-- Name: idx_dim_geografia_lookup; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_dim_geografia_lookup ON dw.dim_geografia USING btree (provincia, canton, parroquia);


--
-- Name: idx_fact_chem_date; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_chem_date ON dw.fact_chemical_application USING btree (sk_tiempo);


--
-- Name: idx_fact_chem_project; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_chem_project ON dw.fact_chemical_application USING btree (sk_proyecto);


--
-- Name: idx_fact_fecha; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_fecha ON dw.fact_regularizacion USING btree (sk_fecha_registro);


--
-- Name: idx_fact_geografia; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_geografia ON dw.fact_regularizacion USING btree (sk_geografia);


--
-- Name: idx_fact_imp_chem; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_imp_chem ON dw.fact_chemical_import USING btree (chemical_key);


--
-- Name: idx_fact_imp_date; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_imp_date ON dw.fact_chemical_import USING btree (sk_tiempo);


--
-- Name: idx_fact_imp_proj; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_imp_proj ON dw.fact_chemical_import USING btree (sk_proyecto);


--
-- Name: idx_fact_impact_date; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_impact_date ON dw.fact_project_environmental_impact USING btree (sk_tiempo);


--
-- Name: idx_fact_impact_project; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_impact_project ON dw.fact_project_environmental_impact USING btree (sk_proyecto);


--
-- Name: idx_fact_pago_fecha; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_pago_fecha ON dw.fact_pago USING btree (sk_fecha_pago);


--
-- Name: idx_fact_pago_origen; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_pago_origen ON dw.fact_pago USING btree (origen);


--
-- Name: idx_fact_pago_proyecto; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_pago_proyecto ON dw.fact_pago USING btree (sk_proyecto);


--
-- Name: idx_fact_pago_secuencia; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_pago_secuencia ON dw.fact_pago USING btree (numero_tramite, secuencia_pago);


--
-- Name: idx_fact_proyecto; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_proyecto ON dw.fact_regularizacion USING btree (sk_proyecto);


--
-- Name: idx_fact_regularizacion_proponente; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_regularizacion_proponente ON dw.fact_regularizacion USING btree (sk_proponente);


--
-- Name: idx_fact_waste_date; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_waste_date ON dw.fact_waste_generation USING btree (sk_tiempo);


--
-- Name: idx_fact_waste_geo_year; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_waste_geo_year ON dw.fact_waste_generation USING btree (geo_location_key, record_year);


--
-- Name: idx_fact_waste_proj_year; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_waste_proj_year ON dw.fact_waste_generation USING btree (sk_proyecto, record_year);


--
-- Name: idx_fact_waste_project; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_waste_project ON dw.fact_waste_generation USING btree (sk_proyecto);


--
-- Name: idx_fact_waste_type; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fact_waste_type ON dw.fact_waste_generation USING btree (waste_type_key);


--
-- Name: idx_fpg_geografia; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fpg_geografia ON dw.fact_proyecto_geografia USING btree (sk_geografia);


--
-- Name: idx_fpg_proyecto; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fpg_proyecto ON dw.fact_proyecto_geografia USING btree (sk_proyecto);


--
-- Name: idx_fpt_pago; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fpt_pago ON dw.fact_payment_traceability USING btree (sk_pago);


--
-- Name: idx_fpt_proyecto; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fpt_proyecto ON dw.fact_payment_traceability USING btree (sk_proyecto);


--
-- Name: idx_fpt_tiempo; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_fpt_tiempo ON dw.fact_payment_traceability USING btree (sk_tiempo);


--
-- Name: idx_mv_estado_proceso; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_mv_estado_proceso ON dw.mv_dashboard_regularizacion USING btree (estado_proceso);


--
-- Name: idx_mv_fecha_reg; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_mv_fecha_reg ON dw.mv_dashboard_regularizacion USING btree (fecha_registro);


--
-- Name: idx_mv_oficina; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_mv_oficina ON dw.mv_dashboard_regularizacion USING btree (oficina_tecnica);


--
-- Name: idx_mv_provincia; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_mv_provincia ON dw.mv_dashboard_regularizacion USING btree (provincia);


--
-- Name: idx_mv_tipo_permiso; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_mv_tipo_permiso ON dw.mv_dashboard_regularizacion USING btree (tipo_permiso_ambiental);


--
-- Name: idx_mv_zona_admin; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX idx_mv_zona_admin ON dw.mv_dashboard_regularizacion USING btree (zona_administrativa);


--
-- Name: idx_tmp_proj_code; Type: INDEX; Schema: stg; Owner: -
--

CREATE INDEX idx_tmp_proj_code ON stg.tmp_dim_proyecto_optimized USING btree (codigo_proyecto);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES dw.users(user_id);


--
-- Name: bridge_interseccion_ambiental bridge_interseccion_ambiental_sk_capa_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.bridge_interseccion_ambiental
    ADD CONSTRAINT bridge_interseccion_ambiental_sk_capa_fkey FOREIGN KEY (sk_capa) REFERENCES dw.dim_capa_ambiental(sk_capa);


--
-- Name: bridge_interseccion_ambiental bridge_interseccion_ambiental_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.bridge_interseccion_ambiental
    ADD CONSTRAINT bridge_interseccion_ambiental_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: dim_geografia dim_geografia_sk_padre_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_geografia
    ADD CONSTRAINT dim_geografia_sk_padre_fkey FOREIGN KEY (sk_padre) REFERENCES dw.dim_geografia(sk_geografia);


--
-- Name: fact_chemical_application fact_chemical_application_chemical_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_application
    ADD CONSTRAINT fact_chemical_application_chemical_key_fkey FOREIGN KEY (chemical_key) REFERENCES dw.dim_chemical_substance(chemical_key);


--
-- Name: fact_chemical_application fact_chemical_application_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_application
    ADD CONSTRAINT fact_chemical_application_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_chemical_application fact_chemical_application_sk_tiempo_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_application
    ADD CONSTRAINT fact_chemical_application_sk_tiempo_fkey FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_chemical_application fact_chemical_application_storage_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_application
    ADD CONSTRAINT fact_chemical_application_storage_key_fkey FOREIGN KEY (storage_key) REFERENCES dw.dim_chemical_storage(storage_key);


--
-- Name: fact_chemical_declaration fact_chemical_declaration_importer_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_declaration
    ADD CONSTRAINT fact_chemical_declaration_importer_key_fkey FOREIGN KEY (importer_key) REFERENCES dw.dim_chemical_importer(importer_key);


--
-- Name: fact_chemical_declaration fact_chemical_declaration_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_declaration
    ADD CONSTRAINT fact_chemical_declaration_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_chemical_declaration fact_chemical_declaration_sk_tiempo_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_declaration
    ADD CONSTRAINT fact_chemical_declaration_sk_tiempo_fkey FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_chemical_import fact_chemical_import_chemical_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_import
    ADD CONSTRAINT fact_chemical_import_chemical_key_fkey FOREIGN KEY (chemical_key) REFERENCES dw.dim_chemical_substance(chemical_key);


--
-- Name: fact_chemical_import fact_chemical_import_geo_location_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_import
    ADD CONSTRAINT fact_chemical_import_geo_location_key_fkey FOREIGN KEY (geo_location_key) REFERENCES dw.dim_geografia(sk_geografia);


--
-- Name: fact_chemical_import fact_chemical_import_importer_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_import
    ADD CONSTRAINT fact_chemical_import_importer_key_fkey FOREIGN KEY (importer_key) REFERENCES dw.dim_chemical_importer(importer_key);


--
-- Name: fact_chemical_import fact_chemical_import_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_import
    ADD CONSTRAINT fact_chemical_import_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_chemical_import fact_chemical_import_sk_tiempo_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_import
    ADD CONSTRAINT fact_chemical_import_sk_tiempo_fkey FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_chemical_movement fact_chemical_movement_chemical_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_movement
    ADD CONSTRAINT fact_chemical_movement_chemical_key_fkey FOREIGN KEY (chemical_key) REFERENCES dw.dim_chemical_substance(chemical_key);


--
-- Name: fact_chemical_movement fact_chemical_movement_importer_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_movement
    ADD CONSTRAINT fact_chemical_movement_importer_key_fkey FOREIGN KEY (importer_key) REFERENCES dw.dim_chemical_importer(importer_key);


--
-- Name: fact_chemical_movement fact_chemical_movement_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_movement
    ADD CONSTRAINT fact_chemical_movement_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_chemical_movement fact_chemical_movement_sk_tiempo_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_chemical_movement
    ADD CONSTRAINT fact_chemical_movement_sk_tiempo_fkey FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_pago fact_pago_sk_fecha_pago_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_pago
    ADD CONSTRAINT fact_pago_sk_fecha_pago_fkey FOREIGN KEY (sk_fecha_pago) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_pago fact_pago_sk_pago_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_pago
    ADD CONSTRAINT fact_pago_sk_pago_fkey FOREIGN KEY (sk_pago) REFERENCES dw.dim_pago(sk_pago);


--
-- Name: fact_pago fact_pago_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_pago
    ADD CONSTRAINT fact_pago_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_payment_traceability fact_payment_traceability_sk_pago_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_payment_traceability
    ADD CONSTRAINT fact_payment_traceability_sk_pago_fkey FOREIGN KEY (sk_pago) REFERENCES dw.dim_pago(sk_pago);


--
-- Name: fact_payment_traceability fact_payment_traceability_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_payment_traceability
    ADD CONSTRAINT fact_payment_traceability_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_payment_traceability fact_payment_traceability_sk_tiempo_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_payment_traceability
    ADD CONSTRAINT fact_payment_traceability_sk_tiempo_fkey FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_project_environmental_impact fact_project_environmental_impact_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_project_environmental_impact
    ADD CONSTRAINT fact_project_environmental_impact_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_project_environmental_impact fact_project_environmental_impact_sk_tiempo_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_project_environmental_impact
    ADD CONSTRAINT fact_project_environmental_impact_sk_tiempo_fkey FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_regularizacion fact_regularizacion_sk_actividad_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_actividad_fkey FOREIGN KEY (sk_actividad) REFERENCES dw.dim_actividad(sk_actividad);


--
-- Name: fact_regularizacion fact_regularizacion_sk_area_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_area_fkey FOREIGN KEY (sk_area) REFERENCES dw.dim_area(sk_area);


--
-- Name: fact_regularizacion fact_regularizacion_sk_estado_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_estado_fkey FOREIGN KEY (sk_estado) REFERENCES dw.dim_estado(sk_estado);


--
-- Name: fact_regularizacion fact_regularizacion_sk_fecha_registro_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_fecha_registro_fkey FOREIGN KEY (sk_fecha_registro) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_regularizacion fact_regularizacion_sk_geografia_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_geografia_fkey FOREIGN KEY (sk_geografia) REFERENCES dw.dim_geografia(sk_geografia);


--
-- Name: fact_regularizacion fact_regularizacion_sk_proponente_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_proponente_fkey FOREIGN KEY (sk_proponente) REFERENCES dw.dim_proponente(sk_proponente);


--
-- Name: fact_regularizacion fact_regularizacion_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_regularizacion fact_regularizacion_sk_usuario_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_regularizacion
    ADD CONSTRAINT fact_regularizacion_sk_usuario_fkey FOREIGN KEY (sk_usuario) REFERENCES dw.dim_usuario(sk_usuario);


--
-- Name: fact_waste_generation fact_waste_generation_danger_class_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_waste_generation
    ADD CONSTRAINT fact_waste_generation_danger_class_key_fkey FOREIGN KEY (danger_class_key) REFERENCES dw.dim_dangerous_classification(danger_class_key);


--
-- Name: fact_waste_generation fact_waste_generation_dangerous_waste_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_waste_generation
    ADD CONSTRAINT fact_waste_generation_dangerous_waste_key_fkey FOREIGN KEY (dangerous_waste_key) REFERENCES dw.dim_dangerous_waste(dangerous_waste_key);


--
-- Name: fact_waste_generation fact_waste_generation_sk_proyecto_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_waste_generation
    ADD CONSTRAINT fact_waste_generation_sk_proyecto_fkey FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto);


--
-- Name: fact_waste_generation fact_waste_generation_sk_tiempo_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_waste_generation
    ADD CONSTRAINT fact_waste_generation_sk_tiempo_fkey FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo);


--
-- Name: fact_waste_generation fact_waste_generation_waste_generator_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_waste_generation
    ADD CONSTRAINT fact_waste_generation_waste_generator_key_fkey FOREIGN KEY (waste_generator_key) REFERENCES dw.dim_waste_generator(waste_generator_key);


--
-- Name: fact_waste_generation fact_waste_generation_waste_type_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_waste_generation
    ADD CONSTRAINT fact_waste_generation_waste_type_key_fkey FOREIGN KEY (waste_type_key) REFERENCES dw.dim_waste_type(waste_type_key);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES dw.roles(role_id);


--
-- PostgreSQL database dump complete
--

\unrestrict jri35fG5TqrWxdPDt8w7rkqDhQ1pl5zd5wu05QydEh9EAY1PNsaoJIfkqpqfO3i

