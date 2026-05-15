import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def get_local_columns():
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT * FROM dw.dim_proyecto LIMIT 1")
        colnames = [desc[0] for desc in cur.description]
        print(f"Columns in dw.dim_proyecto: {colnames}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_local_columns()
