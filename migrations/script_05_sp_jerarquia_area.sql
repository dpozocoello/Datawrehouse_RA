-- ============================================================================
-- SCRIPT 05 — SP: dw.sp_carga_jerarquia_area() v1.0
-- Base de datos: dw_reg_v1
-- Ejecutar en: DBeaver conectado a localhost:5432 / postgres / dw_reg_v1
--
-- Descripción:
--   Materializa la jerarquía recursiva de public.areas (SUIA) en:
--     1. dw.dim_area     — columnas nivel_jerarquico, L1, L2, ruta, es_hoja
--     2. dw.bridge_area_jerarquia — tabla Kimball con todos los pares
--                                   ancestro↔descendiente + distancia
--
-- Dependencias:
--   - Script 04 aplicado (columnas y bridge table creados)
--   - stg.suia_areas_bi     poblada (TRX_10_AREAS ejecutado)
--   - stg.suia_areas_types_bi poblada (TRX_10B_AREAS_TYPES ejecutado)
--   - dw.dim_area            poblada (sp_carga_dim_area ejecutado)
--
-- Prerrequisito de orden en ETL:
--   paso 15 (SP_CARGA_DIM_AREA) → paso 16 (SP_JERARQUIA_AREA)
-- ============================================================================

CREATE OR REPLACE FUNCTION dw.sp_carga_jerarquia_area()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_dim_actualizadas  INTEGER := 0;
    v_bridge_self       INTEGER := 0;
    v_bridge_padre      INTEGER := 0;
    v_bridge_abuelo     INTEGER := 0;
    v_msg               TEXT;
