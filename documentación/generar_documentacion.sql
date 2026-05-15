-- ============================================================================
-- SCRIPT: Generar Documentación Automática del Esquema
-- Descripción: Genera documentación completa en formato texto
-- Autor: DBA PostgreSQL - MAATE
-- ============================================================================
--- '=========================================' --- 'GENERADOR DE DOCUMENTACIÓN DE ESQUEMA' --- '=========================================' --- '' --- 'DATABASE: ' :DBNAME --- 'FECHA: ' :DATE --- '' -- 1. RESUMEN GENERAL
--- '========== RESUMEN GENERAL ==========' --- ''
SELECT count(DISTINCT table_schema) as esquemas,
    count(DISTINCT table_name) as tablas,
    (
        SELECT count(*)
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    ) as columnas,
    (
        SELECT count(*)
        FROM information_schema.table_constraints
        WHERE constraint_type = 'PRIMARY KEY'
            AND table_schema NOT IN ('pg_catalog', 'information_schema')
    ) as claves_primarias,
    (
        SELECT count(*)
        FROM information_schema.table_constraints
        WHERE constraint_type = 'FOREIGN KEY'
            AND table_schema NOT IN ('pg_catalog', 'information_schema')
    ) as foreign_keys
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    AND table_type = 'BASE TABLE';
--- '' -- 2. CATÁLOGO DE TABLAS CON DESCRIPCIÓN
--- '========== CATÁLOGO DE TABLAS ==========' --- ''
SELECT t.table_schema as "Esquema",
    t.table_name as "Tabla",
    (
        SELECT count(*)
        FROM information_schema.columns c
        WHERE c.table_schema = t.table_schema
            AND c.table_name = t.table_name
    ) as "Columnas",
    pg_size_pretty(
        pg_total_relation_size(t.table_schema || '.' || t.table_name)
    ) as "Tamaño",
    COALESCE(
        obj_description((t.table_schema || '.' || t.table_name)::regclass),
        'Sin descripción'
    ) as "Descripción"
FROM information_schema.tables t
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
    AND t.table_type = 'BASE TABLE'
ORDER BY t.table_schema,
    t.table_name;
--- '' -- 3. DICCIONARIO DE DATOS (Ejemplo para una tabla)
--- '========== DICCIONARIO DE DATOS (Ejemplo) ==========' --- 'Ejecute esta consulta cambiando el filtro WHERE para cada tabla' --- '' -- Plantilla de diccionario de datos (descomentar y ajustar)
/*
 SELECT 
 c.ordinal_position as "Pos",
 c.column_name as "Columna",
 CASE 
 WHEN c.character_maximum_length IS NOT NULL 
 THEN c.data_type || '(' || c.character_maximum_length || ')'
 WHEN c.numeric_precision IS NOT NULL 
 THEN c.data_type || '(' || c.numeric_precision || ',' || c.numeric_scale || ')'
 ELSE c.data_type
 END as "Tipo",
 CASE WHEN c.is_nullable = 'YES' THEN 'Sí' ELSE 'No' END as "Nulo",
 c.column_default as "Default",
 CASE 
 WHEN pk.column_name IS NOT NULL THEN 'PK'
 WHEN fk.column_name IS NOT NULL THEN 'FK → ' || fk.tabla_referencia
 ELSE ''
 END as "Constraint",
 COALESCE(col_description((c.table_schema||'.'||c.table_name)::regclass, c.ordinal_position), '') as "Descripción"
 FROM information_schema.columns c
 LEFT JOIN (
 SELECT kcu.table_schema, kcu.table_name, kcu.column_name
 FROM information_schema.key_column_usage kcu
 JOIN information_schema.table_constraints tc 
 ON kcu.constraint_name = tc.constraint_name
 WHERE tc.constraint_type = 'PRIMARY KEY'
 ) pk ON c.table_schema = pk.table_schema 
 AND c.table_name = pk.table_name 
 AND c.column_name = pk.column_name
 LEFT JOIN (
 SELECT 
 kcu.table_schema,
 kcu.table_name,
 kcu.column_name,
 ccu.table_name as tabla_referencia
 FROM information_schema.key_column_usage kcu
 JOIN information_schema.table_constraints tc 
 ON kcu.constraint_name = tc.constraint_name
 JOIN information_schema.constraint_column_usage ccu 
 ON tc.constraint_name = ccu.constraint_name
 WHERE tc.constraint_type = 'FOREIGN KEY'
 ) fk ON c.table_schema = fk.table_schema 
 AND c.table_name = fk.table_name 
 AND c.column_name = fk.column_name
 WHERE c.table_schema = 'public'  -- Cambiar por su esquema
 AND c.table_name = 'SU_TABLA'  -- Cambiar por su tabla
 ORDER BY c.ordinal_position;
 */
--- '' --- '=========================================' --- 'Para generar documentación completa,' --- 'ejecute este script y guarde la salida:' --- 'psql -h servidor -U user -d db -f generar_documentacion.sql > documentacion.txt' --- '========================================='