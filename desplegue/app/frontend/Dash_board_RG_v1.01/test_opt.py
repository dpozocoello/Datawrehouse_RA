import pandas as pd
import time
from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def test_optimized_query(limit=None):
    engine = get_engine()
    limit_clause = f"LIMIT {limit}" if limit else ""

    query = text(f"""
    WITH LatestFact AS (
        SELECT DISTINCT ON (sk_proyecto) 
            sk_proyecto, sk_geografia, sk_proponente, sk_area, interseccion_snap
        FROM dw.fact_regularizacion 
        ORDER BY sk_proyecto, fecha_inicio_proceso DESC
    ),
    AggregatedLayers AS (
        SELECT b.sk_proyecto, string_agg(DISTINCT c.nombre_capa, ', ') as nombre_capa_agg
        FROM dw.bridge_interseccion_ambiental b
        JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
        WHERE b.sk_capa != 0
        GROUP BY b.sk_proyecto
    ),
    BaseProyectos AS (
        SELECT 
            p.codigo_proyecto,
            p.nombre_proyecto,
            p.tipo_permiso_ambiental,
            p.sistema,
            COALESCE(geo.provincia, 'N/A') as provincia,
            COALESCE(geo.canton, 'N/A') as canton,
            COALESCE(geo.parroquia, 'N/A') as parroquia,
            COALESCE(da.nombre_area, 'N/A') as oficina_tecnica,
            COALESCE(prop.nombre_proponente, 'N/A') as proponente,
            CASE 
                WHEN (lf.interseccion_snap NOT IN ('NO', 'N/A', '') AND lf.interseccion_snap IS NOT NULL)
                OR al.nombre_capa_agg IS NOT NULL
                THEN 'Interseca'
                ELSE 'No Interseca'
            END as estado_interseccion,
            COALESCE(
                al.nombre_capa_agg,
                CASE 
                    WHEN lf.interseccion_snap NOT IN ('NO', 'N/A', '') AND lf.interseccion_snap IS NOT NULL THEN REPLACE(lf.interseccion_snap, '<br/>', ' ') 
                    ELSE 'SIN CAPAS ESPECÍFICAS'
                END
            ) as nombre_capa
        FROM dw.dim_proyecto p
        JOIN LatestFact lf ON p.sk_proyecto = lf.sk_proyecto
        LEFT JOIN AggregatedLayers al ON p.sk_proyecto = al.sk_proyecto
        LEFT JOIN dw.dim_geografia geo ON lf.sk_geografia = geo.sk_geografia
        LEFT JOIN dw.dim_area da ON lf.sk_area = da.sk_area
        LEFT JOIN dw.dim_proponente prop ON lf.sk_proponente = prop.sk_proponente
        WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
    )
    SELECT * FROM BaseProyectos
    ORDER BY codigo_proyecto
    {limit_clause}
    """)
    
    start = time.time()
    try:
        df = pd.read_sql(query, engine)
        end = time.time()
        print(f"\n--- Optimized query execution time: {end - start:.2f}s ---")
        print(f"Rows returned: {len(df)}")
        if not df.empty:
            print(df[['codigo_proyecto', 'estado_interseccion', 'nombre_capa']].head().to_string())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_optimized_query(limit=5000)
