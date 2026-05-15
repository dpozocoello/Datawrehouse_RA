-- ==============================================================================
-- MIGRATION: dim_area v2.0
-- Fecha: 2026-05-06
-- Autor: Arquitectura de Datos — DWH Regularización Ambiental
-- Descripción:
--   1. Amplía stg.suia_areas_bi con campos faltantes de public.areas
--   2. Crea stg.suia_areas_types_bi (nuevo: catálogo de tipos de área)
--   3. Amplía dw.dim_area con tipo_area, nombre_area_padre, canton_directo y flags
--   4. Reemplaza dw.sp_carga_dim_area() con lógica v2.0
-- Brechas corregidas:
--   - areas_types NO estaba siendo extraída ni representada en dim_area
--   - 8 campos de public.areas no eran extraídos por TRX_10
--   - Auto-referencia (area_parent_id → areas) nunca se resolvía a nombre
--   - gelo_id_canton (FK directa al cantón) no se aprovechaba
-- ==============================================================================

-- ==============================================================================
-- 1. AMPLIAR stg.suia_areas_bi
-- ==============================================================================
ALTER TABLE stg.suia_areas_bi
    ADD COLUMN IF NOT EXISTS gelo_id_canton          integer,
    ADD COLUMN IF NOT EXISTS area_id_dp              varchar(100),
    ADD COLUMN IF NOT EXISTS area_ente_identification varchar(20),
    ADD COLUMN IF NOT EXISTS entity_type             varchar(20),
    ADD COLUMN IF NOT EXISTS area_issue              boolean,
    ADD COLUMN IF NOT EXISTS area_investment_project boolean,
    ADD COLUMN IF NOT EXISTS area_tracing            boolean,
    ADD COLUMN IF NOT EXISTS area_resolution_ministerial varchar(64);

