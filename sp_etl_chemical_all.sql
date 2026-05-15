CREATE OR REPLACE FUNCTION dw.sp_etl_chemical_all()
RETURNS VOID AS $PROC$
DECLARE 
    v_start_time TIMESTAMP := NOW();
    v_log_id INTEGER;
    v_pre_count_imp INTEGER;
    v_post_count_imp INTEGER;
BEGIN
    -- 1. Initialize Log
    RAISE NOTICE 'Initializing Log...';
    INSERT INTO dw.etl_process_log (process_name, execution_mode, status, start_time)
    VALUES ('Chemical ETL', 'FULL', 'RUNNING', v_start_time)
    RETURNING id INTO v_log_id;
    RAISE NOTICE 'Log ID created: %', v_log_id;

    -- 2. Dimensional Integrity (Key 0)
    RAISE NOTICE 'Setting Dimensional Integrity...';
    INSERT INTO dw.dim_chemical_substance (chemical_key, chemical_id, substance_name)
    VALUES (0, -1, 'N/A') ON CONFLICT (chemical_key) DO NOTHING;

    INSERT INTO dw.dim_chemical_importer (importer_key, importer_id, importer_name)
    VALUES (0, -1, 'N/A') ON CONFLICT (importer_key) DO NOTHING;

    -- 3. Sync Virtual Projects from Chemical Registrations (Tier 3)
    RAISE NOTICE 'Syncing Virtual Projects...';
    INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto, sistema)
    SELECT DISTINCT 
        COALESCE(chsr_code, 'REG-CHSR-' || chsr_id), 
        'REGISTRO SUSTANCIA: ' || COALESCE(chsr_code, 'ID ' || chsr_id), 
        'COA_IMPORT_REG'
    FROM stg.stg_chemical_sustances_records
    ON CONFLICT (codigo_proyecto) DO NOTHING;

    -- 4. Optimized Project Mapping Cache
    RAISE NOTICE 'Building Optimized Mapping Cache...';
    
    -- 4.1 Tier 1: Direct Mapping Lookup
    CREATE TEMP TABLE tmp_t1_lookup AS
    WITH target_suffixes AS (
        SELECT DISTINCT RIGHT(m.prco_cua, 11) as suffix
        FROM stg.stg_chemical_sustances_records r
        JOIN stg.stg_project_mapping m ON r.prco_id = m.prco_id
        WHERE m.prco_cua IS NOT NULL
    )
    SELECT DISTINCT ON (RIGHT(codigo_proyecto, 11))
        RIGHT(codigo_proyecto, 11) as suffix,
        sk_proyecto
    FROM dw.dim_proyecto
    WHERE RIGHT(codigo_proyecto, 11) IN (SELECT suffix FROM target_suffixes)
    ORDER BY RIGHT(codigo_proyecto, 11), sk_proyecto DESC;

    -- 4.2 Tier 2: RUC Mapping Lookup
    CREATE TEMP TABLE tmp_t2_lookup AS
    SELECT DISTINCT ON (dp2.ced_ruc_proponente)
        dp2.ced_ruc_proponente as ruc,
        fr.sk_proyecto
    FROM dw.fact_regularizacion fr
    JOIN dw.dim_proponente dp2 ON fr.sk_proponente = dp2.sk_proponente
    WHERE dp2.ced_ruc_proponente IN (SELECT DISTINCT chsr_identification_rep_legal FROM stg.stg_chemical_sustances_records)
    ORDER BY dp2.ced_ruc_proponente, fr.sk_proyecto DESC;

    -- 4.3 Final Mapping Assemble
    CREATE TEMP TABLE tmp_chemical_project_map AS
    SELECT 
        r.chsr_id,
        COALESCE(
            t1.sk_proyecto, -- Tier 1
            t2.sk_proyecto, -- Tier 2
            dp_v.sk_proyecto, -- Tier 3: Virtual
            0 -- N/A
        ) as resolved_sk_proyecto
    FROM stg.stg_chemical_sustances_records r
    LEFT JOIN stg.stg_project_mapping m ON r.prco_id = m.prco_id
    LEFT JOIN tmp_t1_lookup t1 ON RIGHT(m.prco_cua, 11) = t1.suffix
    LEFT JOIN tmp_t2_lookup t2 ON r.chsr_identification_rep_legal = t2.ruc
    LEFT JOIN dw.dim_proyecto dp_v ON dp_v.codigo_proyecto = COALESCE(r.chsr_code, 'REG-CHSR-' || r.chsr_id);

    CREATE INDEX idx_tmp_chsr ON tmp_chemical_project_map(chsr_id);
    DROP TABLE tmp_t1_lookup;
    DROP TABLE tmp_t2_lookup;

    -- 5. Sync Dimensions (Importadores)
    INSERT INTO dw.dim_chemical_importer (importer_id, importer_name, identification, registration_code)
    SELECT DISTINCT 
        chsr_id, chsr_name_rep_legal, chsr_identification_rep_legal, chsr_substance_registration
    FROM stg.stg_chemical_sustances_records
    ON CONFLICT (importer_id) DO UPDATE SET
        importer_name = EXCLUDED.importer_name,
        identification = EXCLUDED.identification,
        registration_code = EXCLUDED.registration_code,
        date_update = NOW();

    -- 6. LOAD FACT_CHEMICAL_IMPORT
    WITH import_data AS (
        SELECT 
            COALESCE(tpm.resolved_sk_proyecto, 0) as sk_proyecto,
            COALESCE((SELECT chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = ir.dach_id ORDER BY chemical_key DESC LIMIT 1), 0) as chemical_key,
            COALESCE((SELECT importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = ir.chsr_id ORDER BY importer_key DESC LIMIT 1), 0) as importer_key,
            COALESCE((SELECT sk_tiempo FROM dw.dim_tiempo dt WHERE dt.fecha = CAST(ir.inre_begin_authorization_date AS DATE) LIMIT 1), 0) as sk_tiempo,
            COALESCE((SELECT sk_geografia FROM dw.dim_geografia dg WHERE dg.sk_geografia = dr.gelo_id LIMIT 1), 0) as geo_location_key,
            COALESCE(ir.inre_document_autorizes, 'REQ-' || ir.inre_id) as document_number,
            ir.inre_processing_code,
            ir.inre_authorization,
            dr.deir_available_space, dr.deir_net_weight, dr.deir_gross_weight
        FROM stg.stg_import_request ir
        JOIN stg.stg_detail_import_request dr ON ir.inre_id = dr.inre_id
        LEFT JOIN tmp_chemical_project_map tpm ON ir.chsr_id = tpm.chsr_id
    )
    INSERT INTO dw.fact_chemical_import (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
        quantity_authorized, net_weight, gross_weight, import_status, 
        processing_code, document_number, source_system
    )
    SELECT 
        sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
        SUM(deir_available_space), SUM(deir_net_weight), SUM(deir_gross_weight),
        MAX(CASE WHEN inre_authorization THEN 'AUTORIZADO' ELSE 'PENDIENTE' END),
        MAX(inre_processing_code), document_number, 'COA_IMPORT'
    FROM import_data
    GROUP BY sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key, document_number
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number) 
    DO UPDATE SET
        quantity_authorized = EXCLUDED.quantity_authorized,
        net_weight = EXCLUDED.net_weight,
        gross_weight = EXCLUDED.gross_weight;

    -- 7. LOAD FACT_CHEMICAL_MOVEMENT
    DROP TABLE IF EXISTS tmp_movement_pre;
    CREATE TEMP TABLE tmp_movement_pre AS
    WITH movement_data AS (
        SELECT 
            COALESCE(tpm.resolved_sk_proyecto, 0) as sk_proyecto,
            COALESCE((SELECT ds.chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = m.geca_id ORDER BY chemical_key DESC LIMIT 1), 0) as chemical_key,
            COALESCE((SELECT di.importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = d.chsr_id ORDER BY importer_key DESC LIMIT 1), 0) as importer_key,
            0 as sk_tiempo,
            COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id) as invoice_number,
            m.chsm_entry, m.chsm_exit, m.chsm_operator
        FROM stg.stg_chemical_substances_movements m
        JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
        LEFT JOIN tmp_chemical_project_map tpm ON d.chsr_id = tpm.chsr_id
    )
    SELECT 
        sk_proyecto, chemical_key, importer_key, sk_tiempo, 
        SUM(chsm_entry) as q_entry, SUM(chsm_exit) as q_exit, invoice_number, MAX(chsm_operator) as operator
    FROM movement_data
    GROUP BY sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number;

    -- Diagnostic: Check for duplicates in the aggregated set
    IF (SELECT count(*) FROM (SELECT 1 FROM tmp_movement_pre GROUP BY sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number HAVING count(*) > 1) s) > 0 THEN
        RAISE EXCEPTION 'Internal Collision: Aggregated Movements are NOT unique for the Target Key!';
    END IF;

    INSERT INTO dw.fact_chemical_movement (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, 
        quantity_entry, quantity_exit, invoice_number, operator_name
    )
    SELECT * FROM tmp_movement_pre
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number)
    DO UPDATE SET
        quantity_entry = EXCLUDED.quantity_entry,
        quantity_exit = EXCLUDED.quantity_exit,
        operator_name = EXCLUDED.operator_name;

    -- 8. LOAD FACT_CHEMICAL_DECLARATION
    RAISE NOTICE 'Loading Detailed Declarations...';
    INSERT INTO dw.fact_chemical_declaration (
        sk_proyecto, importer_key, sk_tiempo, 
        initial_quantity, final_quantity, is_on_time, 
        declaration_year, declaration_month
    )
    SELECT 
        COALESCE(tpm.resolved_sk_proyecto, 0) as sk_proyecto,
        COALESCE(di.importer_key, 0) as importer_key,
        COALESCE(dt.sk_tiempo, 0) as sk_tiempo,
        SUM(d.chsd_starting_amount), SUM(d.chsd_end_quantity), 
        BOOL_OR(COALESCE(d.chsd_declaration_on_time::boolean, false)),
        d.chsd_year, d.chsd_month
    FROM stg.stg_chemical_substances_declaration d
    LEFT JOIN tmp_chemical_project_map tpm ON d.chsr_id = tpm.chsr_id
    LEFT JOIN dw.dim_chemical_importer di ON di.importer_id = d.chsr_id
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = CAST(CONCAT(d.chsd_year, '-', d.chsd_month, '-01') AS DATE)
    GROUP BY 1, 2, 3, 7, 8
    ON CONFLICT (sk_proyecto, importer_key, sk_tiempo, declaration_year, declaration_month)
    DO UPDATE SET
        initial_quantity = EXCLUDED.initial_quantity,
        final_quantity = EXCLUDED.final_quantity,
        is_on_time = EXCLUDED.is_on_time;

    -- 9. LOAD FACT_CHEMICAL_APPLICATION (Pesticides)
    INSERT INTO dw.fact_chemical_application (
        sk_proyecto, chemical_key, sk_tiempo, dose, dose_unit, usage_year
    )
    SELECT 
        COALESCE(dp.sk_proyecto, 0),
        COALESCE(ds.chemical_key, 0),
        COALESCE(dt.sk_tiempo, 0),
        1, 'REGISTRO', EXTRACT(YEAR FROM NOW())
    FROM stg.stg_detail_pesticide_project dpp
    JOIN stg.stg_pesticide_project pp ON dpp.chpe_id = pp.chpe_id
    LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = pp.chpe_proyect_code
    LEFT JOIN dw.dim_chemical_substance ds ON ds.chemical_id = dpp.pqa_id
    LEFT JOIN dw.dim_tiempo dt ON dt.fecha = CURRENT_DATE;

    DROP TABLE tmp_chemical_project_map;

    -- 10. Metrics & Completion
    SELECT COUNT(*) INTO v_post_count_imp FROM dw.fact_chemical_import;
    
    UPDATE dw.etl_process_log 
    SET end_time = NOW(), status = 'SUCCESS', rows_inserted = (v_post_count_imp - v_pre_count_imp)
    WHERE id = v_log_id;

EXCEPTION WHEN OTHERS THEN
    DECLARE
        v_msg TEXT;
        v_detail TEXT;
        v_hint TEXT;
        v_context TEXT;
    BEGIN
        GET STACKED DIAGNOSTICS 
            v_msg = MESSAGE_TEXT,
            v_detail = PG_EXCEPTION_DETAIL,
            v_hint = PG_EXCEPTION_HINT,
            v_context = PG_EXCEPTION_CONTEXT;
            
        IF v_log_id IS NOT NULL THEN
            UPDATE dw.etl_process_log 
            SET end_time = NOW(), 
                status = 'ERROR', 
                error_message = v_msg || ' | ' || v_context
            WHERE id = v_log_id;
        END IF;
    END;
    RAISE;
END;
$PROC$ LANGUAGE plpgsql;
