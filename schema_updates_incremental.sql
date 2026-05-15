-- 1. Add Unique Constraint to allow UPSERT
ALTER TABLE dw.fact_waste_generation 
DROP CONSTRAINT IF EXISTS unique_waste_generation;

ALTER TABLE dw.fact_waste_generation 
ADD CONSTRAINT unique_waste_generation 
UNIQUE (sk_proyecto, waste_generator_key, sk_tiempo, waste_type_key);

-- 2. Create Logging Table
CREATE TABLE IF NOT EXISTS dw.etl_process_log (
    id SERIAL PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    status VARCHAR(20), -- 'SUCCESS', 'ERROR', 'RUNNING'
    rows_inserted INTEGER DEFAULT 0,
    rows_updated INTEGER DEFAULT 0,
    error_message TEXT,
    execution_mode VARCHAR(20) -- 'FULL', 'INCREMENTAL'
);
