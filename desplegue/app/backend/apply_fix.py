import psycopg2
import os

def apply_sql_fix():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres"
    }
    
    sql_file = r"f:\Datawrehouse_RA\fix_hanging_sp.sql"
    
    try:
        if not os.path.exists(sql_file):
            print(f"Error: No se encuentra el archivo {sql_file}")
            return

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Aplicando fix (Creando índice y actualizando SP)...")
        cur.execute(sql)
        print("Fix aplicado exitosamente.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    apply_sql_fix()
