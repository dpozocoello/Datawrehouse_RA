
-- ==============================================================================
-- cleanup_chemical_orphans.sql
-- ==============================================================================
-- Este script elimina registros huérfanos (sk_proyecto = 0) que ahora tienen
-- un registro vinculado equivalente (sk_proyecto != 0).
-- ==============================================================================

BEGIN;

BEGIN;

-- 1. Limpiar importaciones (basado en source_system seguro)
DELETE FROM dw.fact_chemical_import WHERE source_system IS NULL OR source_system != 'COA_IMPORT';

-- 2. Reiniciar movimientos y declaraciones (se recargarán totalmente del staging)
TRUNCATE dw.fact_chemical_movement RESTART IDENTITY;
TRUNCATE dw.fact_chemical_declaration RESTART IDENTITY;

COMMIT;
