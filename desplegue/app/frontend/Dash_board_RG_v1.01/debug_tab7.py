import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def test_load_environmental_analysis(provincia=None, codigo_proyecto=None):
    engine = get_engine()
    filters = []
    params = {}
    
    if provincia:
        filters.append("geo.provincia = :prov")
        params["prov"] = provincia
    if codigo_proyecto:
        filters.append("p.codigo_proyecto = :cp")
        params["cp"] = codigo_proyecto
        
    where_clause = ""
    if filters:
        where_clause = "AND " + " AND ".join(filters)

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
            p.tipo_permiso_ambiental,
            p.sistema,
            COALESCE(geo.provincia, 'N/A') as provincia,
            COALESCE(geo.canton, 'N/A') as canton,
            COALESCE(geo.parroquia, 'N/A') as parroquia,
            COALESCE(da.nombre_area, 'N/A') as oficina_tecnica,
            COALESCE(prop.nombre_proponente, 'N/A') as proponente,
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
            ) as nombre_capa
        FROM dw.dim_proyecto p
        JOIN LatestFact lf ON p.sk_proyecto = lf.sk_proyecto
        LEFT JOIN dw.dim_geografia geo ON lf.sk_geografia = geo.sk_geografia
        LEFT JOIN dw.dim_area da ON lf.sk_area = da.sk_area
        LEFT JOIN dw.dim_proponente prop ON lf.sk_proponente = prop.sk_proponente
        WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        {where_clause}
    )
    SELECT * FROM BaseProyectos
    ORDER BY codigo_proyecto
    LIMIT 10
    """)
    try:
        df = pd.read_sql(query, engine, params=params)
        print(f"\n--- Testing with provincia={provincia}, codigo={codigo_proyecto} ---")
        print(f"Rows returned: {len(df)}")
        if not df.empty:
            print(df[['codigo_proyecto', 'estado_interseccion', 'nombre_capa', 'provincia']].to_string())
    except Exception as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    # Test 1: Default view (All)
    test_load_environmental_analysis()
    
    # Test 2: Specific Project
    test_load_environmental_analysis(codigo_proyecto="MAAE-RA-2020-368524")
    
    # Test 3: Specific Province
    test_load_environmental_analysis(provincia="PICHINCHA")
