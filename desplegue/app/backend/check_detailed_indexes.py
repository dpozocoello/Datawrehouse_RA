import psycopg2

def check_detailed_indexes():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres"
    }
    
    query = """
    SELECT
        t.relname AS table_name,
        i.relname AS index_name,
        pg_get_indexdef(ix.indexrelid) AS index_def
    FROM
        pg_class t
        JOIN pg_index ix ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
    WHERE
        t.relkind = 'r'
        AND t.relname IN ('fact_pago', 'fact_regularizacion', 'dim_proyecto', 'online_payments_bi', 'financial_transaction_bi')
    ORDER BY
        t.relname,
        i.relname;
    """
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        print(f"{'TABLE':25s} | {'INDEX':30s} | {'DEFINITION'}")
        print("-" * 120)
        for row in rows:
            print(f"{row[0]:25s} | {row[1]:30s} | {row[2]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_detailed_indexes()
