from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        q = text("""
            SELECT p.codigo_proyecto, c.nombre_capa, b.detalle_interseccion, b.sk_capa
            FROM dw.dim_proyecto p
            LEFT JOIN dw.bridge_interseccion_ambiental b ON p.sk_proyecto = b.sk_proyecto
            LEFT JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE p.codigo_proyecto = 'MAAE-RA-2020-363959'
        """)
        df = pd.read_sql(q, conn)
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
