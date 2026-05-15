import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY

def audit_snap_layers():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        # 1. Look for SNAP layers
        print("Searching for SNAP-related layers in coa_mae.layers...")
        cur.execute("""
            SELECT laye_id, laye_name
            FROM coa_mae.layers 
            WHERE laye_name LIKE '%%SNAP%%' OR laye_name LIKE '%%Protegida%%'
        """)
        layers = cur.fetchall()
        for l in layers:
            print(f"Layer ID: {l[0]} | Name: {l[1]}")
        
        snap_ids = [l[0] for l in layers]
        
        # 2. Check intersection for Project 542234
        target_id = 542234
        print(f"/nChecking intersections for Project {target_id} in coa_mae.intersections_project_licencing_coa...")
        cur.execute("""
            SELECT laye_id, inpr_layer_description 
            FROM coa_mae.intersections_project_licencing_coa 
            WHERE prco_id = %s
        """, (target_id,))
        intersections = cur.fetchall()
        
        found_snap = False
        print("Intersections Found:")
        for intersect in intersections:
            is_snap = intersect[0] in snap_ids
            suffix = "[!] SNAP LAYER" if is_snap else ""
            print(f"  - Layer ID: {intersect[0]} | Desc: {intersect[1]} {suffix}")
            if is_snap: found_snap = True
            
        if not found_snap:
            print("/nCONCLUSION: NO SNAP intersection detected in raw data for this project.")
            print("The text 'NO INTERSECA con el Sistema Nacional de Áreas Protegidas (SNAP)' is likely a business logic output.")
        else:
            print("/nCONCLUSION: SNAP intersection DETECTED.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_snap_layers()
