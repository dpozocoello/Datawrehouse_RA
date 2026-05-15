-- ==============================================================================
-- etl_chemical_imports_load.sql (v12.1.0 AUTÓNOMO)
-- ==============================================================================
-- Este script ejecuta la carga unificada de Importaciones, Movimientos y 
-- Declaraciones Químicas mediante el SP dw.sp_etl_chemical_all().
-- ==============================================================================

SELECT dw.sp_etl_chemical_all();