-- ==============================================================================
-- 2. CREAR stg.suia_areas_types_bi (catálogo de tipos de área)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS stg.suia_areas_types_bi (
    arty_id          integer,
    arty_name        varchar(255),
    arty_abbreviation varchar(10),
    arty_status      boolean,
    fecha_carga      timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_suia_areas_types_bi_arty_id
    ON stg.suia_areas_types_bi (arty_id);

-- ==============================================================================
-- 3. AMPLIAR dw.dim_area
-- ==============================================================================
ALTER TABLE dw.dim_area
    ADD COLUMN IF NOT EXISTS tipo_area               varchar(255),
    ADD COLUMN IF NOT EXISTS siglas_tipo_area        varchar(10),
    ADD COLUMN IF NOT EXISTS nombre_area_padre       varchar(255),
    ADD COLUMN IF NOT EXISTS canton_directo          varchar(255),
    ADD COLUMN IF NOT EXISTS area_id_dp              varchar(100),
    ADD COLUMN IF NOT EXISTS area_ente_identification varchar(20),
    ADD COLUMN IF NOT EXISTS entity_type             varchar(20),
    ADD COLUMN IF NOT EXISTS es_emisora_aaa          boolean DEFAULT false,
    ADD COLUMN IF NOT EXISTS es_seguimiento_aaa      boolean DEFAULT false,
    ADD COLUMN IF NOT EXISTS es_proyecto_inversion   boolean DEFAULT false,
    ADD COLUMN IF NOT EXISTS area_resolution_ministerial varchar(64);

-- ==============================================================================
-- 4. REEMPLAZAR dw.sp_carga_dim_area() — v2.0
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_area()
RETURNS void
LANGUAGE plpgsql AS $$
BEGIN

INSERT INTO dw.dim_area (
    id_area,
    nombre_area,
    abreviatura_area,
    id_area_padre,
    zona,
    campus,
    provincia,
    canton,
    canton_directo,
    parroquia,
    estado_area,
    tipo_area,
    siglas_tipo_area,
    nombre_area_padre,
    area_id_dp,
    area_ente_identification,
    entity_type,
    es_emisora_aaa,
    es_seguimiento_aaa,
    es_proyecto_inversion,
    area_resolution_ministerial
)
WITH RECURSIVE

-- ----------------------------------------------------------------
-- CTE-1: Jerarquía geográfica recursiva desde gelo_id (provincia)
-- ----------------------------------------------------------------
geo_hierarchy AS (
    SELECT s.area_id,
           g.gelo_id,
           g.gelo_name,
           g.gelo_parent_id,
           g.gelo_codification_inec,
           1 AS depth
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

-- ----------------------------------------------------------------
-- CTE-2: Pivot jerarquía en niveles l1..l5
-- ----------------------------------------------------------------
pivoted_geo AS (
    SELECT area_id,
        MAX(CASE WHEN depth = 1 THEN gelo_name END)             AS l1,
        MAX(CASE WHEN depth = 2 THEN gelo_name END)             AS l2,
        MAX(CASE WHEN depth = 3 THEN gelo_name END)             AS l3,
        MAX(CASE WHEN depth = 4 THEN gelo_name END)             AS l4,
        MAX(CASE WHEN depth = 5 THEN gelo_name END)             AS l5,
        MAX(CASE WHEN depth = 1 THEN gelo_codification_inec END) AS inec_l1,
        MAX(CASE WHEN depth = 2 THEN gelo_codification_inec END) AS inec_l2,
        MAX(CASE WHEN depth = 3 THEN gelo_codification_inec END) AS inec_l3,
        MAX(CASE WHEN depth = 4 THEN gelo_codification_inec END) AS inec_l4,
        MAX(CASE WHEN depth = 5 THEN gelo_codification_inec END) AS inec_l5
    FROM geo_hierarchy
    GROUP BY area_id
),

-- ----------------------------------------------------------------
-- CTE-3: Resolución de nivel geográfico (normaliza quién es provincia)
-- ----------------------------------------------------------------
resolved_geo AS (
    SELECT area_id,
        CASE
            WHEN l5 = 'ECUADOR' THEN l4
            WHEN l4 = 'ECUADOR' THEN l3
            WHEN l3 = 'ECUADOR' THEN l2
            WHEN l2 = 'ECUADOR' THEN l1
            ELSE COALESCE(l1, 'N/A')
        END AS prov_raw,
        CASE
            WHEN l5 = 'ECUADOR' THEN inec_l4
            WHEN l4 = 'ECUADOR' THEN inec_l3
            WHEN l3 = 'ECUADOR' THEN inec_l2
            WHEN l2 = 'ECUADOR' THEN inec_l1
            ELSE NULL
        END AS inec_prov,
        CASE
            WHEN l5 = 'ECUADOR' THEN l3
            WHEN l4 = 'ECUADOR' THEN l2
            WHEN l3 = 'ECUADOR' THEN l1
            ELSE 'N/A'
        END AS cant,
        CASE
            WHEN l5 = 'ECUADOR' THEN l2
            WHEN l4 = 'ECUADOR' THEN l1
            ELSE 'N/A'
        END AS parr
    FROM pivoted_geo
),

-- ----------------------------------------------------------------
-- CTE-4: Join con INEC para nombre canónico de provincia
-- ----------------------------------------------------------------
expert_geo AS (
    SELECT rg.area_id,
        COALESCE(
            i.nombre_provincia,
            CASE
                WHEN rg.inec_prov = '90' AND rg.prov_raw ILIKE '%SALITRE%' THEN 'GUAYAS'
                ELSE 'N/A'
            END
        ) AS prov_final,
        rg.cant,
        rg.parr
    FROM resolved_geo rg
    LEFT JOIN ref.inec_dpa_2024 i ON rg.inec_prov = i.codigo_provincia
),

-- ----------------------------------------------------------------
-- CTE-5 (NUEVO): Resolución directa de cantón desde gelo_id_canton
-- Más confiable que la jerarquía recursiva para oficinas técnicas
-- ----------------------------------------------------------------
canton_directo_cte AS (
    SELECT s.area_id,
           gc.gelo_name AS canton_directo_nombre
    FROM stg.suia_areas_bi s
    JOIN stg.geographical_locations_bi gc ON s.gelo_id_canton = gc.gelo_id
    WHERE s.gelo_id_canton IS NOT NULL
),

-- ----------------------------------------------------------------
-- CTE-6 (NUEVO): Resolución auto-referencial padre → nombre
-- Resuelve area_parent_id a nombre para jerarquía OT → DZ → DP
-- ----------------------------------------------------------------
area_padre_cte AS (
    SELECT
        hijo.area_id,
        padre.area_name AS nombre_padre
    FROM stg.suia_areas_bi hijo
    JOIN stg.suia_areas_bi padre ON hijo.area_parent_id = padre.area_id
    WHERE hijo.area_parent_id IS NOT NULL
),

-- ----------------------------------------------------------------
-- CTE-7 (NUEVO): Tipo de área desde areas_types
-- ----------------------------------------------------------------
tipo_area_cte AS (
    SELECT
        s.area_id,
        t.arty_name        AS tipo_area,
        t.arty_abbreviation AS siglas_tipo_area
    FROM stg.suia_areas_bi s
    JOIN stg.suia_areas_types_bi t ON s.arty_id = t.arty_id
    WHERE t.arty_status = true
),

-- ----------------------------------------------------------------
-- CTE-8: Ensamble final
-- ----------------------------------------------------------------
final_geo AS (
    SELECT
        s.area_id,
        s.area_name,
        s.area_abbreviation,
        s.area_parent_id,
        'ZONA ' || s.zone_id::text              AS zona_str,
        s.area_campus,
        COALESCE(eg.prov_final, 'N/A')          AS prov_res,
        COALESCE(eg.cant, 'N/A')                AS cant_res,
        COALESCE(cd.canton_directo_nombre, 'N/A') AS cant_directo_res,
        COALESCE(eg.parr, 'N/A')                AS parr_res,
        s.area_status,
        COALESCE(ta.tipo_area,        'N/A')    AS tipo_area,
        COALESCE(ta.siglas_tipo_area, 'N/A')    AS siglas_tipo_area,
        COALESCE(ap.nombre_padre,     'N/A')    AS nombre_padre,
        s.area_id_dp,
        s.area_ente_identification,
        s.entity_type,
        COALESCE(s.area_issue,              false) AS area_issue,
        COALESCE(s.area_tracing,            false) AS area_tracing,
        COALESCE(s.area_investment_project, false) AS area_investment_project,
        s.area_resolution_ministerial
    FROM stg.suia_areas_bi s
    LEFT JOIN expert_geo      eg ON s.area_id = eg.area_id
    LEFT JOIN canton_directo_cte cd ON s.area_id = cd.area_id
    LEFT JOIN area_padre_cte  ap ON s.area_id = ap.area_id
    LEFT JOIN tipo_area_cte   ta ON s.area_id = ta.area_id
)

-- ----------------------------------------------------------------
-- INSERT con UPSERT
-- ----------------------------------------------------------------
SELECT
    f.area_id,
    f.area_name,
    f.area_abbreviation,
    f.area_parent_id,
    f.zona_str,
    f.area_campus,

    -- [v1.4 EXPERT INFERENCE ENGINE] Fallback para 75 áreas sin gelo_id
    CASE WHEN f.prov_res = 'N/A' THEN
        CASE f.area_id
            WHEN 1115 THEN 'AZUAY'              -- OT URDANETA OÑA
            WHEN 1261 THEN 'PICHINCHA'           -- OT DZ 10
            WHEN 555  THEN 'PICHINCHA'           -- CONELEC
            WHEN 1080 THEN 'MANABÍ'              -- DZ 4
            WHEN 1081 THEN 'ESMERALDAS'          -- DZ 2
            WHEN 178  THEN 'PICHINCHA'           -- UEA SECRETARÍA AMBIENTE
            WHEN 1    THEN 'ZONAS NO DELIMITADAS'
            WHEN 1062 THEN 'LOJA'                -- Cuenca Puyango
            WHEN 1258 THEN 'CHIMBORAZO'          -- OT DZ 3
            WHEN 1257 THEN 'GUAYAS'              -- OT DZ 8
            WHEN 1256 THEN 'IMBABURA'            -- OT DZ 1
            WHEN 1253 THEN 'NAPO'                -- OT DZ 2
            WHEN 1252 THEN 'MANABI'              -- OT DZ 4
            WHEN 1255 THEN 'LOJA'                -- OT DZ 7
            WHEN 1254 THEN 'GUAYAS'              -- OT DZ 5
            WHEN 1259 THEN 'AZUAY'               -- OT DZ 6
            WHEN 1260 THEN 'PICHINCHA'           -- OT DZ 9
            WHEN 1082 THEN 'GUAYAS'              -- DZ 5
            WHEN 1083 THEN 'LOJA'                -- DZ 7
            WHEN 1084 THEN 'IMBABURA'            -- DZ 1
            WHEN 1085 THEN 'NAPO'                -- DZ 8
            WHEN 1086 THEN 'CHIMBORAZO'          -- DZ 3
            WHEN 1087 THEN 'AZUAY'               -- DZ 6
            WHEN 1088 THEN 'SUCUMBIOS'           -- DZ 9
            WHEN 1089 THEN 'ZAMORA CHINCHIPE'    -- DZ 10
            WHEN 1139 THEN 'PICHINCHA'           -- DIR. REGULARIZACIÓN AMBIENTAL
            WHEN 1124 THEN 'COTOPAXI'            -- OT LATACUNGA
            WHEN 1090 THEN 'MANABÍ'              -- OT PEDERNALES
            WHEN 1092 THEN 'MANABÍ'              -- OT PORTOVIEJO
            WHEN 1095 THEN 'ESMERALDAS'          -- OT ELOY ALFARO
            WHEN 1129 THEN 'AZUAY'               -- OT CUENCA
            WHEN 1106 THEN 'GUAYAS'              -- OT GUAYAQUIL
            WHEN 1251 THEN 'LOJA'                -- OT ZAPOTILLO
            WHEN 1094 THEN 'ESMERALDAS'          -- OT ESMERALDAS
            WHEN 1091 THEN 'MANABÍ'              -- OT CHONE
            WHEN 1093 THEN 'MANABÍ'              -- OT JIPIJAPA
            WHEN 1098 THEN 'ESMERALDAS'          -- OT MUISNE
            WHEN 239  THEN 'MANABÍ'
            WHEN 244  THEN 'AZUAY'
            WHEN 1107 THEN 'GUAYAS'              -- OT NARANJAL
            WHEN 1112 THEN 'LOJA'                -- OT PUYANGO
            WHEN 1097 THEN 'ESMERALDAS'          -- OT QUININDÉ
            WHEN 1113 THEN 'LOJA'                -- OT CATAMAYO
            WHEN 1127 THEN 'MORONA SANTIAGO'     -- OT MORONA
            WHEN 1096 THEN 'ESMERALDAS'          -- OT SAN LORENZO
            WHEN 1099 THEN 'SANTO DOMINGO DE LOS TSACHILAS' -- OT SANTO DOMINGO
            WHEN 1101 THEN 'PICHINCHA'           -- OT CAYAMBE
            WHEN 1100 THEN 'PICHINCHA'           -- OT SAN MIGUEL DE LOS BANCOS
            WHEN 1103 THEN 'PICHINCHA'           -- OT MEJÍA
            WHEN 1102 THEN 'PICHINCHA'           -- OT QUITO
            WHEN 1117 THEN 'CARCHI'              -- OT TULCÁN
            WHEN 1118 THEN 'IMBABURA'            -- OT IBARRA
            WHEN 1120 THEN 'NAPO'                -- OT TENA
            WHEN 1119 THEN 'ORELLANA'            -- OT ORELLANA
            WHEN 1126 THEN 'PASTAZA'             -- OT PASTAZA
            WHEN 1123 THEN 'TUNGURAHUA'          -- OT AMBATO
            WHEN 1121 THEN 'CHIMBORAZO'          -- OT ALAUSÍ
            WHEN 1130 THEN 'CAÑAR'               -- OT AZOGUES
            WHEN 1122 THEN 'CHIMBORAZO'          -- OT RIOBAMBA
            WHEN 1125 THEN 'COTOPAXI'            -- OT LA MANÁ
            WHEN 1104 THEN 'SANTA ELENA'         -- OT SANTA ELENA
            WHEN 1108 THEN 'LOS RIOS'            -- OT BABAHOYO
            WHEN 1109 THEN 'LOS RIOS'            -- OT QUEVEDO
            WHEN 1105 THEN 'BOLIVAR'             -- OT GUARANDA
            WHEN 1116 THEN 'AZUAY'               -- OT SANTA ISABEL
            WHEN 1114 THEN 'LOJA'                -- OT MACARÁ
            WHEN 1110 THEN 'EL ORO'              -- OT MACHALA
            WHEN 1111 THEN 'EL ORO'              -- OT ZARUMA
            WHEN 1131 THEN 'CAÑAR'               -- OT CAÑAR
            WHEN 1128 THEN 'MORONA SANTIAGO'     -- OT TAISHA
            WHEN 1132 THEN 'SUCUMBIOS'           -- OT LAGO AGRIO
            WHEN 1134 THEN 'ZAMORA CHINCHIPE'    -- OT PALANDA
            WHEN 1133 THEN 'ZAMORA CHINCHIPE'    -- OT ZAMORA
            WHEN 1135 THEN 'MORONA SANTIAGO'     -- OT GUALAQUIZA
            WHEN 1136 THEN 'LOJA'                -- OT LOJA
            ELSE 'N/A'
        END
    ELSE f.prov_res END                          AS provincia,

    -- Cantón: prioriza gelo_id_canton (FK directa) > jerarquía recursiva > expert fallback
    CASE
        WHEN f.cant_directo_res <> 'N/A' THEN f.cant_directo_res
        WHEN f.cant_res <> 'N/A'         THEN f.cant_res
        WHEN f.prov_res = 'N/A' THEN
            CASE f.area_id
                WHEN 1115 THEN 'OÑA'
                WHEN 1261 THEN 'QUITO'
                WHEN 555  THEN 'QUITO'
                WHEN 1080 THEN 'PORTOVIEJO'
                WHEN 1081 THEN 'ESMERALDAS'
                WHEN 178  THEN 'QUITO'
                WHEN 1    THEN 'ZONAS NO DELIMITADAS'
                WHEN 1062 THEN 'PUYANGO'
                WHEN 1258 THEN 'RIOBAMBA'
                WHEN 1257 THEN 'GUAYAQUIL'
                WHEN 1256 THEN 'IBARRA'
                WHEN 1253 THEN 'TENA'
                WHEN 1252 THEN 'PORTOVIEJO'
                WHEN 1255 THEN 'LOJA'
                WHEN 1254 THEN 'GUAYAQUIL'
                WHEN 1259 THEN 'CUENCA'
                WHEN 1260 THEN 'QUITO'
                WHEN 1082 THEN 'GUAYAQUIL'
                WHEN 1083 THEN 'LOJA'
                WHEN 1084 THEN 'IBARRA'
                WHEN 1085 THEN 'TENA'
                WHEN 1086 THEN 'RIOBAMBA'
                WHEN 1087 THEN 'CUENCA'
                WHEN 1088 THEN 'LAGO AGRIO'
                WHEN 1089 THEN 'CHINCHIPE'
                WHEN 1139 THEN 'QUITO'
                WHEN 1124 THEN 'LATACUNGA'
                WHEN 1090 THEN 'PEDERNALES'
                WHEN 1092 THEN 'PORTOVIEJO'
                WHEN 1095 THEN 'ELOY ALFARO'
                WHEN 1129 THEN 'CUENCA'
                WHEN 1106 THEN 'GUAYAQUIL'
                WHEN 1251 THEN 'ZAPOTILLO'
                WHEN 1094 THEN 'ESMERALDAS'
                WHEN 1091 THEN 'CHONE'
                WHEN 1093 THEN 'JIPIJAPA'
                WHEN 1098 THEN 'MUISNE'
                WHEN 239  THEN 'PICHINCHA'
                WHEN 244  THEN 'CUENCA'
                WHEN 1107 THEN 'NARANJAL'
                WHEN 1112 THEN 'PUYANGO'
                WHEN 1097 THEN 'QUININDE'
                WHEN 1113 THEN 'CATAMAYO'
                WHEN 1127 THEN 'MORONA'
                WHEN 1096 THEN 'SAN LORENZO'
                WHEN 1099 THEN 'SANTO DOMINGO'
                WHEN 1101 THEN 'CAYAMBE'
                WHEN 1100 THEN 'SAN MIGUEL DE LOS BANCOS'
                WHEN 1103 THEN 'MEJIA'
                WHEN 1102 THEN 'QUITO'
                WHEN 1117 THEN 'TULCAN'
                WHEN 1118 THEN 'IBARRA'
                WHEN 1120 THEN 'TENA'
                WHEN 1119 THEN 'ORELLANA'
                WHEN 1126 THEN 'PASTAZA'
                WHEN 1123 THEN 'AMBATO'
                WHEN 1121 THEN 'ALAUSI'
                WHEN 1130 THEN 'AZOGUES'
                WHEN 1122 THEN 'RIOBAMBA'
                WHEN 1125 THEN 'LA MANÁ'
                WHEN 1104 THEN 'SANTA ELENA'
                WHEN 1108 THEN 'BABAHOYO'
                WHEN 1109 THEN 'QUEVEDO'
                WHEN 1105 THEN 'GUARANDA'
                WHEN 1116 THEN 'SANTA ISABEL'
                WHEN 1114 THEN 'MACARA'
                WHEN 1110 THEN 'MACHALA'
                WHEN 1111 THEN 'ZARUMA'
                WHEN 1131 THEN 'CAÑAR'
                WHEN 1128 THEN 'TAISHA'
                WHEN 1132 THEN 'LAGO AGRIO'
                WHEN 1134 THEN 'PALANDA'
                WHEN 1133 THEN 'ZAMORA'
                WHEN 1135 THEN 'GUALAQUIZA'
                WHEN 1136 THEN 'LOJA'
                ELSE 'N/A'
            END
        ELSE 'N/A'
    END                                          AS canton,

    -- canton_directo: FK directa a geographical_locations via gelo_id_canton
    f.cant_directo_res                           AS canton_directo,

    f.parr_res                                   AS parroquia,
    CASE WHEN f.area_status THEN 'ACTIVO' ELSE 'INACTIVO' END AS estado_area,
    f.tipo_area,
    f.siglas_tipo_area,
    f.nombre_padre                               AS nombre_area_padre,
    f.area_id_dp,
    f.area_ente_identification,
    f.entity_type,
    f.area_issue                                 AS es_emisora_aaa,
    f.area_tracing                               AS es_seguimiento_aaa,
    f.area_investment_project                    AS es_proyecto_inversion,
    f.area_resolution_ministerial

FROM final_geo f
ON CONFLICT (id_area) DO UPDATE SET
    nombre_area               = EXCLUDED.nombre_area,
    abreviatura_area          = EXCLUDED.abreviatura_area,
    id_area_padre             = EXCLUDED.id_area_padre,
    zona                      = EXCLUDED.zona,
    campus                    = EXCLUDED.campus,
    provincia                 = EXCLUDED.provincia,
    canton                    = EXCLUDED.canton,
    canton_directo            = EXCLUDED.canton_directo,
    parroquia                 = EXCLUDED.parroquia,
    estado_area               = EXCLUDED.estado_area,
    tipo_area                 = EXCLUDED.tipo_area,
    siglas_tipo_area          = EXCLUDED.siglas_tipo_area,
    nombre_area_padre         = EXCLUDED.nombre_area_padre,
    area_id_dp                = EXCLUDED.area_id_dp,
    area_ente_identification  = EXCLUDED.area_ente_identification,
    entity_type               = EXCLUDED.entity_type,
    es_emisora_aaa            = EXCLUDED.es_emisora_aaa,
    es_seguimiento_aaa        = EXCLUDED.es_seguimiento_aaa,
    es_proyecto_inversion     = EXCLUDED.es_proyecto_inversion,
    area_resolution_ministerial = EXCLUDED.area_resolution_ministerial,
    fecha_carga               = NOW();

-- Registro especial SK=0 (sin área definida)
INSERT INTO dw.dim_area (
    id_area, nombre_area, estado_area, tipo_area,
    siglas_tipo_area, nombre_area_padre,
    provincia, canton, canton_directo, parroquia
) VALUES (
    0, 'AREA NO DEFINIDA', 'N/A', 'N/A',
    'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A'
) ON CONFLICT (id_area) DO NOTHING;

RAISE NOTICE 'sp_carga_dim_area() v2.0 ejecutada: tipo_area, canton_directo, nombre_area_padre y flags operacionales incluidos.';

END;
$$;
