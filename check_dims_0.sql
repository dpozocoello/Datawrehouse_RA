SELECT 'dim_chemical_substance' as tab, count(*) FROM dw.dim_chemical_substance WHERE chemical_key = 0
UNION ALL
SELECT 'dim_chemical_importer', count(*) FROM dw.dim_chemical_importer WHERE importer_key = 0
UNION ALL
SELECT 'dim_proyecto', count(*) FROM dw.dim_proyecto WHERE sk_proyecto = 0;
