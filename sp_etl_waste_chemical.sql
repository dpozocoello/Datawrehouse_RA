CREATE OR REPLACE FUNCTION dw.sp_etl_waste_chemical()
RETURNS VOID AS $$
DECLARE 
    v_start_time TIMESTAMP := NOW();
    v_log_id INTEGER;
    v_pre_count INTEGER;
    v_post_count INTEGER;
BEGIN
    -- 1. Initialize Log
    INSERT INTO dw.etl_process_log (process_name, execution_mode, status, start_time)
    VALUES ('Waste Chemical ETL', 'PROCEDURE_V2.1', 'RUNNING', v_start_time);
    
    v_log_id := lastval();

    -- 2. Dimension Defaults
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

    INSERT INTO dw.dim_punto_generacion (punto_generacion_key, source_id, point_name)
    SELECT 0, 0, 'SIN DEFINIR'
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_punto_generacion WHERE punto_generacion_key = 0)
    ON CONFLICT DO NOTHING;

    -- 3. Generator Dimension Sync
    INSERT INTO dw.dim_waste_generator (
        waste_generator_id, generator_name, generator_type, ruc_generator, province, canton, 
        codigo, date_add, date_update, effective_from, is_current
    )
    SELECT 
        s.waste_generator_id::bigint, 
        LEFT(s.generator_name::text, 500),
        LEFT(s.generator_type::text, 200),
        s.ruc::text, 
        LEFT(s.province::text, 100), 
        LEFT(s.canton::text, 100), 
        s.registry_number::text,
        s.date_add::timestamp, s.date_update::timestamp, CURRENT_TIMESTAMP, TRUE
    FROM (
        SELECT DISTINCT ON (stg.waste_generator_id) stg.* 
        FROM stg.stg_waste_generator stg 
        WHERE stg.waste_generator_id IS NOT NULL
        ORDER BY stg.waste_generator_id, stg.date_update DESC NULLS LAST
    ) s
    ON CONFLICT (waste_generator_id) DO UPDATE SET 
        generator_name = EXCLUDED.generator_name,
        generator_type = EXCLUDED.generator_type,
        ruc_generator = EXCLUDED.ruc_generator,
        province = EXCLUDED.province,
        canton = EXCLUDED.canton,
        codigo = EXCLUDED.codigo,
        date_update = EXCLUDED.date_update;

    -- 3.1 Point Dimension Sync (FIXED WITH EXPLICIT CASTS)
    INSERT INTO dw.dim_punto_generacion (
        source_id, source_system, waste_generator_id, point_name, 
        x_coordinate, y_coordinate, province, canton, parroquia, date_update
    )
    SELECT 
        s.source_id::bigint, 
        s.source_system::varchar, 
        s.waste_generator_id::bigint, 
        COALESCE(s.point_name::text, 'Punto ID ' || s.source_id),
        NULLIF(s.x_coordinate::text, '')::numeric, 
        NULLIF(s.y_coordinate::text, '')::numeric, 
        s.province::text, 
        s.canton::text, 
        s.parroquia::text, 
        NOW()
    FROM stg.stg_generation_points s
    ON CONFLICT (source_id, source_system) DO UPDATE SET
        point_name = EXCLUDED.point_name,
        x_coordinate = EXCLUDED.x_coordinate,
        y_coordinate = EXCLUDED.y_coordinate,
        province = EXCLUDED.province,
        canton = EXCLUDED.canton,
        parroquia = EXCLUDED.parroquia,
        date_update = NOW();

    -- 4. Waste Type & Others Sync
    INSERT INTO dw.dim_waste_type (cawa_id, waste_key_code, waste_name, waste_status)
    SELECT cawa_id::bigint, cawa_key::text, cawa_name::text, cawa_status::boolean
    FROM stg.stg_waste_type
    ON CONFLICT (cawa_id) DO UPDATE SET
        waste_key_code = EXCLUDED.waste_key_code,
        waste_name = EXCLUDED.waste_name,
        waste_status = EXCLUDED.waste_status;

    INSERT INTO dw.dim_dangerous_waste (dw_id, dangerous_code, description, regulation_reference)
    SELECT dw_id::bigint, dangerous_code::text, description::text, regulation_reference::text
    FROM stg.stg_dangerous_waste
    ON CONFLICT (dw_id) DO UPDATE SET
        dangerous_code = EXCLUDED.dangerous_code,
        description = EXCLUDED.description,
        regulation_reference = EXCLUDED.regulation_reference;

    INSERT INTO dw.dim_dangerous_classification (class_id, danger_level, description)
    SELECT class_id::bigint, danger_level::text, description::text
    FROM stg.stg_dangerous_classification
    ON CONFLICT (class_id) DO UPDATE SET
        danger_level = EXCLUDED.danger_level,
        description = EXCLUDED.description;

    -- 5. Optimized Caches
    DROP TABLE IF EXISTS stg.tmp_dim_proyecto_optimized;
    CREATE TABLE stg.tmp_dim_proyecto_optimized AS SELECT sk_proyecto, codigo_proyecto FROM dw.dim_proyecto;
    CREATE INDEX idx_tmp_proj_opt ON stg.tmp_dim_proyecto_optimized(codigo_proyecto);

    -- 6. Fact Transformation (Increased Granularity: Punto de Generación)
    DROP TABLE IF EXISTS stg.tmp_final_waste_batch;
    CREATE TABLE stg.tmp_final_waste_batch AS
    SELECT DISTINCT ON (COALESCE(dp.sk_proyecto, 0), dwg.waste_generator_key, COALESCE(dpg.punto_generacion_key, 0), dt.sk_tiempo, COALESCE(dwt.waste_type_key, 0))
        COALESCE(dp.sk_proyecto, 0) as sk_proyecto,
        dwg.waste_generator_key,
        COALESCE(dpg.punto_generacion_key, 0) as punto_generacion_key,
        dt.sk_tiempo,
        COALESCE(dwt.waste_type_key, 0) as waste_type_key,
        COALESCE(ddw.dangerous_waste_key, 0) as dangerous_waste_key,
        COALESCE(ddc.danger_class_key, 0) as danger_class_key,
        COALESCE(dg.sk_geografia, 0) as geo_location_key,
        LEAST(COALESCE(stg.quantity_generated::numeric, 0), 999999999999.999) as quantity_generated,
        LEAST(COALESCE(stg.quantity_delivered::numeric, 0), 999999999999.999) as quantity_delivered,
        LEAST(COALESCE(stg.quantity_stored::numeric, 0), 999999999999.999) as quantity_stored,
        LEFT(stg.unit::text, 50) as unit, 
        stg.record_year::int as record_year,
        stg.source_system::text as source_system
    FROM stg.stg_fact_waste_generation stg
    LEFT JOIN stg.tmp_dim_proyecto_optimized dp ON dp.codigo_proyecto = stg.project_code
    JOIN dw.dim_waste_generator dwg ON dwg.waste_generator_id = stg.waste_generator_id::bigint
    JOIN dw.dim_tiempo dt ON dt.fecha = DATE(stg.date_generated::timestamp)
    LEFT JOIN dw.dim_waste_type dwt ON dwt.cawa_id = stg.waste_type_id::bigint
    LEFT JOIN dw.dim_dangerous_waste ddw ON ddw.dw_id = stg.dangerous_waste_id::bigint
    LEFT JOIN dw.dim_dangerous_classification ddc ON ddc.class_id = stg.danger_class_id::bigint
    LEFT JOIN dw.dim_punto_generacion dpg ON (dpg.source_id = stg.point_id::bigint AND dpg.source_system = stg.source_system)
    LEFT JOIN dw.dim_geografia dg ON (
        UPPER(dg.provincia) = UPPER(COALESCE(dpg.province, dwg.province)) AND 
        UPPER(dg.canton) = UPPER(COALESCE(dpg.canton, dwg.canton))
    )
    ORDER BY 1,2,3,4,5, stg.record_year DESC;

    -- 7. Fact Transformation (UPSERT)
    INSERT INTO dw.fact_waste_generation (
        sk_proyecto, waste_generator_key, punto_generacion_key, sk_tiempo, waste_type_key, 
        dangerous_waste_key, danger_class_key, geo_location_key, quantity_generated, 
        quantity_delivered, quantity_stored, unit, record_year, source_system
    )
    SELECT 
        sk_proyecto, waste_generator_key, punto_generacion_key, sk_tiempo, waste_type_key, 
        dangerous_waste_key, danger_class_key, geo_location_key, quantity_generated, 
        quantity_delivered, quantity_stored, unit, record_year, source_system
    FROM stg.tmp_final_waste_batch
    ON CONFLICT (sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key, punto_generacion_key) 
    DO UPDATE SET
        quantity_generated = EXCLUDED.quantity_generated,
        quantity_delivered = EXCLUDED.quantity_delivered,
        quantity_stored = EXCLUDED.quantity_stored,
        unit = EXCLUDED.unit,
        record_year = EXCLUDED.record_year,
        source_system = EXCLUDED.source_system,
        geo_location_key = EXCLUDED.geo_location_key;

    -- 8. Finalization
    UPDATE dw.etl_process_log SET end_time = NOW(), status = 'SUCCESS' WHERE id = v_log_id;
    DROP TABLE IF EXISTS stg.tmp_final_waste_batch;

EXCEPTION WHEN OTHERS THEN
    IF v_log_id IS NOT NULL THEN
        UPDATE dw.etl_process_log SET end_time = NOW(), status = 'ERROR', error_message = SQLERRM WHERE id = v_log_id;
    END IF;
    RAISE;
END;
$$ LANGUAGE plpgsql;
$$ LANGUAGE plpgsql;
