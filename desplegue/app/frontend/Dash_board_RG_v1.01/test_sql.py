import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def test_query(cp):
    engine = get_engine()
    query = text(f"""
    WITH LatestFact AS (
        SELECT DISTINCT ON (sk_proyecto) 
            sk_proyecto, sk_geografia, sk_proponente, sk_area, interseccion_snap
        FROM dw.fact_regularizacion 
        ORDER BY sk_proyecto, fecha_inicio_proceso DESC
    ),
    BaseProyectos AS (
        SELECT 
            p.codigo_proyecto,
            p.nombre_proyecto,
            CASE 
                WHEN (lf.interseccion_snap NOT IN ('NO', 'N/A', '') AND lf.interseccion_snap IS NOT NULL)
                OR EXISTS (SELECT 1 FROM dw.bridge_interseccion_ambiental b WHERE b.sk_proyecto = p.sk_proyecto AND b.sk_capa != 0) 
                THEN 'Interseca'
                ELSE 'No Interseca'
            END as estado_interseccion,
            COALESCE(
                (
                    SELECT string_agg(DISTINCT c.nombre_capa, ', ')
                    FROM dw.bridge_interseccion_ambiental b
                    JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
                    WHERE b.sk_proyecto = p.sk_proyecto AND c.sk_capa != 0
                ),
                CASE 
                    WHEN lf.interseccion_snap NOT IN ('NO', 'N/A', '') AND lf.interseccion_snap IS NOT NULL THEN REPLACE(lf.interseccion_snap, '<br/>', ' ') 
                    ELSE 'SIN CAPAS ESPECÍFICAS'
                END
            ) as capas_ambientales
        FROM dw.dim_proyecto p
        JOIN LatestFact lf ON p.sk_proyecto = lf.sk_proyecto
        WHERE p.codigo_proyecto = :cp
    )
    SELECT * FROM BaseProyectos
    """)
    df = pd.read_sql(query, engine, params={"cp": cp})
    print(df.to_string())

if __name__ == "__main__":
    test_query("MAAE-RA-2020-368524")
    test_query("MAATE-RA-2023-473741") # A known intersecting one
