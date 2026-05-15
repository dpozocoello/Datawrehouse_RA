-- Check and add missing column
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='dw' AND table_name='fact_waste_generation' AND column_name='source_system') THEN
        ALTER TABLE dw.fact_waste_generation ADD COLUMN source_system VARCHAR(50);
    END IF;
END $$;
