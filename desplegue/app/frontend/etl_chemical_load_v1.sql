-- ==============================================================================
-- ETL QUIMICOS v1.1 - Carga Robust (Maneja orphans sin linked project)
-- ==============================================================================

-- 1. Asegurar registros genéricos en dimensiones
-- ------------------------------------------------------------------------------
INSERT INTO dw.dim_chemical_substance (chemical_id, substance_name, cas_number, classification, chemical_type, is_current)
VALUES (0, 'SUSTANCIA NO ESPECIFICADA', 'N/A', 'GENERAL', 'CHEMICAL', TRUE)
ON CONFLICT (chemical_id) DO NOTHING;

-- 2. Cargar Dimensión Importadores (dim_chemical_importer)
-- ------------------------------------------------------------------------------
TRUNCATE TABLE dw.dim_chemical_importer CASCADE;

INSERT INTO dw.dim_chemical_importer (
    importer_id, 
    importer_name, 
    identification, 
    registration_code, 
    is_current, 
    date_add
)
SELECT DISTINCT 
    chsr_id, 
    COALESCE(chsr_name_rep_legal, 'S/I'), 
    chsr_identification_rep_legal, 
    chsr_code, 
    COALESCE(chsr_status, TRUE), 
    chsr_valid_since
FROM stg.stg_chemical_sustances_records;

-- 3. Cargar Hechos: Importaciones (fact_chemical_import)
-- ------------------------------------------------------------------------------
TRUNCATE TABLE dw.fact_chemical_import;

INSERT INTO dw.fact_chemical_import (
    sk_proyecto, 
    chemical_key, 
    importer_key, 
    sk_tiempo, 
    quantity_authorized, 
    net_weight, 
    gross_weight, 
    import_status, 
    processing_code, 
    document_number, 
    source_system
)
SELECT 
    COALESCE(dp.sk_proyecto, 0), -- Fallback a Proyecto Genérico
    COALESCE(dcs.chemical_key, (SELECT chemical_key FROM dw.dim_chemical_substance WHERE chemical_id = 0)),
    dim_imp.importer_key,
    COALESCE(dt.sk_tiempo, 0),
    dir.deir_net_weight,
    dir.deir_net_weight,
    dir.deir_gross_weight,
    CASE WHEN ir.inre_status THEN 'ACTIVO' ELSE 'INACTIVO' END,
    ir.inre_processing_code,
    ir.inre_document_autorizes,
    ir.inre_type
FROM stg.stg_import_request ir
JOIN stg.stg_detail_import_request dir ON ir.inre_id = dir.inre_id
JOIN stg.stg_chemical_sustances_records scr ON ir.chsr_id = scr.chsr_id
LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto LIKE '%' || CAST(scr.prco_id AS BIGINT)::text
LEFT JOIN dw.dim_chemical_substance dcs ON dcs.chemical_id = dir.achs_id
JOIN dw.dim_chemical_importer dim_imp ON dim_imp.importer_id = ir.chsr_id
LEFT JOIN dw.dim_tiempo dt ON dt.fecha = DATE(ir.inre_begin_authorization_date);

-- 4. Cargar Hechos: Movimientos (fact_chemical_movement)
-- ------------------------------------------------------------------------------
TRUNCATE TABLE dw.fact_chemical_movement;

INSERT INTO dw.fact_chemical_movement (
    sk_proyecto, 
    chemical_key, 
    importer_key, 
    sk_tiempo, 
    quantity_entry, 
    quantity_exit, 
    invoice_number, 
    operator_name
)
SELECT 
    COALESCE(dp.sk_proyecto, 0),
    COALESCE(dcs.chemical_key, (SELECT chemical_key FROM dw.dim_chemical_substance WHERE chemical_id = 0)),
    dim_imp.importer_key,
    COALESCE(dt.sk_tiempo, 0),
    mv.chsm_entry,
    mv.chsm_exit,
    mv.chsm_invoice,
    mv.chsm_creator_user
FROM stg.stg_chemical_substances_movements mv
JOIN stg.stg_chemical_sustances_records scr ON mv.chsr_id = scr.chsr_id
LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto LIKE '%' || CAST(scr.prco_id AS BIGINT)::text
LEFT JOIN dw.dim_chemical_substance dcs ON dcs.chemical_id = mv.geca_id
JOIN dw.dim_chemical_importer dim_imp ON dim_imp.importer_id = mv.chsr_id
LEFT JOIN dw.dim_tiempo dt ON dt.fecha = DATE(mv.chsm_creation_date);

-- 5. Cargar Hechos: Declaraciones (fact_chemical_declaration)
-- ------------------------------------------------------------------------------
TRUNCATE TABLE dw.fact_chemical_declaration;

INSERT INTO dw.fact_chemical_declaration (
    sk_proyecto, 
    importer_key, 
    sk_tiempo, 
    initial_quantity, 
    final_quantity, 
    is_on_time, 
    declaration_year, 
    declaration_month
)
SELECT 
    COALESCE(dp.sk_proyecto, 0),
    dim_imp.importer_key,
    COALESCE(dt.sk_tiempo, 0),
    dec.chsd_starting_amount,
    dec.chsd_end_quantity,
    CASE WHEN dec.chsd_declaration_on_time = 'S' THEN TRUE ELSE FALSE END,
    dec.chsd_year,
    dec.chsd_month
FROM stg.stg_chemical_substances_declaration dec
JOIN stg.stg_chemical_sustances_records scr ON dec.chsr_id = scr.chsr_id
LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto LIKE '%' || CAST(scr.prco_id AS BIGINT)::text
JOIN dw.dim_chemical_importer dim_imp ON dim_imp.importer_id = dec.chsr_id
LEFT JOIN dw.dim_tiempo dt ON dt.fecha = DATE(dec.chsd_creation_date);

-- 6. Verificación Final
-- ------------------------------------------------------------------------------
SELECT 'dw.dim_chemical_importer' as tabla, COUNT(*) as registros FROM dw.dim_chemical_importer
UNION ALL
SELECT 'dw.fact_chemical_import', COUNT(*) FROM dw.fact_chemical_import
UNION ALL
SELECT 'dw.fact_chemical_movement', COUNT(*) FROM dw.fact_chemical_movement
UNION ALL
SELECT 'dw.fact_chemical_declaration', COUNT(*) FROM dw.fact_chemical_declaration;
