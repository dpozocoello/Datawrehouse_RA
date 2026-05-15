-- ============================================================================
-- SCRIPT 04 — DDL: Jerarquía Recursiva dim_area v3.0
-- Base de datos: dw_reg_v1
-- Ejecutar en: DBeaver conectado a localhost:5432 / postgres / dw_reg_v1
--
-- Cambios:
--   1. ALTER TABLE dw.dim_area    — 10 columnas de jerarquía
--   2. CREATE TABLE dw.bridge_area_jerarquia — bridge Kimball
--   3. Índices de soporte para consultas BI
--
-- Prerrequisito: Scripts 01, 02, 03 aplicados (dim_area v2.0 en pie)
-- ============================================================================


-- ============================================================================
-- PARTE 1: Columnas de jerarquía en dw.dim_area
-- ============================================================================
--
-- nivel_jerarquico : 1 = raíz, 2 = hijo, 3 = nieto
-- l1_id / l1_nombre / l1_siglas_tipo : ancestro nivel 1 (raíz) — siempre poblado
-- l2_id / l2_nombre / l2_siglas_tipo : ancestro nivel 2 — NULL si el nodo es raíz
-- ruta_ids         : cadena de IDs "558" | "558/278" | "558/278/999"
-- ruta_nombres     : breadcrumb "DIRECCIÓN NACIONAL FORESTAL > UNIDAD DE CONSERVACIÓN"
-- es_hoja          : TRUE si el nodo no tiene hijos (nodo terminal)
--
ALTER TABLE dw.dim_area
    ADD COLUMN IF NOT EXISTS nivel_jerarquico  SMALLINT      DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS l1_id             INTEGER       DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS l1_nombre         VARCHAR(255)  DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS l1_siglas_tipo    VARCHAR(10)   DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS l2_id             INTEGER       DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS l2_nombre         VARCHAR(255)  DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS l2_siglas_tipo    VARCHAR(10)   DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS ruta_ids          VARCHAR(200)  DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS ruta_nombres      TEXT          DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS es_hoja           BOOLEAN       DEFAULT NULL;

-- Índices para filtrado por nivel y ancestros
CREATE INDEX IF NOT EXISTS idx_dim_area_nivel   ON dw.dim_area(nivel_jerarquico);
CREATE INDEX IF NOT EXISTS idx_dim_area_l1_id   ON dw.dim_area(l1_id);
CREATE INDEX IF NOT EXISTS idx_dim_area_l2_id   ON dw.dim_area(l2_id);
CREATE INDEX IF NOT EXISTS idx_dim_area_es_hoja ON dw.dim_area(es_hoja);


-- ============================================================================
-- PARTE 2: Bridge table — Kimball variable-depth hierarchy
-- ============================================================================
--
-- Almacena TODAS las relaciones ancestro ↔ descendiente con su distancia.
-- Permite responder "todos los descendientes de X" con un simple JOIN y
-- sin CTEs recursivas en tiempo de consulta — fundamental para BI.
--
-- Distancias:
--   0 = self (cada nodo es ancestro de sí mismo)
--   1 = padre directo
--   2 = abuelo
--
-- Uso típico en Power BI / Tableau:
--   SELECT d.* FROM dw.dim_area d
--   JOIN dw.bridge_area_jerarquia b ON b.sk_area_descendiente = d.sk_area
--   WHERE b.id_area_ancestro = :id_zona AND b.distancia > 0
--
CREATE TABLE IF NOT EXISTS dw.bridge_area_jerarquia (
    sk_area_descendiente  INTEGER   NOT NULL,
    sk_area_ancestro      INTEGER   NOT NULL,
    id_area_descendiente  INTEGER   NOT NULL,
    id_area_ancestro      INTEGER   NOT NULL,
    distancia             SMALLINT  NOT NULL,   -- 0=self  1=padre  2=abuelo
    es_hoja               BOOLEAN   NOT NULL DEFAULT FALSE,
    es_raiz               BOOLEAN   NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_bridge_area_jerarquia
        PRIMARY KEY (sk_area_descendiente, sk_area_ancestro),
    CONSTRAINT fk_bridge_area_desc
        FOREIGN KEY (sk_area_descendiente) REFERENCES dw.dim_area(sk_area)
        ON DELETE CASCADE,
    CONSTRAINT fk_bridge_area_anc
        FOREIGN KEY (sk_area_ancestro) REFERENCES dw.dim_area(sk_area)
        ON DELETE CASCADE
);

-- Índices para los patrones de consulta más frecuentes en BI
CREATE INDEX IF NOT EXISTS idx_bridge_area_ancestro
    ON dw.bridge_area_jerarquia(sk_area_ancestro);

CREATE INDEX IF NOT EXISTS idx_bridge_area_distancia
    ON dw.bridge_area_jerarquia(distancia);

CREATE INDEX IF NOT EXISTS idx_bridge_area_hojas_raiz
    ON dw.bridge_area_jerarquia(es_raiz, es_hoja);

CREATE INDEX IF NOT EXISTS idx_bridge_area_id_anc
    ON dw.bridge_area_jerarquia(id_area_ancestro, distancia);


-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_area'
  AND column_name IN (
      'nivel_jerarquico','l1_id','l1_nombre','l1_siglas_tipo',
      'l2_id','l2_nombre','l2_siglas_tipo','ruta_ids','ruta_nombres','es_hoja'
  )
ORDER BY column_name;

SELECT table_name, (SELECT COUNT(*) FROM dw.bridge_area_jerarquia) AS filas_bridge
FROM information_schema.tables
WHERE table_schema = 'dw' AND table_name = 'bridge_area_jerarquia';
