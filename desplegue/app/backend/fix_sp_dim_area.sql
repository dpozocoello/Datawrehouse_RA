-- [v1.2 FIX] Refined Hierarchy Resolution for Areas
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
            1 as depth
        FROM stg.suia_areas_bi s
            JOIN stg.geographical_locations_bi g ON s.gelo_id = g.gelo_id
        UNION ALL
        -- Recursive: Go up to parents
        SELECT gh.area_id,
            p.gelo_id,
            p.gelo_name,
            p.gelo_parent_id,
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
            ) as l5
        FROM geo_hierarchy
        GROUP BY area_id
    ),
    resolved_geo AS (
        SELECT area_id,
            -- Logic based on ECUADOR location
            CASE
                WHEN l5 = 'ECUADOR' THEN l4
                WHEN l4 = 'ECUADOR' THEN l3
                WHEN l3 = 'ECUADOR' THEN l2
                WHEN l2 = 'ECUADOR' THEN l1
                ELSE COALESCE(l1, 'N/A')
            END as prov,
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
    )
SELECT s.area_id,
    s.area_name,
    s.area_abbreviation,
    s.area_parent_id,
    'ZONA ' || s.zone_id::text,
    s.area_campus,
    COALESCE(rg.prov, 'N/A'),
    COALESCE(rg.cant, 'N/A'),
    COALESCE(rg.parr, 'N/A'),
    CASE
        WHEN s.area_status THEN 'ACTIVO'
        ELSE 'INACTIVO'
    END
FROM stg.suia_areas_bi s
    LEFT JOIN resolved_geo rg ON s.area_id = rg.area_id ON CONFLICT (id_area) DO
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
-- Ensure a default record for 0/N/A
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
RAISE NOTICE 'Dimensión Areas (v1.2 Fix) cargada exitosamente';
END;
$$ LANGUAGE plpgsql;