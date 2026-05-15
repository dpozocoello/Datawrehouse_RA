-- Fix for data type mismatch in fact_regularizacion
ALTER TABLE dw.fact_regularizacion
ALTER COLUMN interseccion_snap TYPE VARCHAR(100);
-- Also update the DDL file to reflect this change
-- (I'll do this in a separate step or just mention it)