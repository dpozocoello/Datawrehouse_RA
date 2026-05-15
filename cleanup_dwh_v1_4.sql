-- DWH Cleanup Script v1.4 (REFINED)
-- Purge all data from Staging and DW schemas to allow fresh ingestion.
BEGIN;
-- 1. FACT TABLES
TRUNCATE TABLE dw.fact_regularizacion CASCADE;
TRUNCATE TABLE dw.fact_pago CASCADE;
-- 2. DIMENSION TABLES
TRUNCATE TABLE dw.dim_area CASCADE;
TRUNCATE TABLE dw.dim_proyecto CASCADE;
TRUNCATE TABLE dw.dim_proponente CASCADE;
TRUNCATE TABLE dw.dim_estado CASCADE;
TRUNCATE TABLE dw.dim_tipo_pago CASCADE;
TRUNCATE TABLE dw.dim_pago CASCADE;
TRUNCATE TABLE dw.dim_actividad CASCADE;
TRUNCATE TABLE dw.dim_geografia CASCADE;
-- 3. STAGING TABLES
TRUNCATE TABLE stg.suia_areas_bi CASCADE;
TRUNCATE TABLE stg.geographical_locations_bi CASCADE;
TRUNCATE TABLE stg.consolidado_proyectos CASCADE;
TRUNCATE TABLE stg.suia_rcoa_bi CASCADE;
TRUNCATE TABLE stg.suia_coa_bi CASCADE;
TRUNCATE TABLE stg.jbpm_snap_variables CASCADE;
TRUNCATE TABLE stg.online_payments_bi CASCADE;
TRUNCATE TABLE stg.financial_transaction_bi CASCADE;
TRUNCATE TABLE stg.online_payments_historical_bi CASCADE;
-- RESET SEQUENCES
ALTER SEQUENCE IF EXISTS dw.dim_proyecto_sk_proyecto_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS dw.dim_proponente_sk_proponente_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS dw.dim_area_sk_area_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS dw.dim_pago_sk_pago_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS dw.dim_tipo_pago_sk_tipo_pago_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS dw.dim_actividad_sk_actividad_seq RESTART WITH 1;
COMMIT;
ANALYZE;