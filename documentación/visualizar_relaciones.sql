-- ============================================================================
-- SCRIPT: Visualizar Relaciones y Foreign Keys
-- Descripción: Mapea todas las relaciones entre tablas mediante foreign keys
--              Identifica dependencias y estructura relacional
-- Autor: DBA PostgreSQL - MAATE
-- ============================================================================
--- '=========================================' --- 'ANÁLISIS DE RELACIONES ENTRE TABLAS' --- '=========================================' --- '' -- 1. TODAS LAS FOREIGN KEYS DE LA BASE DE DATOS
--- '1. FOREIGN KEYS DEFINIDAS' --- '-------------------------'
SELECT tc.table_schema as esquema_origen,
    tc.table_name as tabla_origen,
    kcu.column_name as columna_origen,
    ccu.table_schema as esquema_destino,
    ccu.table_name as tabla_destino,
    ccu.column_name as columna_destino,
    tc.constraint_name as nombre_fk,
    rc.update_rule as regla_update,
    rc.delete_rule as regla_delete
FROM information_schema.table_constraints as tc
    JOIN information_schema.key_column_usage as kcu ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage as ccu ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
    JOIN information_schema.referential_constraints as rc ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY tc.table_schema,
    tc.table_name,
    kcu.column_name;
--- '' -- 2. CONTEO DE RELACIONES POR TABLA
--- '2. TABLAS MÁS CONECTADAS' --- '------------------------' WITH fk_origen AS (
    SELECT tc.table_schema,
        tc.table_name,
        count(*) as fk_salientes
    FROM information_schema.table_constraints tc
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    GROUP BY tc.table_schema,
        tc.table_name
),
fk_destino AS (
    SELECT ccu.table_schema,
        ccu.table_name,
        count(*) as fk_entrantes
    FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND ccu.table_schema NOT IN ('pg_catalog', 'information_schema')
    GROUP BY ccu.table_schema,
        ccu.table_name
)
SELECT COALESCE(o.table_schema, d.table_schema) as esquema,
    COALESCE(o.table_name, d.table_name) as tabla,
    COALESCE(o.fk_salientes, 0) as relaciones_hacia_otras,
    COALESCE(d.fk_entrantes, 0) as relaciones_desde_otras,
    COALESCE(o.fk_salientes, 0) + COALESCE(d.fk_entrantes, 0) as total_relaciones,
    CASE
        WHEN COALESCE(d.fk_entrantes, 0) > COALESCE(o.fk_salientes, 0) THEN 'Tabla Maestra/Catálogo'
        WHEN COALESCE(o.fk_salientes, 0) > COALESCE(d.fk_entrantes, 0) THEN 'Tabla Dependiente'
        ELSE 'Tabla Intermedia'
    END as tipo_tabla
FROM fk_origen o
    FULL OUTER JOIN fk_destino d ON o.table_schema = d.table_schema
    AND o.table_name = d.table_name
ORDER BY total_relaciones DESC,
    esquema,
    tabla;
--- '' -- 3. IDENTIFICAR TABLAS CENTRALES (HUBs)
--- '3. TABLAS CENTRALES (Núcleo del Sistema)' --- '-----------------------------------------' WITH fk_destino AS (
    SELECT ccu.table_schema,
        ccu.table_name,
        count(DISTINCT tc.table_name) as tablas_dependientes
    FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND ccu.table_schema NOT IN ('pg_catalog', 'information_schema')
    GROUP BY ccu.table_schema,
        ccu.table_name
)
SELECT fd.table_schema as esquema,
    fd.table_name as tabla_central,
    fd.tablas_dependientes,
    pg_size_pretty(
        pg_total_relation_size(fd.table_schema || '.' || fd.table_name)
    ) as tamaño,
    'TABLA CRÍTICA' as importancia
FROM fk_destino fd
WHERE fd.tablas_dependientes >= 3 -- Tablas con 3+ dependientes
ORDER BY fd.tablas_dependientes DESC,
    fd.table_schema,
    fd.table_name;
