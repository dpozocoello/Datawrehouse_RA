-- ==============================================================================
-- SCRIPT DE LIMPIEZA DINÁMICA - DATA WAREHOUSE RGD v2.0
-- Propósito: Truncar TODAS las tablas de los esquemas dw y stg.
-- ==============================================================================

DO $$ 
DECLARE 
    r RECORD;
BEGIN
    -- Desactivar triggers temporalmente para mayor velocidad si es necesario
    -- SET session_replication_role = 'replica'; 

    RAISE NOTICE 'Iniciando limpieza de esquemas dw y stg...';

    FOR r IN (
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname IN ('dw', 'stg')
    ) LOOP
        RAISE NOTICE 'Truncando tabla: %.%', r.schemaname, r.tablename;
        EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.schemaname) || '.' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;

    -- Reiniciar secuencias de los esquemas
    -- (Opcional, pero recomendado para un reset total)
    
    RAISE NOTICE 'Limpieza completada exitosamente.';
END $$;
