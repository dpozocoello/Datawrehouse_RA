-- 1. Initialize Dimensional Integrity (Key 0)
INSERT INTO dw.dim_chemical_substance (chemical_key, chemical_id, substance_name)
SELECT 0, -1, 'N/A'
WHERE NOT EXISTS (SELECT 1 FROM dw.dim_chemical_substance WHERE chemical_key = 0)
ON CONFLICT (chemical_key) DO NOTHING;

INSERT INTO dw.dim_chemical_importer (importer_key, importer_id, importer_name)
SELECT 0, -1, 'N/A'
WHERE NOT EXISTS (SELECT 1 FROM dw.dim_chemical_importer WHERE importer_key = 0)
ON CONFLICT (importer_key) DO NOTHING;

-- 2. Add Unique Constraint to Fact Table for UPSERT support
-- Check if it already exists to avoid errors
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'unique_chemical_import') THEN
        ALTER TABLE dw.fact_chemical_import 
        ADD CONSTRAINT unique_chemical_import 
        UNIQUE (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number);
    END IF;
END $$;
