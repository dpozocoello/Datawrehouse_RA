SELECT sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key, COUNT(*) 
FROM dw.fact_waste_generation 
GROUP BY 1,2,3,4 
HAVING COUNT(*) > 1 
LIMIT 20;
