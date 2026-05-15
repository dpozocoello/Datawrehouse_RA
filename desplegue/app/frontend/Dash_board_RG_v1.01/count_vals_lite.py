from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def count_intersections():
    engine = get_engine()
    with engine.connect() as conn:
        print("OCCURRENCES OF interseccion_snap (Top 20):")
        query = text("""
        SELECT interseccion_snap, COUNT(*) as qty 
        FROM dw.fact_regularizacion 
        GROUP BY interseccion_snap 
        ORDER BY qty DESC
        LIMIT 20
        """)
        res = conn.execute(query)
        for row in res:
            val = str(row[0])[:50] + "..." if row[0] and len(str(row[0])) > 50 else row[0]
            print(f"{val} | {row[1]}")
        
        print("\nChecking for any record with 'C':")
        res = conn.execute(text("SELECT COUNT(*) FROM dw.fact_regularizacion WHERE interseccion_snap = 'C'"))
        print(f"Count of 'C': {res.scalar()}")

if __name__ == "__main__":
    count_intersections()
