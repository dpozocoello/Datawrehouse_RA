import psycopg2

def extract_schema():
    try:
        conn = psycopg2.connect(dbname="dwh_bi", user="postgres", password="postgres", host="localhost")
        conn.set_client_encoding('SQL_ASCII')
        cur = conn.cursor()
        
        tables = [
            'fact_regularizacion', 'dim_proyecto', 'bridge_interseccion_ambiental', 
            'dim_capa_ambiental', 'dim_geografia', 'dim_area', 'dim_proponente'
        ]
        
        with open('superposicion_schema_raw.txt', 'w', encoding='utf-8') as f:
            for t in tables:
                f.write(f"\n{'='*50}\n TABLA: dw.{t}\n{'='*50}\n")
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_schema = 'dw' AND table_name = '{t}' 
                    ORDER BY ordinal_position
                """)
                rows = cur.fetchall()
                f.write(f"{'COLUMN_NAME':<30} | {'DATA_TYPE':<20} | {'NULL?'}\n")
                f.write("-" * 65 + "\n")
                for r in rows:
                    f.write(f"{str(r[0]):<30} | {str(r[1]):<20} | {str(r[2])}\n")
                    
        print("Schema extraído con éxito en superposicion_schema_raw.txt")
        
    except Exception as e:
        with open('superposicion_schema_error.txt', 'w', encoding='utf-8') as f:
            f.write(str(e))
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    extract_schema()
