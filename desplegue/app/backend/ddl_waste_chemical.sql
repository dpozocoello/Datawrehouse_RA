-- ==============================================================================
-- MODELO DIMENSIONAL: INTEGRACIÓN DE DESECHOS PELIGROSOS Y SUSTANCIAS QUÍMICAS
-- ==============================================================================
-- Este script crea las dimensiones y hechos en el Data Warehouse (esquema 'dw')
-- para incorporar los datos de:
--   - coa_waste_generator_record
--   - waste_dangerous
--   - chemical_pesticides
--   - coa_chemical_sustances
-- ==============================================================================

-- 1. DIMENSIONES

-- 1.1 Dimensión Generador de Desechos
CREATE TABLE IF NOT EXISTS dw.dim_waste_generator (
    waste_generator_key BIGSERIAL PRIMARY KEY,
    waste_generator_id BIGINT NOT NULL,
    generator_name VARCHAR(500),
    generator_type VARCHAR(200),
    province VARCHAR(100),
    canton VARCHAR(100),
    codigo VARCHAR(100),
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE,
    date_add TIMESTAMP,
    date_update TIMESTAMP
);

-- 1.2 Dimensión Tipo de Desecho
CREATE TABLE IF NOT EXISTS dw.dim_waste_type (
    waste_type_key BIGSERIAL PRIMARY KEY,
    cawa_id BIGINT NOT NULL,
    waste_key_code VARCHAR(100),
    waste_name VARCHAR(1000),
    waste_status BOOLEAN
);

-- 1.3 Dimensión Residuos Peligrosos (waste_dangerous)
CREATE TABLE IF NOT EXISTS dw.dim_dangerous_waste (
    dangerous_waste_key BIGSERIAL PRIMARY KEY,
    dw_id BIGINT NOT NULL,
    dangerous_code VARCHAR(100),
    description VARCHAR(1000),
    regulation_reference VARCHAR(500),
    is_current BOOLEAN DEFAULT TRUE
);

-- 1.4 Dimensión Clasificación de Peligrosidad
CREATE TABLE IF NOT EXISTS dw.dim_dangerous_classification (
    danger_class_key BIGSERIAL PRIMARY KEY,
    class_id BIGINT NOT NULL,
    danger_level VARCHAR(50),
    description VARCHAR(500)
);

-- 1.5 Dimensión Sustancias Químicas (combinada de chemical_pesticides y coa_chemical_sustances)
CREATE TABLE IF NOT EXISTS dw.dim_chemical_substance (
    chemical_key BIGSERIAL PRIMARY KEY,
    chemical_id BIGINT NOT NULL,
    substance_name VARCHAR(500),
    cas_number VARCHAR(100),
    classification VARCHAR(200),
    chemical_type VARCHAR(100),
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

-- 1.6 Dimensión Almacenamiento Químico (chemical_storage)
CREATE TABLE IF NOT EXISTS dw.dim_chemical_storage (
    storage_key BIGSERIAL PRIMARY KEY,
    storage_id BIGINT NOT NULL,
    storage_type VARCHAR(200),
    capacity NUMERIC(15,3),
    unit VARCHAR(50),
    location_description VARCHAR(1000)
);

-- 2. TABLAS DE HECHOS

-- 2.1 Hechos Generación de Desechos
CREATE TABLE IF NOT EXISTS dw.fact_waste_generation (
    sk_proyecto BIGINT NOT NULL,
    waste_generator_key BIGINT NOT NULL,
    sk_tiempo BIGINT NOT NULL,
    waste_type_key BIGINT NOT NULL,
    dangerous_waste_key BIGINT,
    danger_class_key BIGINT,
    geo_location_key BIGINT,
    quantity_generated NUMERIC(15,3),
    quantity_delivered NUMERIC(15,3),
    quantity_stored NUMERIC(15,3),
    unit VARCHAR(50),
    record_year INT,
    FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto),
    FOREIGN KEY (waste_generator_key) REFERENCES dw.dim_waste_generator(waste_generator_key),
    FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo),
    FOREIGN KEY (waste_type_key) REFERENCES dw.dim_waste_type(waste_type_key),
    FOREIGN KEY (dangerous_waste_key) REFERENCES dw.dim_dangerous_waste(dangerous_waste_key),
    FOREIGN KEY (danger_class_key) REFERENCES dw.dim_dangerous_classification(danger_class_key)
);

-- 2.2 Hechos Aplicación / Uso de Sustancias Químicas
CREATE TABLE IF NOT EXISTS dw.fact_chemical_application (
    sk_proyecto BIGINT NOT NULL,
    chemical_key BIGINT NOT NULL,
    sk_tiempo BIGINT NOT NULL,
    storage_key BIGINT,
    geo_location_key BIGINT,
    dose NUMERIC(15,3),
    dose_unit VARCHAR(50),
    application_method VARCHAR(200),
    area_covered NUMERIC(15,3),
    usage_year INT,
    FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto),
    FOREIGN KEY (chemical_key) REFERENCES dw.dim_chemical_substance(chemical_key),
    FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo),
    FOREIGN KEY (storage_key) REFERENCES dw.dim_chemical_storage(storage_key)
);

-- 2.3 Hechos de Impacto Ambiental (Tabla Puente / Agregada)
CREATE TABLE IF NOT EXISTS dw.fact_project_environmental_impact (
    sk_proyecto BIGINT NOT NULL,
    sk_tiempo BIGINT NOT NULL,
    total_waste_volume NUMERIC(15,3),
    total_dangerous_waste_volume NUMERIC(15,3),
    total_chemical_dose NUMERIC(15,3),
    environmental_risk_score NUMERIC(10,2),
    PRIMARY KEY (sk_proyecto, sk_tiempo),
    FOREIGN KEY (sk_proyecto) REFERENCES dw.dim_proyecto(sk_proyecto),
    FOREIGN KEY (sk_tiempo) REFERENCES dw.dim_tiempo(sk_tiempo)
);

-- 3. ÍNDICES Y OPTIMIZACIÓN
CREATE INDEX IF NOT EXISTS idx_fact_waste_project ON dw.fact_waste_generation(sk_proyecto);
CREATE INDEX IF NOT EXISTS idx_fact_waste_date ON dw.fact_waste_generation(sk_tiempo);

CREATE INDEX IF NOT EXISTS idx_fact_chem_project ON dw.fact_chemical_application(sk_proyecto);
CREATE INDEX IF NOT EXISTS idx_fact_chem_date ON dw.fact_chemical_application(sk_tiempo);

CREATE INDEX IF NOT EXISTS idx_fact_impact_project ON dw.fact_project_environmental_impact(sk_proyecto);
CREATE INDEX IF NOT EXISTS idx_fact_impact_date ON dw.fact_project_environmental_impact(sk_tiempo);
