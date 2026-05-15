-- ==============================================================================
-- DDL v2 — CAMBIOS ESTRUCTURALES sobre dw_reg_v1
-- Aplicar DESPUÉS de tener la v1 funcionando
-- Ejecutar: psql -U postgres -d dw_reg_v1 -f ddl_dwh_v2.sql
-- ==============================================================================
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 1. dim_geografia — Jerarquía recursiva (provincia → cantón → parroquia)   ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
-- 1.1 Agregar columnas de jerarquía
ALTER TABLE dw.dim_geografia
ADD COLUMN IF NOT EXISTS sk_padre INT REFERENCES dw.dim_geografia(sk_geografia),
    ADD COLUMN IF NOT EXISTS nivel VARCHAR(20) DEFAULT 'PARROQUIA';
-- 1.2 Poblar jerarquía: crear nodos de Provincia y Cantón (nivel superior)
-- Primero insertar niveles de PROVINCIA como nodos raíz (sin padre)
INSERT INTO dw.dim_geografia (provincia, canton, parroquia, nivel, sk_padre)
SELECT DISTINCT provincia,
    '__NIVEL_PROVINCIA__',
    '__NIVEL_PROVINCIA__',
    'PROVINCIA',
    NULL
FROM dw.dim_geografia
WHERE nivel = 'PARROQUIA'
    OR nivel IS NULL ON CONFLICT (provincia, canton, parroquia) DO
UPDATE
SET nivel = 'PROVINCIA';
-- Insertar niveles de CANTON con padre = su provincia
INSERT INTO dw.dim_geografia (provincia, canton, parroquia, nivel, sk_padre)
SELECT DISTINCT g.provincia,
    g.canton,
    '__NIVEL_CANTON__',
    'CANTON',
    prov.sk_geografia
FROM dw.dim_geografia g
    JOIN dw.dim_geografia prov ON prov.provincia = g.provincia
    AND prov.canton = '__NIVEL_PROVINCIA__'
    AND prov.nivel = 'PROVINCIA'
WHERE (
        g.nivel = 'PARROQUIA'
        OR g.nivel IS NULL
    ) ON CONFLICT (provincia, canton, parroquia) DO
UPDATE
SET nivel = 'CANTON',
    sk_padre = EXCLUDED.sk_padre;
-- Actualizar parroquias existentes: asignar padre = su cantón
UPDATE dw.dim_geografia parr
SET nivel = 'PARROQUIA',
    sk_padre = canton_node.sk_geografia
FROM dw.dim_geografia canton_node
WHERE canton_node.provincia = parr.provincia
    AND canton_node.canton = parr.canton
    AND canton_node.parroquia = '__NIVEL_CANTON__'
    AND canton_node.nivel = 'CANTON'
    AND parr.parroquia != '__NIVEL_CANTON__'
    AND parr.parroquia != '__NIVEL_PROVINCIA__';
CREATE INDEX IF NOT EXISTS idx_dim_geo_padre ON dw.dim_geografia(sk_padre);
CREATE INDEX IF NOT EXISTS idx_dim_geo_nivel ON dw.dim_geografia(nivel);
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 2. Bridge Table: Proyecto ↔ Geografía (M:N)                              ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
CREATE TABLE IF NOT EXISTS dw.fact_proyecto_geografia (
    sk_proyecto INT REFERENCES dw.dim_proyecto(sk_proyecto),
    sk_geografia INT REFERENCES dw.dim_geografia(sk_geografia),
    es_principal BOOLEAN DEFAULT false,
    fecha_carga TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (sk_proyecto, sk_geografia)
);
CREATE INDEX IF NOT EXISTS idx_fpg_proyecto ON dw.fact_proyecto_geografia(sk_proyecto);
CREATE INDEX IF NOT EXISTS idx_fpg_geografia ON dw.fact_proyecto_geografia(sk_geografia);
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 3. dim_proyecto — Agregar area_responsable                                ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
ALTER TABLE dw.dim_proyecto
ADD COLUMN IF NOT EXISTS area_responsable TEXT;
-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║ 4. fact_pago — Campos de secuencia y depósito                             ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
-- 4.1 Modificar constraint para soportar multi-proyecto
-- (ya se hizo en fix_integridad_pagos.sql, pero asegurar idempotencia)
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'uk_fact_pago_dedup'
        AND conrelid = 'dw.fact_pago'::regclass
) THEN -- Verificar si ya tiene 3 columnas
IF (
    SELECT COUNT(1)
    FROM pg_constraint c
    WHERE c.conname = 'uk_fact_pago_dedup'
        AND c.conrelid = 'dw.fact_pago'::regclass
        AND array_length(c.conkey, 1) = 2
) > 0 THEN
ALTER TABLE dw.fact_pago DROP CONSTRAINT uk_fact_pago_dedup;
ALTER TABLE dw.fact_pago
ADD CONSTRAINT uk_fact_pago_dedup UNIQUE (sk_proyecto, id_transaccion_origen, origen);
END IF;
END IF;
END $$;
-- 4.2 Agregar campos de secuencia de pago
ALTER TABLE dw.fact_pago
ADD COLUMN IF NOT EXISTS secuencia_pago INT,
    ADD COLUMN IF NOT EXISTS es_deposito_inicial BOOLEAN DEFAULT false,
    ADD COLUMN IF NOT EXISTS monto_acumulado NUMERIC(12, 2);
CREATE INDEX IF NOT EXISTS idx_fact_pago_tramite ON dw.fact_pago(numero_tramite);
CREATE INDEX IF NOT EXISTS idx_fact_pago_secuencia ON dw.fact_pago(numero_tramite, secuencia_pago);