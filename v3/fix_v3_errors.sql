-- ==============================================================================
-- FIX: fix_v3_errors.sql
-- ==============================================================================

-- 1. Asegurar que la columna retired_value_1 existe en stg.online_payments_historical_bi
-- Se usa un bloque anónimo para evitar errores si ya existe
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema='stg' AND table_name='online_payments_historical_bi' 
                   AND column_name='retired_value_1') THEN
        ALTER TABLE stg.online_payments_historical_bi ADD COLUMN retired_value_1 character varying;
    END IF;
END $$;

-- 2. Asegurar que retired_value existe (por si acaso)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema='stg' AND table_name='online_payments_historical_bi' 
                   AND column_name='retired_value') THEN
        ALTER TABLE stg.online_payments_historical_bi ADD COLUMN retired_value character varying;
    END IF;
END $$;

-- 3. Los casts de REPLACE ya están en el archivo etl_carga_datos_v3.sql, 
-- pero nos aseguramos de que el archivo en disco sea el correcto.
-- (Este script no modifica el archivo .sql, solo aplica el cambio en la DB si fuera necesario, 
-- pero el etl_carga_datos_v3.sql se encargará en la siguiente ejecución).
