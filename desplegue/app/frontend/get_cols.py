import psycopg2

try:
    # Use standard postgresql credentials found in sqlalchemy string previously (postgres:postgres@localhost:5432/ECO_SIEAA)
    conn = psycopg2.connect(dbname="ECO_SIEAA", user="postgres", password="password", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'dim_pago';")
    print("dim_pago cols:", [r[0] for r in cur.fetchall()])
    
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'fact_pago';")
    print("fact_pago cols:", [r[0] for r in cur.fetchall()])
    conn.close()
except psycopg2.OperationalError:
    try:
        conn = psycopg2.connect(dbname="ECO_SIEAA", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'dim_pago';")
        print("dim_pago cols:", [r[0] for r in cur.fetchall()])
        
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'fact_pago';")
        print("fact_pago cols:", [r[0] for r in cur.fetchall()])
        conn.close()
    except Exception as e2:
        print("Fallback DB Error:", e2)
except Exception as e:
    print("DB Error:", e)
