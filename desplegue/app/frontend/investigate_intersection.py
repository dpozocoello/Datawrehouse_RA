from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Layers Catalog ---")
        q_layers = text("SELECT sk_capa, nombre_capa FROM dw.dim_capa_ambiental")
        layers = pd.read_sql(q_layers, conn)
        print(layers)
        
        print("\n--- Intersection counts by Layer ---")
        q_counts = text("""
            SELECT c.nombre_capa, COUNT(b.sk_proyecto) as total_proyectos
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            GROUP BY 1 ORDER BY 2 DESC
        """)
        counts = pd.read_sql(q_counts, conn)
        print(counts)
        
        print("\n--- Sample records with SIN INTERSECCION layer ---")
        q_sample = text("""
            SELECT b.sk_proyecto, c.nombre_capa, b.detalle_interseccion
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE c.nombre_capa LIKE '%SIN INTERSECCION%'
            LIMIT 5
        """)
        sample = pd.read_sql(q_sample, conn)
        print(sample)

except Exception as e:
    print(f"Error: {e}")
