import psycopg2
import sys

# Set output encoding to avoid issues in Windows Terminal
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def verify_implementation():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Datawarehouse_RA",
            user="postgres",
            password="postgres",
            port=5432
        )
        cur = conn.cursor()
        
        print("--- Verificación de Tablas Nuevas ---")
        tables = ['dim_capa_ambiental', 'bridge_interseccion_ambiental']
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'dw' AND table_name = '{table}'")
            exists = cur.fetchone()[0]
            print(f"Table dw.{table}: {'EXISTS' if exists else 'MISSING'}")

        print("\n--- Verificación de Datos en dim_capa_ambiental ---")
        cur.execute("SELECT sk_capa, nombre_capa FROM dw.dim_capa_ambiental ORDER BY sk_capa")
        rows = cur.fetchall()
        for row in rows:
            print(f"SK: {row[0]} | Name: {row[1]}")

        print("\n--- Verificación de Procedimientos Almacenados ---")
        functions = ['sp_carga_puente_ambiental']
        for func in functions:
            cur.execute(f"SELECT COUNT(*) FROM pg_proc JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid WHERE nspname = 'dw' AND proname = '{func}'")
            exists = cur.fetchone()[0]
            print(f"Function dw.{func}: {'EXISTS' if exists else 'MISSING'}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_implementation()