BEGIN

    -- =========================================================================
    -- GUARDIA: validar que staging tiene datos
    -- =========================================================================
    IF (SELECT COUNT(*) FROM stg.suia_areas_bi) = 0 THEN
        RAISE WARNING '[sp_carga_jerarquia_area] stg.suia_areas_bi está vacía — abortando.';
        RETURN 'ADVERTENCIA: staging vacío, no se actualizó dim_area ni bridge.';
    END IF;

    -- =========================================================================
    -- PASO 1: Resolver jerarquía desde staging y actualizar dw.dim_area
    --
    -- CTE recursiva que recorre public.areas hasta 10 niveles de profundidad.
    -- Para cada nodo produce:
    --   nivel    : 1 (raíz) | 2 (hijo) | 3 (nieto)
    --   l1_*     : ancestro de nivel 1 (siempre el mismo para toda la rama)
    --   l2_*     : ancestro de nivel 2 (NULL si el nodo es raíz)
    --   ruta_ids : "100" | "100/278" | "100/278/999"
    --   ruta_nombres : breadcrumb legible
    --   es_hoja  : TRUE si el nodo no tiene hijos en staging
    -- =========================================================================
    WITH RECURSIVE hier AS (

        -- Nodos raíz (nivel 1 — sin padre)
        SELECT
            a.area_id,
            a.area_parent_id,
            CAST(1                                           AS SMALLINT) AS nivel,
            a.area_id                                                      AS l1_id,
            CAST(a.area_name                                AS TEXT)       AS l1_nombre,
            CAST(COALESCE(t.arty_abbreviation, 'N/A')       AS TEXT)       AS l1_tipo,
            CAST(NULL                                        AS INTEGER)    AS l2_id,
            CAST(NULL                                        AS TEXT)       AS l2_nombre,
            CAST(NULL                                        AS TEXT)       AS l2_tipo,
            CAST(a.area_id::TEXT                             AS TEXT)       AS ruta_ids,
            CAST(a.area_name                                 AS TEXT)       AS ruta_nombres
        FROM stg.suia_areas_bi a
        LEFT JOIN stg.suia_areas_types_bi t ON a.arty_id = t.arty_id
        WHERE a.area_parent_id IS NULL

        UNION ALL

        -- Nodos hijo / nieto (niveles 2 y 3)
        SELECT
            a.area_id,
            a.area_parent_id,
            CAST(h.nivel + 1                                         AS SMALLINT),
            h.l1_id,
            h.l1_nombre,
            h.l1_tipo,
            -- l2_* se establece cuando el padre es nivel 1
            CAST(CASE WHEN h.nivel = 1 THEN a.area_id    ELSE h.l2_id      END AS INTEGER),
            CAST(CASE WHEN h.nivel = 1 THEN a.area_name  ELSE h.l2_nombre   END AS TEXT),
            CAST(CASE WHEN h.nivel = 1
                      THEN COALESCE(t.arty_abbreviation, 'N/A')
                      ELSE h.l2_tipo
                 END AS TEXT),
            CAST(h.ruta_ids    || '/' || a.area_id   AS TEXT),
            CAST(h.ruta_nombres || ' > ' || a.area_name AS TEXT)
        FROM stg.suia_areas_bi a
        LEFT JOIN stg.suia_areas_types_bi t ON a.arty_id = t.arty_id
        JOIN hier h ON a.area_parent_id = h.area_id
        WHERE h.nivel < 10

    ),
    -- Nodos terminales: no aparecen como padre de ningún otro nodo
    hojas AS (
        SELECT a.area_id
        FROM stg.suia_areas_bi a
        WHERE a.area_id NOT IN (
            SELECT DISTINCT area_parent_id
            FROM   stg.suia_areas_bi
            WHERE  area_parent_id IS NOT NULL
        )
    ),
    hier_final AS (
        SELECT
            h.area_id,
            h.nivel,
            h.l1_id,
            LEFT(h.l1_nombre, 255)                                  AS l1_nombre,
            LEFT(h.l1_tipo,   10)                                   AS l1_tipo,
            h.l2_id,
            CASE WHEN h.l2_nombre IS NOT NULL
                 THEN LEFT(h.l2_nombre, 255) ELSE NULL END           AS l2_nombre,
            CASE WHEN h.l2_tipo IS NOT NULL
                 THEN LEFT(h.l2_tipo, 10)    ELSE NULL END           AS l2_tipo,
            LEFT(h.ruta_ids,  200)                                  AS ruta_ids,
            h.ruta_nombres,
            (lf.area_id IS NOT NULL)                                AS es_hoja
        FROM hier h
        LEFT JOIN hojas lf ON h.area_id = lf.area_id
    )
    UPDATE dw.dim_area d
    SET
        nivel_jerarquico = hf.nivel,
        l1_id            = hf.l1_id,
        l1_nombre        = hf.l1_nombre,
        l1_siglas_tipo   = hf.l1_tipo,
        l2_id            = hf.l2_id,
        l2_nombre        = hf.l2_nombre,
        l2_siglas_tipo   = hf.l2_tipo,
        ruta_ids         = hf.ruta_ids,
        ruta_nombres     = hf.ruta_nombres,
        es_hoja          = hf.es_hoja
    FROM hier_final hf
    WHERE d.id_area = hf.area_id
      AND d.id_area > 0;

    GET DIAGNOSTICS v_dim_actualizadas = ROW_COUNT;


    -- =========================================================================
    -- PASO 2: Poblar bridge_area_jerarquia
    --
    -- Elimina y reconstruye la bridge table completa.
    -- Se insertan 3 grupos: distancia 0 (self), 1 (padre), 2 (abuelo).
    -- =========================================================================
    TRUNCATE TABLE dw.bridge_area_jerarquia;

    -- Distancia 0: cada nodo es ancestro de sí mismo
    INSERT INTO dw.bridge_area_jerarquia (
        sk_area_descendiente, sk_area_ancestro,
        id_area_descendiente, id_area_ancestro,
        distancia, es_hoja, es_raiz
    )
    SELECT
        d.sk_area,   d.sk_area,
        d.id_area,   d.id_area,
        0,
        COALESCE(d.es_hoja, FALSE),
        (d.id_area_padre IS NULL)
    FROM dw.dim_area d
    WHERE d.id_area > 0;

    GET DIAGNOSTICS v_bridge_self = ROW_COUNT;

    -- Distancia 1: relación directa padre → hijo
    INSERT INTO dw.bridge_area_jerarquia (
        sk_area_descendiente, sk_area_ancestro,
        id_area_descendiente, id_area_ancestro,
        distancia, es_hoja, es_raiz
    )
    SELECT
        hijo.sk_area,   padre.sk_area,
        hijo.id_area,   padre.id_area,
        1,
        COALESCE(hijo.es_hoja, FALSE),
        (padre.id_area_padre IS NULL)
    FROM dw.dim_area hijo
    JOIN dw.dim_area padre ON hijo.id_area_padre = padre.id_area
    WHERE hijo.id_area  > 0
      AND padre.id_area > 0;

    GET DIAGNOSTICS v_bridge_padre = ROW_COUNT;

    -- Distancia 2: relación abuelo → nieto
    INSERT INTO dw.bridge_area_jerarquia (
        sk_area_descendiente, sk_area_ancestro,
        id_area_descendiente, id_area_ancestro,
        distancia, es_hoja, es_raiz
    )
    SELECT
        nieto.sk_area,   abuelo.sk_area,
        nieto.id_area,   abuelo.id_area,
        2,
        COALESCE(nieto.es_hoja, FALSE),
        (abuelo.id_area_padre IS NULL)
    FROM dw.dim_area nieto
    JOIN dw.dim_area padre  ON nieto.id_area_padre  = padre.id_area
    JOIN dw.dim_area abuelo ON padre.id_area_padre  = abuelo.id_area
    WHERE nieto.id_area  > 0
      AND padre.id_area  > 0
      AND abuelo.id_area > 0;

    GET DIAGNOSTICS v_bridge_abuelo = ROW_COUNT;


    -- =========================================================================
    -- RESULTADO
    -- =========================================================================
    v_msg := format(
        'OK | dim_area actualizadas: %s | bridge dist=0: %s | dist=1: %s | dist=2: %s | total bridge: %s',
        v_dim_actualizadas,
        v_bridge_self,
        v_bridge_padre,
        v_bridge_abuelo,
        (v_bridge_self + v_bridge_padre + v_bridge_abuelo)
    );

    RAISE NOTICE '%', v_msg;
    RETURN v_msg;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '[sp_carga_jerarquia_area] Error: %', SQLERRM;
END;
$$;


-- ============================================================================
-- VERIFICACIÓN INMEDIATA — ejecutar tras aplicar el SP
-- ============================================================================
SELECT dw.sp_carga_jerarquia_area();

-- Distribución por nivel
SELECT nivel_jerarquico, siglas_tipo_area, COUNT(*) AS total
FROM dw.dim_area
WHERE id_area > 0
GROUP BY nivel_jerarquico, siglas_tipo_area
ORDER BY nivel_jerarquico, total DESC;

-- Estado bridge
SELECT distancia, COUNT(*) AS pares, SUM(CASE WHEN es_hoja THEN 1 ELSE 0 END) AS hojas
FROM dw.bridge_area_jerarquia
GROUP BY distancia ORDER BY distancia;

-- Ejemplo de ruta completa
SELECT nivel_jerarquico, ruta_ids, ruta_nombres, es_hoja
FROM dw.dim_area
WHERE nivel_jerarquico = 3
LIMIT 5;
