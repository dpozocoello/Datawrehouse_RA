-- ==============================================================================
-- ETL EXTRACT: CARGA A STAGING DE DESECHOS Y SUSTANCIAS QUÍMICAS
-- ==============================================================================
-- Estas consultas extraen la data desde los esquemas transaccionales
-- para cargar las tablas STG del DWH.
-- ==============================================================================

-- 1. STG Waste Generator (coa_waste_generator_record)
SELECT 
    wg.waste_generator_id,
    wg.name as generator_name,
    wg.type as generator_type,
    wg.province,
    wg.canton,
    wg.date_add,
    wg.date_update
FROM coa_waste_generator_record.waste_generator wg
WHERE wg.status = TRUE;

-- 2. STG Waste Type (coa_waste_generator_record)
SELECT 
    wt.cawa_id,
    wt.cawa_key as waste_key_code,
    wt.cawa_name as waste_name,
    wt.cawa_status as waste_status
FROM coa_waste_generator_record.catalogs_waste wt;

-- 3. STG Dangerous Waste (waste_dangerous)
SELECT 
    dw.dw_id,
    dw.dangerous_code,
    dw.description,
    dw.regulation_reference
FROM waste_dangerous.dangerous_waste dw
WHERE dw.is_active = TRUE;

-- 4. STG Dangerous Classification (waste_dangerous)
SELECT 
    class_id,
    danger_level,
    description
FROM waste_dangerous.dw_classification;

-- 5. STG Chemical Substance (coa_chemical_sustances & chemical_pesticides)
SELECT 
    cs.chemical_id,
    cs.name as substance_name,
    cs.cas_number,
    cs.classification,
    cs.type as chemical_type
FROM coa_chemical_sustances.chemical_substance cs
UNION ALL
SELECT 
    cp.chemical_id,
    cp.name as substance_name,
    cp.cas_number,
    cp.classification,
    cp.type as chemical_type
FROM chemical_pesticides.chemical_substance cp;

-- 6. STG Chemical Storage (coa_chemical_sustances)
SELECT 
    st.storage_id,
    st.storage_type,
    st.capacity,
    st.unit,
    st.location_description
FROM coa_chemical_sustances.chemical_storage st;

-- 7. STG Hechos: Generación de Desechos
SELECT 
    pw.project_id,
    wr.waste_generator_id,
    wr.date_generated,
    wr.cawa_id as waste_type_id,
    wr.dw_id as dangerous_waste_id,
    wr.class_id as danger_class_id,
    wr.location_id,
    wr.quantity_generated,
    wr.quantity_delivered,
    wr.quantity_stored,
    wr.unit,
    EXTRACT(YEAR FROM wr.date_generated) as record_year
FROM coa_waste_generator_record.waste_record wr
JOIN coa_waste_generator_record.project_waste pw ON wr.record_id = pw.record_id;

-- 8. STG Hechos: Uso de Sustancias Químicas
SELECT 
    cu.project_id,
    cu.substance_id as chemical_id,
    cu.usage_date as date_applied,
    cu.storage_id,
    cu.location_id,
    cu.dose,
    cu.dose_unit,
    cu.application_method,
    cu.area_covered,
    EXTRACT(YEAR FROM cu.usage_date) as usage_year
FROM coa_chemical_sustances.chemical_usage cu;
