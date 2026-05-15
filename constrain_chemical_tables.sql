-- 1. FACT_CHEMICAL_MOVEMENT
DROP TABLE IF EXISTS dw.fact_chemical_movement_tmp;
CREATE TABLE dw.fact_chemical_movement_tmp AS 
SELECT DISTINCT ON (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number) * 
FROM dw.fact_chemical_movement 
ORDER BY sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number;

TRUNCATE dw.fact_chemical_movement;

INSERT INTO dw.fact_chemical_movement SELECT * FROM dw.fact_chemical_movement_tmp;

ALTER TABLE dw.fact_chemical_movement 
ADD CONSTRAINT unique_chemical_movement 
UNIQUE (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number);

DROP TABLE dw.fact_chemical_movement_tmp;

-- 2. FACT_CHEMICAL_DECLARATION
DROP TABLE IF EXISTS dw.fact_chemical_declaration_tmp;
CREATE TABLE dw.fact_chemical_declaration_tmp AS 
SELECT DISTINCT ON (sk_proyecto, importer_key, sk_tiempo, declaration_year, declaration_month) * 
FROM dw.fact_chemical_declaration 
ORDER BY sk_proyecto, importer_key, sk_tiempo, declaration_year, declaration_month;

TRUNCATE dw.fact_chemical_declaration;

INSERT INTO dw.fact_chemical_declaration SELECT * FROM dw.fact_chemical_declaration_tmp;

ALTER TABLE dw.fact_chemical_declaration 
ADD CONSTRAINT unique_chemical_declaration 
UNIQUE (sk_proyecto, importer_key, sk_tiempo, declaration_year, declaration_month);

DROP TABLE dw.fact_chemical_declaration_tmp;
