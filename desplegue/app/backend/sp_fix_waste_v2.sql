-- ==============================================================================
-- FIX: sp_carga_waste_chemical_v2.sql
-- ==============================================================================

CREATE OR REPLACE FUNCTION dw.sp_carga_waste_chemical_v2() RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE INFO '[RGD_TRANSFORM] Iniciando transformación v2.0...';

    -- 1. Actualizar Dimensión: dw.dim_tipo_desecho (Con Jerarquía)
    -- Se corrigió la columna cawp_id que presentaba error de existencia
    INSERT INTO dw.dim_tipo_desecho (
        codigo_desecho, nombre_desecho, categoria_desecho, grupo_jerarquico, unidad_medida
    )
    SELECT 
        st.cawa_key, 
        st.cawa_name,
        CASE 
            WHEN sp.cawp_name ILIKE '%PELIGROSO%' THEN 'PELIGROSO'
            WHEN sp.cawp_name ILIKE '%ESPECIAL%' THEN 'ESPECIAL'
            ELSE 'OTRO'
        END,
        sp.cawp_name,
        'KG'
    FROM stg.stg_waste_type st
    JOIN stg.stg_waste_catalogs_parent sp ON st.cawp_id = sp.cawp_id
    ON CONFLICT (codigo_desecho) DO UPDATE SET
        nombre_desecho = EXCLUDED.nombre_desecho,
        grupo_jerarquico = EXCLUDED.grupo_jerarquico;

    -- 2. Actualizar Dimensión: dw.dim_generador_desechos
    INSERT INTO dw.dim_generador_desechos (
        ruc_generador, nombre_generador, codigo_rgd, fuente_sistema
    )
    SELECT 
        ruc, 
        COALESCE(registry_number, 'GENERADOR_S_N'), 
        registry_number,
        source
    FROM stg.stg_waste_generator
    ON CONFLICT (ruc_generador) DO NOTHING;

    -- 3. Cargar Hechos: dw.fact_generacion_desechos (Declaraciones)
    -- NOTA: Se comenta esta sección debido a que no existen declaraciones anuales en el origen actual
    /*
    TRUNCATE TABLE dw.fact_generacion_desechos;
    INSERT INTO dw.fact_generacion_desechos (
        sk_generador, sk_tipo_desecho, cantidad_generada, cantidad_entregada, anio_declaracion
    )
    SELECT 
        dg.sk_generador,
        dt.sk_tipo_desecho,
        sd.total_quantity_declared,
        sd.total_quantity_delivered,
        sd.gras_year
    FROM stg.stg_rgd_annual_declarations sd
    JOIN dw.dim_generador_desechos dg ON sd.hwge_id::text = dg.id_generador_externo
    CROSS JOIN dw.dim_tipo_desecho dt 
    WHERE sd.total_quantity_declared > 0;
    */

    RAISE INFO '[RGD_TRANSFORM] Transformación finalizada OK.';
    RETURN TRUE;
END;
$$;
