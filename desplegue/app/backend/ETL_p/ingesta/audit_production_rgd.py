import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_SUIA_ENLISY

def audit_production():
    try:
        conn = psycopg2.connect(
            host=CONN_SUIA_ENLISY['host'],
            port=CONN_SUIA_ENLISY['port'],
            database=CONN_SUIA_ENLISY['database'],
            user=CONN_SUIA_ENLISY['user'],
            password=CONN_SUIA_ENLISY['password']
        )
        cur = conn.cursor()
        
        # 1. Validar COA (Legado)
        print("### AUDIT COA (suia_iii) ###")
        cur.execute("SELECT count(*) FROM suia_iii.hazardous_wastes_generators")
        print(f"Total Generators in suia_iii: {cur.fetchone()[0]}")
        
        # Validar relación COA Proyectos
        cur.execute("""
            SELECT count(*) 
            FROM suia_iii.hazardous_wastes_generators hwg
            JOIN suia_iii.projects_environmental_licensing pel ON hwg.pren_id = pel.pren_id
        """)
        print(f"Generators with Project link in suia_iii: {cur.fetchone()[0]}")
        
        # 2. Validar RCOA (Nuevo)
        print("\n### AUDIT RCOA (coa_waste_generator_record) ###")
        cur.execute("SELECT count(*) FROM coa_waste_generator_record.waste_generator_record_coa")
        print(f"Total Generators in RCOA: {cur.fetchone()[0]}")
        
        # Validar relación RCOA Proyectos
        cur.execute("""
            SELECT count(*) 
            FROM coa_waste_generator_record.waste_generator_record_coa wgr
            JOIN coa_waste_generator_record.waste_generator_record_project_licencing_coa link ON wgr.ware_id = link.ware_id
            JOIN coa_mae.project_licencing_coa plc ON link.prco_id = plc.prco_id
        """)
        print(f"Generators with Project link in RCOA: {cur.fetchone()[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    audit_production()
