-- ==============================================================================
-- PARCHE QUIRURGICO PARA STG.ONLINE_PAYMENTS_HISTORICAL_BI
-- Corrige columna faltante y asegura tipos de texto para procesamiento.
-- ==============================================================================

DO $$ 
BEGIN
    -- 1. Agregar columna retired_value_1 si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'stg' 
          AND table_name = 'online_payments_historical_bi' 
          AND column_name = 'retired_value_1'
    ) THEN
        ALTER TABLE stg.online_payments_historical_bi ADD COLUMN retired_value_1 character varying;
        RAISE NOTICE 'Columna retired_value_1 agregada.';
    END IF;

    -- 2. Asegurar que campos de montos son TEXT/VARCHAR (para compatibilidad con REPLACE)
    -- Si por alguna razon son double precision, los convertimos.
    ALTER TABLE stg.online_payments_historical_bi ALTER COLUMN value_updated TYPE character varying;
    ALTER TABLE stg.online_payments_historical_bi ALTER COLUMN retired_value TYPE character varying;

END $$;
