from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def analyze_flags():
    engine = get_engine()
    with engine.connect() as conn:
        print("SAMPLE VALUES FOR interseccion_snap (Non-'NO' and Non-'N/A'):")
        query = text("""
        SELECT interseccion_snap, COUNT(*) as qty 
        FROM dw.fact_regularizacion 
        WHERE interseccion_snap NOT IN ('NO', 'N/A') AND interseccion_snap IS NOT NULL
        GROUP BY interseccion_snap 
        ORDER BY qty DESC
        LIMIT 10
        """)
        res = conn.execute(query)
        for row in res:
            print(f"|{row[0]}| -> {row[1]}")
        
        print("\nChecking for specific negative keywords:")
        query_neg = text("""
        SELECT interseccion_snap, COUNT(*) 
        FROM dw.fact_regularizacion 
        WHERE interseccion_snap ILIKE '%NO INTERSECA%' OR interseccion_snap ILIKE '%SIN INTERSECCION%'
        GROUP BY interseccion_snap
        """)
        res_neg = conn.execute(query_neg)
        for row in res_neg:
            print(f"Negative: |{row[0]}| -> {row[1]}")

if __name__ == "__main__":
    analyze_flags()
