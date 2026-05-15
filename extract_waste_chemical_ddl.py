import psycopg2
import json

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres"
}

SCHEMAS = [
    'waste_dangerous',
    'coa_chemical_sustances',
    'coa_waste_generator_record',
    'chemical_pesticides'
]

def extract_schema_metadata():
    metadata = {}
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        cur = conn.cursor()

        for schema in SCHEMAS:
            metadata[schema] = {}
            
            # Get tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """, (schema,))
            tables = [row[0] for row in cur.fetchall()]
            
            for table in tables:
                metadata[schema][table] = {
                    "columns": [],
                    "primary_keys": [],
                    "foreign_keys": []
                }
                
                # Get columns
                cur.execute("""
                    SELECT column_name, data_type, character_maximum_length, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;
                """, (schema, table))
                for col in cur.fetchall():
                    metadata[schema][table]["columns"].append({
                        "name": col[0],
                        "type": col[1],
                        "max_length": col[2],
                        "is_nullable": col[3]
                    })
                
                # Get primary keys
                cur.execute("""
                    SELECT a.attname
                    FROM   pg_index i
                    JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                         AND a.attnum = ANY(i.indkey)
                    WHERE  i.indrelid = %s::regclass
                    AND    i.indisprimary;
                """, (f"{schema}.{table}",))
                metadata[schema][table]["primary_keys"] = [row[0] for row in cur.fetchall()]
                
                # Get foreign keys
                cur.execute("""
                    SELECT
                        kcu.column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                          AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                          AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = %s AND tc.table_name=%s;
                """, (schema, table))
                for fk in cur.fetchall():
                    metadata[schema][table]["foreign_keys"].append({
                        "column": fk[0],
                        "foreign_schema": fk[1],
                        "foreign_table": fk[2],
                        "foreign_column": fk[3]
                    })

        cur.close()
        conn.close()

        with open('f:/Datawrehouse_RA/waste_chemical_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)
        print("Metadata extracted successfully to f:/Datawrehouse_RA/waste_chemical_metadata.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_schema_metadata()
