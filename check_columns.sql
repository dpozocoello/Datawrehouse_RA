SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'dw' AND table_name = 'fact_waste_generation';
