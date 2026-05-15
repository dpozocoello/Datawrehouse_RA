SELECT 'fact_chemical_import' as tab, count(*) FROM dw.fact_chemical_import
UNION ALL
SELECT 'fact_chemical_movement', count(*) FROM dw.fact_chemical_movement
UNION ALL
SELECT 'fact_chemical_declaration', count(*) FROM dw.fact_chemical_declaration;
