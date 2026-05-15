import psycopg2

def kill_hanging_session(pid):
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        print(f"Intentando terminar sesión con PID: {pid}...")
        cur.execute(f"SELECT pg_terminate_backend({pid});")
        result = cur.fetchone()[0]
        if result:
            print(f"Sesión {pid} terminada exitosamente.")
        else:
            print(f"No se pudo terminar la sesión {pid} o ya no existe.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # PID detectado en el paso anterior: 23252
    kill_hanging_session(23252)
