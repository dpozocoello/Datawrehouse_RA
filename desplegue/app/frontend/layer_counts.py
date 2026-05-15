from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        q = text("""
            SELECT c.nombre_capa, COUNT(b.sk_proyecto) as total
            FROM dw.dim_capa_ambiental c
            LEFT JOIN dw.bridge_interseccion_ambiental b ON c.sk_capa = b.sk_capa
            GROUP BY 1 ORDER BY 2 DESC
        """)
        df = pd.read_sql(q, conn)
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
