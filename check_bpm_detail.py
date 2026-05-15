import pandas as pd
import psycopg2

BPMS_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_bpms_enlisy_app", "user":"postgres", "password":"postgres"}

def check_bpm_detail():
    code = 'MAAE-RA-2020-363959'
    try:
        conn = psycopg2.connect(**BPMS_PARAMS)
        cur = conn.cursor()
        print(f"--- Buscando BPM SNAP para {code} ---")
        cur.execute("""
            SELECT v.variableid, v.value, b.status
            FROM variableinstancelog v
            JOIN bamtasksummary b ON v.processinstanceid = b.processinstanceid
            WHERE v.value = %s AND v.variableid ILIKE '%%snap%%'
        """, (code,))
        res = cur.fetchall()
        print(f"BPM Status: {res}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_bpm_detail()
