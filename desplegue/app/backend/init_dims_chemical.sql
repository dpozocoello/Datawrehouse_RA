-- 1. Initialize Dimensional Integrity (Key 0)
INSERT INTO dw.dim_chemical_substance (chemical_key, chemical_id, substance_name)
VALUES (0, -1, 'N/A')
ON CONFLICT (chemical_key) DO NOTHING;

INSERT INTO dw.dim_chemical_importer (importer_key, importer_id, importer_name)
VALUES (0, -1, 'N/A')
ON CONFLICT (importer_key) DO NOTHING;

-- 2. Add Unique Constraint to Fact Table for UPSERT support
ALTER TABLE dw.fact_chemical_import 
DROP CONSTRAINT IF EXISTS unique_chemical_import;

ALTER TABLE dw.fact_chemical_import 
ADD CONSTRAINT unique_chemical_import 
UNIQUE (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number);
