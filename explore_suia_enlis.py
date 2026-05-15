"""
Arquitecto de Datos - Exploración de suia_enlis
Servidor: 172.16.0.179:5632
Objetivo: Identificar tablas de Oficinas Técnicas y Zonales
"""
import psycopg2
import sys

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "dbname": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
    "connect_timeout": 15
}

def separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)

def main():
    print("Conectando a suia_enlis en 172.16.0.179:5632 ...")
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        conn.autocommit = True
        cur = conn.cursor()
        print("✓ Conexión exitosa.\n")
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        sys.exit(1)

    # ── 1. Schemas disponibles ───────────────────────────────────────────────
    separator("1. SCHEMAS DE LA BASE DE DATOS suia_enlis")
    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('information_schema','pg_catalog','pg_toast')
        ORDER BY schema_name;
    """)
    schemas = [r[0] for r in cur.fetchall()]
    for s in schemas:
        print(f"  • {s}")

    # ── 2. Todas las tablas ──────────────────────────────────────────────────
    separator("2. LISTADO COMPLETO DE TABLAS")
    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('information_schema','pg_catalog','pg_toast')
        ORDER BY table_schema, table_name;
    """)
    all_tables = cur.fetchall()
    print(f"  Total de tablas encontradas: {len(all_tables)}\n")
    for schema, table in all_tables:
        print(f"  [{schema}] {table}")

    # ── 3. Tablas candidatas por nombre ──────────────────────────────────────
    separator("3. TABLAS CANDIDATAS (palabras clave: oficina, zonal, tecni, area, sede, regional, dependencia, unidad, localidad, provincia, canton, distrito, parroquia, circuito)")
    keywords = [
        'oficina', 'zonal', 'tecni', 'area', 'sede', 'regional',
        'dependencia', 'unidad', 'localidad', 'provincia',
        'canton', 'distrito', 'parroquia', 'circuito', 'coordinaci'
    ]
    candidates = [
        (s, t) for (s, t) in all_tables
        if any(k in t.lower() for k in keywords)
    ]
    print(f"  Tablas candidatas encontradas: {len(candidates)}\n")
    for schema, table in candidates:
        print(f"  ★  [{schema}] {table}")

    # ── 4. Detalle de columnas de tablas candidatas ──────────────────────────
    separator("4. DETALLE DE COLUMNAS (tablas candidatas)")
    for schema, table in candidates:
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema, table))
        cols = cur.fetchall()

        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s;
        """, (schema, table))

        # Contar registros
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}";')
            row_count = cur.fetchone()[0]
        except Exception:
            row_count = "N/A"
            conn.rollback()

        print(f"\n  ┌─ [{schema}].[{table}]  ({row_count} registros)")
        for col_name, dtype, maxlen, nullable in cols:
            len_str = f"({maxlen})" if maxlen else ""
            null_str = "NULL" if nullable == "YES" else "NOT NULL"
            print(f"  │   {col_name:<35} {dtype}{len_str} [{null_str}]")
        print(f"  └{'─'*60}")

    # ── 5. Búsqueda en columnas (por si el nombre está en los datos) ─────────
    separator("5. BÚSQUEDA DE 'oficina' Y 'zonal' EN NOMBRES DE COLUMNAS")
    cur.execute("""
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN ('information_schema','pg_catalog','pg_toast')
          AND (
              LOWER(column_name) LIKE '%oficina%'
           OR LOWER(column_name) LIKE '%zonal%'
           OR LOWER(column_name) LIKE '%tecnica%'
           OR LOWER(column_name) LIKE '%tecnico%'
          )
        ORDER BY table_schema, table_name, column_name;
    """)
    col_matches = cur.fetchall()
    print(f"  Columnas encontradas con términos clave: {len(col_matches)}\n")
    for schema, table, col, dtype in col_matches:
        print(f"  [{schema}].[{table}]  →  columna: {col}  ({dtype})")

    cur.close()
    conn.close()
    print("\n✓ Exploración completada.")

if __name__ == "__main__":
    main()
