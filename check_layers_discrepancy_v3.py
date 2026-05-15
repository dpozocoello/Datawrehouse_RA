import psycopg2

SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}

def check_project_layers():
    code = 'MAAE-RA-2020-363827'
    try:
        conn = psycopg2.connect(**SUIA_PARAMS)
        cur = conn.cursor()
        print(f"--- Capas para {code} ---")
        query = """
            SELECT iplc.laye_id, lc.laye_name
            FROM coa_mae.intersections_project_licencing_coa iplc
            JOIN coa_mae.project_licencing_coa plc ON iplc.prco_id = plc.prco_id
            JOIN coa_mae.layers lc ON iplc.laye_id = lc.laye_id
            WHERE plc.prco_cua = %s AND iplc.inpr_status = TRUE
        """
        cur.execute(query, (code,))
        rows = cur.fetchall()
        for row in rows:
            print(row)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_project_layers()
