import psycopg2
import os

def list_schemas_to_file():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Datawarehouse_RA",
            user="postgres",
            password="postgres",
            port=5432
        )
        cur = conn.cursor()
        cur.execute("SELECT nspname FROM pg_catalog.pg_namespace")
        with open('schemas_output.txt', 'w') as f:
            for row in cur.fetchall():
                f.write(f"{row[0]}\n")
        cur.close()
        conn.close()
        print("Done writing schemas to output.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_schemas_to_file()
