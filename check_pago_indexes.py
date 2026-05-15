import psycopg2
from psycopg2.extras import RealDictCursor

def get_pago_indexes():
    conn = psycopg2.connect("host=localhost dbname=dw_reg_v1 user=postgres password=postgres port=5432")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT
        t.relname as table_name,
        i.relname as index_name,
        a.attname as column_name
    FROM
        pg_class t,
        pg_class i,
        pg_index ix,
        pg_attribute a
    WHERE
        t.oid = ix.indrelid
        AND i.oid = ix.indexrelid
        AND a.attrelid = t.oid
        AND a.attnum = ANY(ix.indkey)
        AND t.relkind = 'r'
        AND t.relname = 'fact_pago'
    ORDER BY
        t.relname,
        i.relname;
    """
    
    cur.execute(query)
    results = cur.fetchall()
    
    print(f"{'TABLE':<20} | {'INDEX':<30} | {'COLUMN'}")
    print("-" * 65)
    for row in results:
        print(f"{row['table_name']:<20} | {row['index_name']:<30} | {row['column_name']}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    get_pago_indexes()
