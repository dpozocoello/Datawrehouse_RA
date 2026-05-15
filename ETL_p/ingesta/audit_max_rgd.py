import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def audit_max_values():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        print("Auditing absolute MAX values in stg.stg_fact_waste_generation...")
        cur.execute("""
            SELECT 
                MAX(quantity_generated), 
                MAX(quantity_delivered), 
                MAX(quantity_stored) 
            FROM stg.stg_fact_waste_generation
        """)
        m_gen, m_del, m_sto = cur.fetchone()
        print(f"MAX Generated: {m_gen}")
        print(f"MAX Delivered: {m_del}")
        print(f"MAX Stored:    {m_sto}")
        
        # Check if any exceed 10^12
        limit = 10**12
        if any(v is not None and v >= limit for v in [m_gen, m_del, m_sto]):
            print("\nCONCLUSION: OVERFLOW CONFIRMED. Values exceed 10^12 limit for NUMERIC(15,3).")
        else:
            print("\nCONCLUSION: Values appear to be within limits. Check for NaN or Inf.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_max_values()
