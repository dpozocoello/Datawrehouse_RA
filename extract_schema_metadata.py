"""
Script para extraer metadatos de esquemas de la base de datos suia_enlisy
y generar diagramas ER en formato Mermaid.
Esquemas objetivo: suia_iii, coa_mae, coa_waste_generator_record, chemical_pesticides
"""
import sys
import os
import json

# Usar psycopg2 directamente
import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

SCHEMAS = ["suia_iii", "coa_mae", "coa_waste_generator_record", "chemical_pesticides"]

def get_tables(cur, schema):
    """Obtener todas las tablas de un esquema."""
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """, (schema,))
    return [r[0] for r in cur.fetchall()]

def get_columns(cur, schema, table):
    """Obtener columnas de una tabla."""
    cur.execute("""
        SELECT column_name, data_type, is_nullable, 
               character_maximum_length, column_default
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
    """, (schema, table))
    return cur.fetchall()

def get_primary_keys(cur, schema, table):
    """Obtener claves primarias."""
    cur.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %s 
            AND tc.table_name = %s
            AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position;
    """, (schema, table))
    return [r[0] for r in cur.fetchall()]

def get_foreign_keys(cur, schema):
    """Obtener todas las foreign keys de un esquema."""
    cur.execute("""
        SELECT 
            tc.table_name as source_table,
            kcu.column_name as source_column,
            ccu.table_schema as target_schema,
            ccu.table_name as target_table,
            ccu.column_name as target_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.table_schema = %s 
            AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, kcu.ordinal_position;
    """, (schema,))
    return cur.fetchall()

def get_cross_schema_fks(cur, schemas):
    """Obtener FK que cruzan entre esquemas."""
    cur.execute("""
        SELECT 
            tc.table_schema as source_schema,
            tc.table_name as source_table,
            kcu.column_name as source_column,
            ccu.table_schema as target_schema,
            ccu.table_name as target_table,
            ccu.column_name as target_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND (tc.table_schema = ANY(%s) OR ccu.table_schema = ANY(%s))
        ORDER BY tc.table_schema, tc.table_name;
    """, (schemas, schemas))
    return cur.fetchall()

def main():
    output = {}
    
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        cur = conn.cursor()
        print("Conectado a suia_enlisy en 172.16.0.179:5632")
        
        for schema in SCHEMAS:
            print(f"\n{'='*60}")
            print(f"ESQUEMA: {schema}")
            print(f"{'='*60}")
            
            tables = get_tables(cur, schema)
            print(f"  Tablas encontradas: {len(tables)}")
            
            schema_data = {"tables": {}, "foreign_keys": []}
            
            for table in tables:
                cols = get_columns(cur, schema, table)
                pks = get_primary_keys(cur, schema, table)
                
                schema_data["tables"][table] = {
                    "columns": [
                        {
                            "name": c[0],
                            "type": c[1],
                            "nullable": c[2],
                            "max_length": c[3],
                            "default": str(c[4]) if c[4] else None
                        }
                        for c in cols
                    ],
                    "primary_keys": pks
                }
                print(f"  - {table}: {len(cols)} columnas, PK: {pks}")
            
            fks = get_foreign_keys(cur, schema)
            schema_data["foreign_keys"] = [
                {
                    "source_table": fk[0],
                    "source_column": fk[1],
                    "target_schema": fk[2],
                    "target_table": fk[3],
                    "target_column": fk[4],
                    "constraint_name": fk[5]
                }
                for fk in fks
            ]
            print(f"  Foreign Keys: {len(fks)}")
            
            output[schema] = schema_data
        
        # Cross-schema FKs
        print(f"\n{'='*60}")
        print("FOREIGN KEYS CROSS-SCHEMA")
        print(f"{'='*60}")
        
        cross_fks = get_cross_schema_fks(cur, SCHEMAS)
        output["cross_schema_fks"] = [
            {
                "source_schema": fk[0],
                "source_table": fk[1],
                "source_column": fk[2],
                "target_schema": fk[3],
                "target_table": fk[4],
                "target_column": fk[5],
                "constraint_name": fk[6]
            }
            for fk in cross_fks
        ]
        print(f"  Cross-schema FKs encontradas: {len(cross_fks)}")
        for fk in cross_fks:
            print(f"    {fk[0]}.{fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}.{fk[5]}")
        
        cur.close()
        conn.close()
        
        # Guardar JSON
        with open("f:\\Datawrehouse_RA\\schema_metadata.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\nMetadatos guardados en schema_metadata.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
