-- ==============================================================================
-- SCRIPT DE LIMPIEZA TOTAL - DATA WAREHOUSE dw_reg_v1
-- Propósito: Truncar todas las tablas para permitir una carga desde cero.
-- ==============================================================================
-- 1. TABLAS DE HECHOS (FACT TABLES) - Eliminar primero por dependencias FK
TRUNCATE TABLE dw.fact_pago CASCADE;
TRUNCATE TABLE dw.fact_proyecto_geografia CASCADE;
TRUNCATE TABLE dw.fact_regularizacion CASCADE;
-- 2. TABLAS DIMENSIONALES
TRUNCATE TABLE dw.dim_proyecto CASCADE;
TRUNCATE TABLE dw.dim_proponente CASCADE;
TRUNCATE TABLE dw.dim_actividad CASCADE;
TRUNCATE TABLE dw.dim_usuario CASCADE;
TRUNCATE TABLE dw.dim_estado CASCADE;
TRUNCATE TABLE dw.dim_pago CASCADE;
-- Nota: dim_tiempo no se trunca usualmente ya que es estática, 
-- pero si se requiere "total desde cero", se puede incluir:
-- TRUNCATE TABLE dw.dim_tiempo CASCADE;
-- 3. TABLAS DE STAGING
TRUNCATE TABLE stg.suia_rcoa_bi CASCADE;
TRUNCATE TABLE stg.suia_coa_bi CASCADE;
TRUNCATE TABLE stg.jbpm_sector_bi CASCADE;
TRUNCATE TABLE stg.jbpm_4cat_bi CASCADE;
TRUNCATE TABLE stg.jbpm_hidro_bi CASCADE;
TRUNCATE TABLE stg.jbpm_snap_variables CASCADE;
TRUNCATE TABLE stg.consolidado_proyectos CASCADE;
TRUNCATE TABLE stg.online_payments_bi CASCADE;
TRUNCATE TABLE stg.financial_transaction_bi CASCADE;
TRUNCATE TABLE stg.online_payments_historical_bi CASCADE;
-- Reiniciar secuencias si es necesario
-- (Opcional, los TRUNCATE RESTART IDENTITY lo harían)
SELECT 'Limpieza completada exitosamente' as mensaje;