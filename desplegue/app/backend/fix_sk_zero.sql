-- Fix for surrogate key 0 in dim_area
-- We need to allow inserting 0 into the SERIAL column and ensure it exists.
-- 1. Ensure the N/A record exists with sk_area = 0
-- We might need to temporarily disable the sequence or just insert it explicitly.
INSERT INTO dw.dim_area (sk_area, id_area, nombre_area, estado_area)
VALUES (0, 0, 'AREA NO DEFINIDA', 'N/A') ON CONFLICT (id_area) DO
UPDATE
SET nombre_area = EXCLUDED.nombre_area,
    estado_area = EXCLUDED.estado_area;
-- If there's a conflict on sk_area (unlikely if it's 0), we'd need to handle it.
-- But since sk_area is the PK, if sk_area 0 already exists but with a different id_area, that's a problem.
-- Let's just be clean:
DELETE FROM dw.dim_area
WHERE sk_area = 0
    OR id_area = 0;
INSERT INTO dw.dim_area (sk_area, id_area, nombre_area, estado_area)
VALUES (0, 0, 'AREA NO DEFINIDA', 'N/A');
-- 2. Update the Stored Procedure to be more robust
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_area() RETURNS void AS $$ BEGIN
INSERT INTO dw.dim_area (
        id_area,
        nombre_area,
        abreviatura_area,
        id_area_padre,
        zona,
        campus,
        estado_area
    )
SELECT area_id,
    area_name,
    area_abbreviation,
    area_parent_id,
    'ZONA ' || zone_id::text,
    area_campus,
    CASE
        WHEN area_status THEN 'ACTIVO'
        ELSE 'INACTIVO'
    END
FROM stg.suia_areas_bi ON CONFLICT (id_area) DO
UPDATE
SET nombre_area = EXCLUDED.nombre_area,
    abreviatura_area = EXCLUDED.abreviatura_area,
    id_area_padre = EXCLUDED.id_area_padre,
    zona = EXCLUDED.zona,
    campus = EXCLUDED.campus,
    estado_area = EXCLUDED.estado_area,
    fecha_carga = NOW();
-- Ensure a default record for 0/N/A (redundant but safe)
IF NOT EXISTS (
    SELECT 1
    FROM dw.dim_area
    WHERE sk_area = 0
) THEN
INSERT INTO dw.dim_area (sk_area, id_area, nombre_area, estado_area)
VALUES (0, 0, 'AREA NO DEFINIDA', 'N/A');
END IF;
RAISE NOTICE 'Dimensión Areas cargada exitosamente';
END;
$$ LANGUAGE plpgsql;