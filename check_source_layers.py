import psycopg2

def check_layers_detailed():
    try:
        conn = psycopg2.connect(
            host="172.16.0.179",
            database="suia_enlisy",
            user="postgres",
            password="postgres",
            port=5632
        )
        cur = conn.cursor()
        
        # Determine table name for layers
        print("Finding layers tables...")
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name ILIKE '%layer%'
        """)
        for s, t in cur.fetchall():
            print(f"Schema: {s} | Table: {t}")

        # Check suia_iii.layers if it exists
        print("\n--- Catálogo de Capas (Layers suia_iii) ---")
        cur.execute("SELECT laye_id, laye_name FROM suia_iii.layers ORDER BY laye_id")
        for row in cur.fetchall():
            print(f"{row[0]}: {row[1]}")

        # Search for 'Patrimonio' and 'Intangible' specifically
        print("\n--- Búsqueda de Capas Específicas ---")
        cur.execute("""
            SELECT laye_id, laye_name 
            FROM suia_iii.layers 
            WHERE laye_name ILIKE '%patrimonio%' 
               OR laye_name ILIKE '%intangible%'
               OR laye_name ILIKE '%snap%'
               OR laye_name ILIKE '%area%proteg%'
        """)
        for row in cur.fetchall():
            print(f"ID: {row[0]} | Name: {row[1]}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_layers_detailed()
