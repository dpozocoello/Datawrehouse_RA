import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def check_intersections():
    print("Connecting to DB...")
    engine = get_engine()
    with engine.connect() as conn:
        print("Checking distinct values for interseccion_snap in dw.fact_regularizacion:")
        res = conn.execute(text("SELECT DISTINCT interseccion_snap FROM dw.fact_regularizacion"))
        for row in res:
            print(f" - '{row[0]}'")
        
        print("\nChecking sample projects in Pichincha and their intersection status:")
        query = text("""
        SELECT p.codigo_proyecto, geo.provincia, f.interseccion_snap,
               EXISTS (SELECT 1 FROM dw.bridge_interseccion_ambiental b WHERE b.sk_proyecto = p.sk_proyecto) as bridge_exists
        FROM dw.dim_proyecto p
        JOIN dw.fact_regularizacion f ON p.sk_proyecto = f.sk_proyecto
        JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        WHERE geo.provincia ILIKE 'PICHINCHA'
        LIMIT 10
        """)
        df = pd.read_sql(query, engine)
        print(df)

if __name__ == "__main__":
    check_intersections()
