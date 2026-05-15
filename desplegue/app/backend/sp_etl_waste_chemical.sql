CREATE OR REPLACE FUNCTION dw.sp_etl_waste_chemical()
RETURNS VOID AS $PROC$
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
$PROC$ LANGUAGE plpgsql;
