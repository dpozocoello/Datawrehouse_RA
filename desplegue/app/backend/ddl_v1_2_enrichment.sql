-- [v1.2] Enrichment of Areas Dimension with Geographic Hierarchy
-- 1. Modify staging table to include gelo_id
ALTER TABLE stg.suia_areas_bi
ADD COLUMN IF NOT EXISTS gelo_id INT;
-- 2. Create new staging table for geographical locations
CREATE TABLE IF NOT EXISTS stg.geographical_locations_bi (
    gelo_id INT,
    gelo_name VARCHAR(255),
    gelo_parent_id INT,
    gelo_codification_inec VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT NOW()
);
-- 3. Modify dimension table to include geographic hierarchy columns
ALTER TABLE dw.dim_area
ADD COLUMN IF NOT EXISTS provincia VARCHAR(100);
ALTER TABLE dw.dim_area
ADD COLUMN IF NOT EXISTS canton VARCHAR(100);
ALTER TABLE dw.dim_area
ADD COLUMN IF NOT EXISTS parroquia VARCHAR(100);
-- 4. Update sp_carga_dim_area to resolve the hierarchy
-- This updated version uses multiple joins to resolve Provincia -> Canton -> Parroquia
-- from the stg.geographical_locations_bi table.
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
            1 as depth,
            g.gelo_name as leaf_name
        FROM stg.suia_areas_bi s
            JOIN stg.geographical_locations_bi g ON s.gelo_id = g.gelo_id
        UNION ALL
        -- Recursive: Go up to parents
        SELECT gh.area_id,
            p.gelo_id,
            p.gelo_name,
            p.gelo_parent_id,
            gh.depth + 1,
            gh.leaf_name
        FROM geo_hierarchy gh
            JOIN stg.geographical_locations_bi p ON gh.gelo_parent_id = p.gelo_id
    ),
    resolved_geo AS (
        -- We resolve up to 3 levels: Parroquia (depth 1), Canton (depth 2), Provincia (depth 3)
        -- Note: This depends on how deep the gelo_id in areas is.
        -- If gelo_id is a Province, it will be depth 1 in our CTE.
        -- We'll use a safer approach: pivoting the hierarchy.
        SELECT area_id,
            MAX(
                CASE
                    WHEN depth = 1 THEN gelo_name
                END
            ) as level_1,
            MAX(
                CASE
                    WHEN depth = 2 THEN gelo_name
                END
            ) as level_2,
            MAX(
                CASE
                    WHEN depth = 3 THEN gelo_name
                END
            ) as level_3,
            MAX(
                CASE
                    WHEN depth = 4 THEN gelo_name
                END
            ) as level_4
        FROM geo_hierarchy
        GROUP BY area_id
    )
SELECT s.area_id,
    s.area_name,
    s.area_abbreviation,
    s.area_parent_id,
    'ZONA ' || s.zone_id::text,
    s.area_campus,
    -- Geography Logic:
    -- Level 4: Pais (ECUADOR)
    -- Level 3: Provincia
    -- Level 2: Canton
    -- Level 1: Parroquia (if exists)
    COALESCE(rg.level_3, rg.level_2, rg.level_1, 'N/A') as provincia,
    CASE
        WHEN rg.level_3 IS NOT NULL THEN rg.level_2
        WHEN rg.level_2 IS NOT NULL THEN rg.level_1
        ELSE 'N/A'
    END as canton,
    CASE
        WHEN rg.level_3 IS NOT NULL THEN rg.level_1
        ELSE 'N/A'
    END as parroquia,
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
RAISE NOTICE 'Dimensión Areas (v1.2) cargada exitosamente con jerarquía geográfica';
END;
$$ LANGUAGE plpgsql;