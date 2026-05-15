-- [v1.3.1 EXPERT] Enhanced Hierarchy Resolution with Administrative Zone Mapping
-- Fase A: Normalización contra el Catálogo Nacional y Corrección de Anomalías zonales
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
        -- Base: Locations linked directly to areas
        SELECT s.area_id,
            g.gelo_id,
            g.gelo_name,
            g.gelo_parent_id,
            g.gelo_codification_inec,
            1 as depth
        FROM stg.suia_areas_bi s
            JOIN stg.geographical_locations_bi g ON s.gelo_id = g.gelo_id
        UNION ALL
        -- Recursive: Go up to parents
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
            MAX(
                CASE
                    WHEN depth = 1 THEN gelo_name
                END
            ) as l1,
            MAX(
                CASE
                    WHEN depth = 2 THEN gelo_name
                END
            ) as l2,
            MAX(
                CASE
                    WHEN depth = 3 THEN gelo_name
                END
            ) as l3,
            MAX(
                CASE
                    WHEN depth = 4 THEN gelo_name
                END
            ) as l4,
            MAX(
                CASE
                    WHEN depth = 5 THEN gelo_name
                END
            ) as l5,
            MAX(
                CASE
                    WHEN depth = 1 THEN gelo_codification_inec
                END
            ) as inec_l1,
            MAX(
                CASE
                    WHEN depth = 2 THEN gelo_codification_inec
                END
            ) as inec_l2,
            MAX(
                CASE
                    WHEN depth = 3 THEN gelo_codification_inec
                END
            ) as inec_l3,
            MAX(
                CASE
                    WHEN depth = 4 THEN gelo_codification_inec
                END
            ) as inec_l4,
            MAX(
                CASE
                    WHEN depth = 5 THEN gelo_codification_inec
                END
            ) as inec_l5
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
                    WHEN rg.inec_prov = '90'
                    AND rg.prov_raw ILIKE '%SALITRE%' THEN 'GUAYAS'
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
            'ZONA ' || s.zone_id::text as zona,
            s.area_campus,
            -- Core mapping
            COALESCE(eg.prov_final, 'N/A') as prov_temp,
            COALESCE(eg.cant, 'N/A') as cant_temp,
            COALESCE(eg.parr, 'N/A') as parr_temp,
            s.zone_id,
            s.area_status
        FROM stg.suia_areas_bi s
            LEFT JOIN expert_geo eg ON s.area_id = eg.area_id
    )
SELECT area_id,
    area_name,
    area_abbreviation,
    area_parent_id,
    zona,
    area_campus,
    -- Apply fallback for Zonal mapping [v1.3.1]
    CASE
        WHEN prov_temp = 'N/A'
        AND area_name ILIKE '%ZONAL%' THEN CASE
            WHEN zone_id = 1 THEN 'IMBABURA'
            WHEN zone_id = 2 THEN 'NAPO'
            WHEN zone_id = 3 THEN 'CHIMBORAZO'
            WHEN zone_id = 4 THEN 'MANABI'
            WHEN zone_id = 5 THEN 'GUAYAS'
            WHEN zone_id = 6 THEN 'AZUAY'
            WHEN zone_id = 7 THEN 'LOJA'
            WHEN zone_id = 8 THEN 'GUAYAS'
            WHEN zone_id = 9 THEN 'PICHINCHA'
            ELSE 'N/A'
        END
        ELSE prov_temp
    END as provincia,
    CASE
        WHEN prov_temp = 'N/A'
        AND area_name ILIKE '%ZONAL%' THEN CASE
            WHEN zone_id = 1 THEN 'IBARRA'
            WHEN zone_id = 2 THEN 'TENA'
            WHEN zone_id = 3 THEN 'RIOBAMBA'
            WHEN zone_id = 4 THEN 'PORTOVIEJO'
            WHEN zone_id = 5 THEN 'GUAYAQUIL'
            WHEN zone_id = 6 THEN 'CUENCA'
            WHEN zone_id = 7 THEN 'LOJA'
            WHEN zone_id = 8 THEN 'GUAYAQUIL'
            WHEN zone_id = 9 THEN 'QUITO'
            ELSE 'N/A'
        END
        ELSE cant_temp
    END as canton,
    parr_temp as parroquia,
    CASE
        WHEN area_status THEN 'ACTIVO'
        ELSE 'INACTIVO'
    END as estado_area
FROM final_geo ON CONFLICT (id_area) DO
UPDATE
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
-- Standard SK=0
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_area
    WHERE id_area = 0
) THEN
INSERT INTO dw.dim_area (
        id_area,
        nombre_area,
        estado_area,
        provincia,
        canton,
        parroquia
    )
VALUES (
        0,
        'AREA NO DEFINIDA',
        'N/A',
        'N/A',
        'N/A',
        'N/A'
    );
END IF;
RAISE NOTICE 'Dimensión Areas (v1.3.1 Expert Zonal Fix) cargada exitosamente';
END;
$$ LANGUAGE plpgsql;