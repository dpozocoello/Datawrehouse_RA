"""
Generador de Diagramas ER en formato PNG usando matplotlib/graphviz.
Lee los metadatos extraídos de la base de datos suia_enlisy y genera
diagramas por esquema + un diagrama de relaciones cross-schema.
"""
import json
import os
import sys

# Configurar UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

OUTPUT_DIR = r"f:\Datawrehouse_RA\diagramas_er"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SCHEMAS = ["suia_iii", "coa_mae", "coa_waste_generator_record", "chemical_pesticides"]

def get_schema_summary(cur, schema):
    """Obtener resumen compacto: tablas, PKs, FKs."""
    # Tablas y conteo de columnas
    cur.execute("""
        SELECT t.table_name, 
               count(c.column_name) as col_count
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c 
            ON t.table_name = c.table_name AND t.table_schema = c.table_schema
        WHERE t.table_schema = %s AND t.table_type = 'BASE TABLE'
        GROUP BY t.table_name
        ORDER BY t.table_name;
    """, (schema,))
    tables = cur.fetchall()
    
    # Foreign Keys intra-esquema
    cur.execute("""
        SELECT 
            tc.table_name,
            kcu.column_name,
            ccu.table_schema as ref_schema,
            ccu.table_name as ref_table,
            ccu.column_name as ref_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_schema = %s 
            AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name;
    """, (schema,))
    fks = cur.fetchall()
    
    # Primary Keys
    cur.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %s AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY tc.table_name;
    """, (schema,))
    pks = {}
    for row in cur.fetchall():
        pks.setdefault(row[0], []).append(row[1])
    
    return tables, fks, pks

def get_waste_chemical_details(cur):
    """Obtener tablas y relaciones relevantes para Registro Generador de Desechos
    y Registro de Sustancias Químicas."""
    
    # Tablas coa_waste_generator_record
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'coa_waste_generator_record' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    waste_tables = [r[0] for r in cur.fetchall()]
    
    # Tablas chemical_pesticides
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'chemical_pesticides' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    chem_tables = [r[0] for r in cur.fetchall()]
    
    # Columnas detalladas de coa_waste_generator_record
    waste_cols = {}
    for t in waste_tables:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'coa_waste_generator_record' AND table_name = %s
            ORDER BY ordinal_position;
        """, (t,))
        waste_cols[t] = cur.fetchall()
    
    # Columnas detalladas de chemical_pesticides
    chem_cols = {}
    for t in chem_tables:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'chemical_pesticides' AND table_name = %s
            ORDER BY ordinal_position;
        """, (t,))
        chem_cols[t] = cur.fetchall()
    
    # FK entre waste y chemical_pesticides
    cur.execute("""
        SELECT 
            tc.table_schema as src_schema,
            tc.table_name as src_table,
            kcu.column_name as src_col,
            ccu.table_schema as ref_schema,
            ccu.table_name as ref_table,
            ccu.column_name as ref_col
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND (
                (tc.table_schema = 'coa_waste_generator_record' AND ccu.table_schema = 'chemical_pesticides')
                OR (tc.table_schema = 'chemical_pesticides' AND ccu.table_schema = 'coa_waste_generator_record')
                OR (tc.table_schema = 'coa_waste_generator_record' AND ccu.table_schema = 'coa_waste_generator_record')
                OR (tc.table_schema = 'chemical_pesticides' AND ccu.table_schema = 'chemical_pesticides')
                OR (tc.table_schema = 'coa_waste_generator_record' AND ccu.table_schema IN ('suia_iii', 'coa_mae', 'public'))
                OR (tc.table_schema = 'chemical_pesticides' AND ccu.table_schema IN ('suia_iii', 'coa_mae', 'public'))
            )
        ORDER BY tc.table_schema, tc.table_name;
    """)
    cross_fks = cur.fetchall()
    
    return waste_tables, chem_tables, waste_cols, chem_cols, cross_fks

def generate_mermaid_schema(schema_name, tables, fks, pks, max_tables=50):
    """Generar código Mermaid para un esquema."""
    lines = ["erDiagram"]
    
    # Limitar tablas si hay demasiadas
    table_names = [t[0] for t in tables[:max_tables]]
    
    # Entidades
    for tname, col_count in tables[:max_tables]:
        pk_list = pks.get(tname, [])
        pk_str = ", ".join(pk_list) if pk_list else "N/A"
        safe_name = tname.replace("-", "_").replace(" ", "_")
        lines.append(f'    {safe_name} {{')
        lines.append(f'        string PK "{pk_str}"')
        lines.append(f'        int columns "{col_count}"')
        lines.append(f'    }}')
    
    # Relaciones (FK)
    seen_rels = set()
    for fk in fks:
        src_table, src_col, ref_schema, ref_table, ref_col = fk
        if src_table not in table_names:
            continue
        if ref_schema != schema_name and ref_table not in table_names:
            continue
        
        safe_src = src_table.replace("-", "_").replace(" ", "_")
        safe_ref = ref_table.replace("-", "_").replace(" ", "_")
        
        rel_key = f"{safe_src}_{safe_ref}"
        if rel_key not in seen_rels:
            seen_rels.add(rel_key)
            lines.append(f'    {safe_ref} ||--o{{ {safe_src} : "{src_col}"')
    
    return "\n".join(lines)

def main():
    conn = psycopg2.connect(**CONN_PARAMS)
    cur = conn.cursor()
    print("Conectado exitosamente a suia_enlisy")
    
    all_data = {}
    
    for schema in SCHEMAS:
        print(f"\nProcesando esquema: {schema}")
        tables, fks, pks = get_schema_summary(cur, schema)
        all_data[schema] = {"tables": tables, "fks": fks, "pks": pks}
        
        mermaid = generate_mermaid_schema(schema, tables, fks, pks)
        
        mermaid_file = os.path.join(OUTPUT_DIR, f"er_{schema}.mmd")
        with open(mermaid_file, "w", encoding="utf-8") as f:
            f.write(mermaid)
        print(f"  Mermaid guardado: {mermaid_file}")
        print(f"  Tablas: {len(tables)}, FK: {len(fks)}")
    
    # Análisis específico waste <-> chemical_pesticides
    print("\n" + "="*70)
    print("ANALISIS: coa_waste_generator_record <-> chemical_pesticides")
    print("="*70)
    
    waste_tables, chem_tables, waste_cols, chem_cols, cross_fks = get_waste_chemical_details(cur)

    print(f"\ncoa_waste_generator_record: {len(waste_tables)} tablas")
    for t in waste_tables:
        print(f"  - {t} ({len(waste_cols[t])} cols)")
    
    print(f"\nchemical_pesticides: {len(chem_tables)} tablas")
    for t in chem_tables:
        print(f"  - {t} ({len(chem_cols[t])} cols)")
    
    print(f"\nRelaciones FK encontradas: {len(cross_fks)}")
    for fk in cross_fks:
        print(f"  {fk[0]}.{fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}.{fk[5]}")
    
    # Guardar análisis detallado
    analysis = {
        "coa_waste_generator_record": {
            "tables": waste_tables,
            "columns": {t: [(c[0], c[1], c[2]) for c in cols] for t, cols in waste_cols.items()},
        },
        "chemical_pesticides": {
            "tables": chem_tables,
            "columns": {t: [(c[0], c[1], c[2]) for c in cols] for t, cols in chem_cols.items()},
        },
        "cross_schema_fks": [
            {"src": f"{fk[0]}.{fk[1]}.{fk[2]}", "ref": f"{fk[3]}.{fk[4]}.{fk[5]}"}
            for fk in cross_fks
        ]
    }
    
    with open(os.path.join(OUTPUT_DIR, "analisis_waste_chemical.json"), "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
    
    cur.close()
    conn.close()
    print("\nAnálisis completo guardado.")

if __name__ == "__main__":
    main()
