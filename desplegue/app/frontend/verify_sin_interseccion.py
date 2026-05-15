from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        q = text("SELECT sk_capa, nombre_capa FROM dw.dim_capa_ambiental WHERE nombre_capa ILIKE '%SIN INTERSECCION%'")
        df = pd.read_sql(q, conn)
        print("Layer Match:")
        print(df)
        
        if not df.empty:
            sk = df.iloc[0]['sk_capa']
            q2 = text(f"SELECT COUNT(*) FROM dw.bridge_interseccion_ambiental WHERE sk_capa = {sk}")
            count = conn.execute(q2).scalar()
            print(f"\nProjects with this layer: {count}")
            
            q3 = text(f"SELECT detalle_interseccion FROM dw.bridge_interseccion_ambiental WHERE sk_capa = {sk} LIMIT 5")
            details = conn.execute(q3).fetchall()
            print("\nSample details for this layer:")
            for d in details:
                print(d[0])

except Exception as e:
    print(f"Error: {e}")
