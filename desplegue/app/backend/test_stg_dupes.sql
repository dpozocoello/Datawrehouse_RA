WITH resolved_stg AS (
    SELECT 
        stg.*,
        'SN-PROY' as final_project_code -- Simplificado para test
    FROM stg.stg_fact_waste_generation stg
)
SELECT 
    sk_proyecto, waste_generator_key, dt.sk_tiempo, dwt.waste_type_key, COUNT(*)
FROM resolved_stg stg
LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = stg.final_project_code
JOIN dw.dim_waste_generator dwg ON dwg.waste_generator_id = stg.waste_generator_id
JOIN dw.dim_tiempo dt ON dt.fecha = DATE(stg.date_generated)
LEFT JOIN dw.dim_waste_type dwt ON dwt.cawa_id = stg.waste_type_id::int
GROUP BY 1,2,3,4
HAVING COUNT(*) > 1
LIMIT 10;
