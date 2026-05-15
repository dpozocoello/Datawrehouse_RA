-- ==============================================================================
-- MODELO DIMENSIONAL: REGISTRO DE IMPORTACIÓN DE SUSTANCIAS QUÍMICAS Y PESTICIDAS
-- ==============================================================================
-- Esquemas: stg (Staging), dw (Data Warehouse)
-- ==============================================================================

-- 1. TABLAS DE STAGING (COA CHEMICAL)
-- ------------------------------------------------------------------------------

-- 1.1 Registro de Sustancias (Header/Empresa)
CREATE TABLE IF NOT EXISTS stg.stg_chemical_sustances_records (
    chsr_id BIGINT,
    prco_id BIGINT,
    chsr_identification_rep_legal VARCHAR(25),
    chsr_name_rep_legal VARCHAR(500),
    chsr_substance_registration VARCHAR(255),
    chsr_code VARCHAR(255),
    chsr_valid_since TIMESTAMP,
    chsr_valid_until TIMESTAMP,
    chsr_status BOOLEAN,
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 1.2 Declaraciones Mensuales/Anuales
CREATE TABLE IF NOT EXISTS stg.stg_chemical_substances_declaration (
    chsd_id BIGINT,
    chsr_id BIGINT,
    chsd_year INTEGER,
    chsd_month INTEGER,
    chsd_starting_amount NUMERIC(15,3),
    chsd_end_quantity NUMERIC(15,3),
    chsd_declaration_on_time BOOLEAN,
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 1.3 Movimientos (Entradas/Salidas)
CREATE TABLE IF NOT EXISTS stg.stg_chemical_substances_movements (
    chsm_id BIGINT,
    chsd_id BIGINT,
    chsm_invoice VARCHAR(100),
    chsm_operator VARCHAR(500),
    chsm_entry NUMERIC(15,3),
    chsm_exit NUMERIC(15,3),
    achs_id BIGINT,
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 1.4 Solicitudes de Importación
CREATE TABLE IF NOT EXISTS stg.stg_import_request (
    inre_id BIGINT,
    chsr_id BIGINT,
    mach_id BIGINT,
    dach_id BIGINT,
    inre_authorization BOOLEAN,
    inre_begin_authorization_date TIMESTAMP,
    inre_end_authorization_date TIMESTAMP,
    inre_processing_code VARCHAR(100),
    inre_document_autorizes VARCHAR(100),
    req_no VARCHAR(100),
    inre_type VARCHAR(10),
    inre_status BOOLEAN,
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 1.3 Detalle de Importación (Cantidades)
CREATE TABLE IF NOT EXISTS stg.stg_detail_import_request (
    deir_id BIGINT,
    inre_id BIGINT,
    deir_available_space NUMERIC(15,3),
    deir_net_weight NUMERIC(15,3),
    deir_gross_weight NUMERIC(15,3),
    gelo_id INTEGER, -- País de Origen
    achs_id BIGINT,
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 1.5 Puente de Mapeo de Proyectos (ID -> CUA)
CREATE TABLE IF NOT EXISTS stg.stg_project_mapping (
    prco_id BIGINT,
    prco_cua VARCHAR(100),
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 2. TABLAS DE STAGING (PESTICIDES)
-- ------------------------------------------------------------------------------

-- 2.1 Proyectos de Pesticidas
CREATE TABLE IF NOT EXISTS stg.stg_pesticide_project (
    chpe_id BIGINT,
    chpe_proyect_code VARCHAR(100), -- MAE-RA...
    chpe_status BOOLEAN,
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 2.2 Productos PQA registered
CREATE TABLE IF NOT EXISTS stg.stg_products_pqa (
    pqa_id BIGINT,
    pqa_name VARCHAR(500),
    pqa_registration_number VARCHAR(100),
    pqa_toxicological_category VARCHAR(200),
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 2.3 Detalle Proyecto - Producto
CREATE TABLE IF NOT EXISTS stg.stg_detail_pesticide_project (
    depp_id BIGINT,
    chpe_id BIGINT,
    pqa_id BIGINT,
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- 3. DIMENSIONES DW
-- ------------------------------------------------------------------------------

-- 3.1 Dimensión Importador / Fabricante
CREATE TABLE IF NOT EXISTS dw.dim_chemical_importer (
    importer_key SERIAL PRIMARY KEY,
    importer_id BIGINT NOT NULL UNIQUE, -- chsr_id
    importer_name VARCHAR(500),
    identification VARCHAR(50),
    registration_code VARCHAR(255),
    is_current BOOLEAN DEFAULT TRUE,
    date_add TIMESTAMP DEFAULT NOW(),
    date_update TIMESTAMP
);

-- 4. TABLAS DE HECHOS DW
-- ------------------------------------------------------------------------------

-- 4.1 Hechos Importación de Sustancias Químicas
CREATE TABLE IF NOT EXISTS dw.fact_chemical_import (
    sk_proyecto BIGINT NOT NULL,
    chemical_key BIGINT NOT NULL,
    importer_key BIGINT NOT NULL,
    sk_tiempo BIGINT NOT NULL,
    geo_location_key BIGINT, -- sk_geografia (País Origen)
    quantity_authorized NUMERIC(15,3),
    net_weight NUMERIC(15,3),
    gross_weight NUMERIC(15,3),
    import_status VARCHAR(50),
    processing_code VARCHAR(100),
    document_number VARCHAR(100),
    source_system VARCHAR(50), -- 'COA_IMPORT' or 'PESTICIDES'
    FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto),
    FOREIGN KEY (chemical_key) REFERENCES dw.dim_chemical_substance(chemical_key),
    FOREIGN KEY (importer_key) REFERENCES dw.dim_chemical_importer(importer_key),
    FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo),
    FOREIGN KEY (geo_location_key) REFERENCES dw.dim_geografia(sk_geografia)
);

-- 4.2 Hechos Movimientos de Sustancias Químicas
CREATE TABLE IF NOT EXISTS dw.fact_chemical_movement (
    sk_proyecto BIGINT NOT NULL,
    chemical_key BIGINT NOT NULL,
    importer_key BIGINT NOT NULL,
    sk_tiempo BIGINT NOT NULL,
    quantity_entry NUMERIC(15,3),
    quantity_exit NUMERIC(15,3),
    invoice_number VARCHAR(100),
    operator_name VARCHAR(500),
    FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto),
    FOREIGN KEY (chemical_key) REFERENCES dw.dim_chemical_substance(chemical_key),
    FOREIGN KEY (importer_key) REFERENCES dw.dim_chemical_importer(importer_key),
    FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo)
);

-- 4.3 Hechos Declaraciones de Sustancias Químicas
CREATE TABLE IF NOT EXISTS dw.fact_chemical_declaration (
    sk_proyecto BIGINT NOT NULL,
    importer_key BIGINT NOT NULL,
    sk_tiempo BIGINT NOT NULL, -- sk_tiempo representing the declaration period
    initial_quantity NUMERIC(15,3),
    final_quantity NUMERIC(15,3),
    is_on_time BOOLEAN,
    declaration_year INTEGER,
    declaration_month INTEGER,
    FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto),
    FOREIGN KEY (importer_key) REFERENCES dw.dim_chemical_importer(importer_key),
    FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo)
);

-- 5. ÍNDICES
CREATE INDEX IF NOT EXISTS idx_fact_imp_proj ON dw.fact_chemical_import(sk_proyecto);
CREATE INDEX IF NOT EXISTS idx_fact_imp_chem ON dw.fact_chemical_import(chemical_key);
CREATE INDEX IF NOT EXISTS idx_fact_imp_date ON dw.fact_chemical_import(sk_tiempo);
