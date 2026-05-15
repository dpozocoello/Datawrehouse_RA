import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def get_full_cols():
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'dim_proyecto' ORDER BY ordinal_position")
        cols = [row[0] for row in cur.fetchall()]
        print("\n".join(cols))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_full_cols()
