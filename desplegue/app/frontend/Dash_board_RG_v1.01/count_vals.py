import pandas as pd
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
        df = pd.read_sql(query, engine)
        print(df.to_string())
        
        print("\nChecking for any record with 'C':")
        res = conn.execute(text("SELECT COUNT(*) FROM dw.fact_regularizacion WHERE interseccion_snap = 'C'"))
        print(f"Count of 'C': {res.scalar()}")

if __name__ == "__main__":
    count_intersections()