--- '' -- 4. CADENAS DE DEPENDENCIA (Jerarquías)
--- '4. CADENAS DE DEPENDENCIA' --- '-------------------------' --- 'Mostrando relaciones con múltiples niveles' --- '' WITH RECURSIVE dep_tree AS (
    -- Tablas sin dependencias (raíz)
    SELECT t.table_schema,
        t.table_name,
        0 as nivel,
        t.table_schema || '.' || t.table_name as ruta
    FROM information_schema.tables t
        LEFT JOIN information_schema.table_constraints tc ON t.table_name = tc.table_name
        AND t.table_schema = tc.table_schema
        AND tc.constraint_type = 'FOREIGN KEY'
    WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
        AND t.table_type = 'BASE TABLE'
        AND tc.constraint_name IS NULL
    UNION ALL
    -- Tablas dependientes
    SELECT tc.table_schema,
        tc.table_name,
        dt.nivel + 1,
        dt.ruta || ' -> ' || tc.table_schema || '.' || tc.table_name
    FROM dep_tree dt
        JOIN information_schema.table_constraints tc ON dt.table_schema = tc.table_schema
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND dt.table_name = ccu.table_name
        AND dt.nivel < 5 -- Limitar profundidad para evitar ciclos
)
SELECT DISTINCT nivel,
    table_schema as esquema,
    table_name as tabla,
    ruta
FROM dep_tree
WHERE nivel <= 3 -- Mostrar primeros 3 niveles
ORDER BY nivel,
    table_schema,
    table_name;
--- '' -- 5. DETECTAR RELACIONES CIRCULARES
--- '5. DETECTAR POSIBLES CICLOS EN RELACIONES' --- '------------------------------------------' WITH grafo_fk AS (
    SELECT DISTINCT tc.table_schema || '.' || tc.table_name as tabla_a,
        ccu.table_schema || '.' || ccu.table_name as tabla_b
    FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
)
SELECT g1.tabla_a,
    g1.tabla_b,
    'Posible ciclo detectado' as advertencia
FROM grafo_fk g1
    JOIN grafo_fk g2 ON g1.tabla_b = g2.tabla_a
    AND g1.tabla_a = g2.tabla_b
WHERE g1.tabla_a < g1.tabla_b -- Evitar duplicados
ORDER BY g1.tabla_a;
--- '' -- 6. REGLAS DE CASCADA
--- '6. REGLAS DE DELETE Y UPDATE' --- '-----------------------------'
SELECT tc.table_schema as esquema,
    tc.table_name as tabla_origen,
    ccu.table_name as tabla_referenciada,
    tc.constraint_name as nombre_fk,
    rc.delete_rule as regla_delete,
    rc.update_rule as regla_update,
    CASE
        WHEN rc.delete_rule = 'CASCADE' THEN '⚠ DELETE en cascada activo'
        WHEN rc.delete_rule = 'SET NULL' THEN 'ℹ DELETE establece NULL'
        WHEN rc.delete_rule = 'NO ACTION' THEN '✓ DELETE protegido'
        ELSE rc.delete_rule
    END as descripcion_delete
FROM information_schema.table_constraints tc
    JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
    JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY rc.delete_rule,
    tc.table_schema,
    tc.table_name;
--- '' -- 7. RELACIONES MUCHOS A MUCHOS (Tablas intermedias)
--- '7. IDENTIFICAR TABLAS INTERMEDIAS (M:N)' --- '---------------------------------------' WITH tabla_fks AS (
    SELECT tc.table_schema,
        tc.table_name,
        count(*) as num_fk
    FROM information_schema.table_constraints tc
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    GROUP BY tc.table_schema,
        tc.table_name
    HAVING count(*) >= 2
),
tabla_columnas AS (
    SELECT table_schema,
        table_name,
        count(*) as num_columnas
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    GROUP BY table_schema,
        table_name
)
SELECT tf.table_schema as esquema,
    tf.table_name as tabla_intermedia,
    tf.num_fk as foreign_keys,
    tc.num_columnas as total_columnas,
    'Posible relación N:M' as tipo
FROM tabla_fks tf
    JOIN tabla_columnas tc ON tf.table_schema = tc.table_schema
    AND tf.table_name = tc.table_name
WHERE tc.num_columnas = tf.num_fk + 1 -- Solo FK + PK (opcional)
    OR tc.num_columnas = tf.num_fk -- Solo FKs
ORDER BY tf.table_schema,
    tf.table_name;
--- '' --- '=========================================' --- 'ANÁLISIS DE RELACIONES COMPLETADO' --- '=========================================' --- '' --- 'PUNTOS A REVISAR:' --- '1. Valide tablas centrales identificadas' --- '2. Revise ciclos detectados' --- '3. Verifique reglas de cascada' --- '4. Documente relaciones M:N' --- ''