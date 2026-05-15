import pandas as pd
import psycopg2

# Conexiones
SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}
DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def diagnose_sample():
    try:
        codes = ['MAAE-RA-2020-363831', 'MAAE-RA-2020-363959']
        print(f"--- Diagnosticando Proyectos: {codes} ---")
        
        # 1. Registro en Producción
        conn_suia = psycopg2.connect(**SUIA_PARAMS)
        cur = conn_suia.cursor()
        for code in codes:
            print(f"\n[PROYECTO: {code} en 179]")
            # Ver capas en coa_mae
            cur.execute("""
                SELECT iplc.laye_id, lc.laye_name, iplc.inpr_status
                FROM coa_mae.intersections_project_licencing_coa iplc
                JOIN coa_mae.project_licencing_coa plc ON iplc.prco_id = plc.prco_id
                JOIN coa_mae.layers_coa lc ON iplc.laye_id = lc.laye_id
                WHERE plc.prco_cua = %s
            """, (code,))
            res_layers = cur.fetchall()
            print(f"Capas en COA: {res_layers}")
            
            # Ver certificados
            cur.execute("""
                SELECT cein_code, cein_status, cein_creation_date 
                FROM coa_mae.certificate_intersection_coa cic
                JOIN coa_mae.project_licencing_coa plc ON cic.prco_id = plc.prco_id
                WHERE plc.prco_cua = %s
            """, (code,))
            res_certs = cur.fetchall()
            print(f"Certificados: {res_certs}")
            
        conn_suia.close()
        
        # 2. Registro en DWH
        conn_dwh = psycopg2.connect(**DWH_PARAMS)
        cur_dwh = conn_dwh.cursor()
        for code in codes:
            print(f"\n[PROYECTO: {code} en LOCAL]")
            cur_dwh.execute("""
                SELECT di.dictamen_final, di.certificate_code, di.is_current
                FROM dw.dim_intersection di
                JOIN dw.dim_proyecto dp ON di.sk_proyecto = dp.sk_proyecto
                WHERE dp.codigo_proyecto = %s
            """, (code,))
            res_dwh = cur_dwh.fetchall()
            print(f"DWH Info: {res_dwh}")
        conn_dwh.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_sample()
