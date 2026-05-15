import psycopg2
import sys
import os

# Añadir el path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY

def find_table_by_column():
    print(f"Cuscando tablas con la columna 'hwra_id' en {CONN_SUIA_ENLISY['host']}...")
    try:
        conn = psycopg2.connect(
            host=CONN_SUIA_ENLISY['host'],
            port=CONN_SUIA_ENLISY['port'],
            database=CONN_SUIA_ENLISY['database'],
            user=CONN_SUIA_ENLISY['user'],
            password=CONN_SUIA_ENLISY['password']
        )
        cur = conn.cursor()
        
        # Buscar en todas las tablas que tengan una columna similar a hwra_id
        search_sql = """
            SELECT table_schema, table_name, column_name 
            FROM information_schema.columns 
            WHERE column_name ILIKE '%hwra_id%' 
               OR column_name ILIKE '%hwra_year%'
        """
        cur.execute(search_sql)
        results = cur.fetchall()
        
        if not results:
            print("No se encontraron tablas con columnas similares a 'hwra_id'.")
            print("Buscando tablas que contengan 'record' y 'annual' en su nombre...")
            cur.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_name ILIKE '%annual%' AND table_name ILIKE '%record%'
            """)
            results = cur.fetchall()
            
        print("\nResultados encontrados:")
        print("-" * 50)
        for row in results:
            print(f"Schema: {row[0]} | Table: {row[1]} | (Match found)")
        print("-" * 50)
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    find_table_by_column()
