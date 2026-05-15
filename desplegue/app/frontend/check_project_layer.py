from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        q = text("""
            SELECT b.sk_proyecto, p.codigo_proyecto, c.nombre_capa, b.detalle_interseccion
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_proyecto p ON b.sk_proyecto = p.sk_proyecto
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE p.codigo_proyecto = 'MAATE-RA-2022-363959'
        """)
        df = pd.read_sql(q, conn)
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
