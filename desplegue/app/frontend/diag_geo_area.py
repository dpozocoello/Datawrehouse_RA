import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def dump_info():
    print("--- VIEW DEFINITION: dw.v_dashboard_regularizacion ---")
    q_view = "SELECT view_definition FROM information_schema.views WHERE table_schema = 'dw' AND table_name = 'v_dashboard_regularizacion'"
    with engine.connect() as conn:
        res = conn.execute(text(q_view)).fetchone()
        if res:
            print(res[0])
        else:
            print("View not found!")

    print("\n--- SAMPLE: dw.dim_area ---")
    df_area = pd.read_sql("SELECT * FROM dw.dim_area LIMIT 10", engine)
    print(df_area.to_string())

    print("\n--- SAMPLE: dw.dim_geografia ---")
    df_geo = pd.read_sql("SELECT * FROM dw.dim_geografia LIMIT 10", engine)
    print(df_geo.to_string())

    print("\n--- CHECK: Zonas in dim_area ---")
    df_zonas = pd.read_sql("SELECT DISTINCT nombre_area, zona_administrativa FROM dw.dim_area", engine)
    print(df_zonas.to_string())

if __name__ == "__main__":
    dump_info()
