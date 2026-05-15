
CREATE OR REPLACE FUNCTION dw.sp_etl_chemical_test()
RETURNS VOID AS $PROC$
BEGIN
    -- 1. Create Project Mapping Cache
    DROP TABLE IF EXISTS tmp_chemical_project_map;
    CREATE TEMP TABLE tmp_chemical_project_map AS
    WITH base AS (
        SELECT 
            r.chsr_id,
            COALESCE(m.prco_cua, 'N/A') as direct_cua,
            r.chsr_identification_rep_legal as ruc,
            r.chsr_code
        FROM stg.stg_chemical_sustances_records r
        LEFT JOIN stg.stg_project_mapping m ON m.prco_id = r.prco_id
    )
    SELECT 
        b.chsr_id,
        COALESCE(
            (SELECT dp1.sk_proyecto FROM dw.dim_proyecto dp1 
             WHERE RIGHT(dp1.codigo_proyecto, 11) = RIGHT(b.direct_cua, 11) 
             ORDER BY dp1.sk_proyecto DESC LIMIT 1),
            (SELECT fr.sk_proyecto FROM dw.fact_regularizacion fr
             JOIN dw.dim_proponente dp2 ON fr.sk_proponente = dp2.sk_proponente
             WHERE dp2.ced_ruc_proponente = b.ruc 
             ORDER BY fr.sk_proyecto DESC LIMIT 1),
            (SELECT dp3.sk_proyecto FROM dw.dim_proyecto dp3 
             WHERE dp3.codigo_proyecto = COALESCE(b.chsr_code, 'REG-CHSR-' || b.chsr_id) 
             LIMIT 1),
            0
        ) as resolved_sk_proyecto
    FROM base b;

    -- 2. Fact Import
    INSERT INTO dw.fact_chemical_import (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
        quantity_authorized, net_weight, gross_weight, import_status, 
        processing_code, document_number, source_system
    )
    SELECT 
        COALESCE(tpm.resolved_sk_proyecto, 0),
        COALESCE((SELECT ds.chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = ir.dach_id ORDER BY chemical_key DESC LIMIT 1), 0),
        COALESCE((SELECT di.importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = ir.chsr_id ORDER BY importer_key DESC LIMIT 1), 0),
        0, -- Time 0
        COALESCE((SELECT sk_geografia FROM dw.dim_geografia dg WHERE dg.sk_geografia = dr.gelo_id LIMIT 1), 0),
        SUM(dr.deir_available_space), SUM(dr.deir_net_weight), SUM(dr.deir_gross_weight),
        MAX(CASE WHEN ir.inre_authorization THEN 'AUTORIZADO' ELSE 'PENDIENTE' END),
        ir.inre_processing_code, 
        COALESCE(ir.inre_document_autorizes, 'REQ-' || ir.inre_id), 
        'COA_IMPORT'
    FROM stg.stg_import_request ir
    JOIN stg.stg_detail_import_request dr ON ir.inre_id = dr.inre_id
    LEFT JOIN tmp_chemical_project_map tpm ON ir.chsr_id = tpm.chsr_id
    GROUP BY 1, 2, 3, 4, 5, 10, 11, 12
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number) 
    DO UPDATE SET
        quantity_authorized = EXCLUDED.quantity_authorized,
        net_weight = EXCLUDED.net_weight,
        gross_weight = EXCLUDED.gross_weight;

    -- 3. Fact Movement
    INSERT INTO dw.fact_chemical_movement (
        sk_proyecto, chemical_key, importer_key, sk_tiempo, 
        quantity_entry, quantity_exit, invoice_number, operator_name
    )
    SELECT 
        COALESCE(tpm.resolved_sk_proyecto, 0),
        COALESCE((SELECT ds.chemical_key FROM dw.dim_chemical_substance ds WHERE ds.chemical_id = m.achs_id ORDER BY chemical_key DESC LIMIT 1), 0),
        COALESCE((SELECT di.importer_key FROM dw.dim_chemical_importer di WHERE di.importer_id = d.chsr_id ORDER BY importer_key DESC LIMIT 1), 0),
        0,
        SUM(m.chsm_entry), SUM(m.chsm_exit), 
        COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id), 
        MAX(m.chsm_operator)
    FROM stg.stg_chemical_substances_movements m
    JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
    LEFT JOIN tmp_chemical_project_map tpm ON d.chsr_id = tpm.chsr_id
    GROUP BY 1, 2, 3, 4, 7
    ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number)
    DO UPDATE SET
        quantity_entry = EXCLUDED.quantity_entry,
        quantity_exit = EXCLUDED.quantity_exit;

END;
$PROC$ LANGUAGE plpgsql;
