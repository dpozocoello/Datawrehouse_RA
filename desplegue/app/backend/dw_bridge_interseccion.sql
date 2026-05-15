/*
 * SP: Carga de Tabla Puente de Intersecciones Ambientales (v1.4.1)
 * Autor: Antigravity AI
 * Descripción: Parsea la columna de texto consolidada del staging y puebla la relación N:M.
 */
CREATE OR REPLACE FUNCTION dw.sp_carga_puente_ambiental() RETURNS void AS $$ BEGIN -- Limpieza previa para carga total
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
$$ LANGUAGE plpgsql;