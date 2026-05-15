from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- 1. Proyectos por Capa (Top 10) ---")
        q1 = text("""
            SELECT c.nombre_capa, COUNT(DISTINCT b.sk_proyecto) as total_proyectos
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE c.nombre_capa NOT ILIKE :no_inter
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """)
        print(pd.read_sql(q1, conn, params={"no_inter": "%SIN INTERSECCIÓN%"}))
        
        print("\n--- 2. Intersecciones por Tipo de Permiso ---")
        q2 = text("""
            SELECT p.tipo_permiso_ambiental, COUNT(*) as total_intersecciones
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_proyecto p ON b.sk_proyecto = p.sk_proyecto
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE c.nombre_capa NOT ILIKE :no_inter
            AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            GROUP BY 1 ORDER BY 2 DESC
        """)
        print(pd.read_sql(q2, conn, params={"no_inter": "%SIN INTERSECCIÓN%"}))
        
        print("\n--- 3. Proyectos con Múltiples Capas ---")
        q3 = text("""
            SELECT num_capas, COUNT(*) as cantidad_proyectos
            FROM (
                SELECT b.sk_proyecto, COUNT(DISTINCT b.sk_capa) as num_capas
                FROM dw.bridge_interseccion_ambiental b
                JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
                WHERE c.nombre_capa NOT ILIKE :no_inter
                GROUP BY 1
            ) s
            GROUP BY 1 ORDER BY 1 ASC
        """)
        print(pd.read_sql(q3, conn, params={"no_inter": "%SIN INTERSECCIÓN%"}))
        
        print("\n--- 4. Cobertura Geográfica (Top 5 Provincias) ---")
        q4 = text("""
            SELECT geo.provincia, COUNT(*) as total_intersecciones
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_proyecto p ON b.sk_proyecto = p.sk_proyecto
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            LEFT JOIN (
                SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia 
                FROM dw.fact_regularizacion ORDER BY sk_proyecto, fecha_inicio_proceso DESC
            ) fr ON p.sk_proyecto = fr.sk_proyecto
            LEFT JOIN dw.dim_geografia geo ON fr.sk_geografia = geo.sk_geografia
            WHERE c.nombre_capa NOT ILIKE :no_inter
            AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            GROUP BY 1 ORDER BY 2 DESC LIMIT 5
        """)
        print(pd.read_sql(q4, conn, params={"no_inter": "%SIN INTERSECCIÓN%"}))

except Exception as e:
    print(f"Error: {e}")
