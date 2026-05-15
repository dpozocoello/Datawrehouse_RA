-- 1. Create Deduplicated Backup Table
DROP TABLE IF EXISTS dw.fact_chemical_import_tmp;
CREATE TABLE dw.fact_chemical_import_tmp AS 
SELECT DISTINCT ON (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number) * 
FROM dw.fact_chemical_import 
ORDER BY sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number;

-- 2. Clear Original Table
TRUNCATE dw.fact_chemical_import;

-- 3. Restore Clean Data
INSERT INTO dw.fact_chemical_import 
SELECT * FROM dw.fact_chemical_import_tmp;

-- 4. Add the Unique Constraint
ALTER TABLE dw.fact_chemical_import 
ADD CONSTRAINT unique_chemical_import 
UNIQUE (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number);

-- 5. Cleanup
DROP TABLE dw.fact_chemical_import_tmp;

-- 6. Also ensure "N/A" records are present (if they failed earlier)
INSERT INTO dw.dim_chemical_substance (chemical_key, chemical_id, substance_name)
VALUES (0, -1, 'N/A')
ON CONFLICT (chemical_key) DO NOTHING;

INSERT INTO dw.dim_chemical_importer (importer_key, importer_id, importer_name)
VALUES (0, -1, 'N/A')
ON CONFLICT (importer_key) DO NOTHING;
