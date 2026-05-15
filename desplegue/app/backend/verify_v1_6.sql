SELECT 'dw.dim_waste_generator' as table, count(*) FROM dw.dim_waste_generator 
UNION ALL 
SELECT 'dw.fact_payment_traceability', count(*) FROM dw.fact_payment_traceability 
UNION ALL 
SELECT 'dw.dim_waste_generator_ruc', count(*) FROM dw.dim_waste_generator WHERE ruc_generator IS NOT NULL;
