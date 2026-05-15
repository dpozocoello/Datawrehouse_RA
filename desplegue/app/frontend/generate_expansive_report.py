from sqlalchemy import create_engine, text
import pandas as pd

def run_query(conn, query, params=None):
    try:
        return pd.read_sql(text(query), conn, params=params)
    except Exception as e:
        return str(e)

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        # 1. Top Layers
        q1 = """
            SELECT c.nombre_capa, COUNT(DISTINCT b.sk_proyecto) as total
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE c.nombre_capa NOT ILIKE '%%SIN INTERSECCIÓN%%'
            GROUP BY 1 ORDER BY 2 DESC LIMIT 15
        """
        df1 = run_query(conn, q1)
        
        # 2. Status Distribution
        q2 = """
            SELECT 
                CASE 
                    WHEN b.sk_proyecto IS NOT NULL AND c.nombre_capa NOT ILIKE '%%SIN INTERSECCIÓN%%' THEN 'Interseca'
                    ELSE 'No Interseca'
                END as estado,
                COUNT(DISTINCT p.sk_proyecto) as total
            FROM dw.dim_proyecto p
            LEFT JOIN dw.bridge_interseccion_ambiental b ON p.sk_proyecto = b.sk_proyecto
            LEFT JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            GROUP BY 1
        """
        df2 = run_query(conn, q2)
        
        # 3. By Permit Type
        q3 = """
            SELECT p.tipo_permiso_ambiental, COUNT(*) as total_intersecciones
            FROM dw.bridge_interseccion_ambiental b
            JOIN dw.dim_proyecto p ON b.sk_proyecto = p.sk_proyecto
            JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
            WHERE c.nombre_capa NOT ILIKE '%%SIN INTERSECCIÓN%%'
            AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            GROUP BY 1 ORDER BY 2 DESC
        """
        df3 = run_query(conn, q3)
        
        # 4. Multi-layer analysis
        q4 = """
            SELECT num_capas, COUNT(*) as qty
            FROM (
                SELECT b.sk_proyecto, COUNT(DISTINCT b.sk_capa) as num_capas
                FROM dw.bridge_interseccion_ambiental b
                JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
                WHERE c.nombre_capa NOT ILIKE '%%SIN INTERSECCIÓN%%'
                GROUP BY 1
            ) s
            GROUP BY 1 ORDER BY 1 ASC
        """
        df4 = run_query(conn, q4)
        
        # Generate Markdown
        with open('analisis_ambiental_detallado.md', 'w', encoding='utf-8') as f:
            f.write("# 🌲 Análisis Expansivo de Capas de Intersección Ambiental\n\n")
            f.write("Este análisis proporciona una visión estadística completa de los solapamientos ambientales registrados en el Data Warehouse.\n\n")
            
            f.write("## 1. Resumen Global de Intersección\n")
            f.write(df2.to_markdown(index=False) + "\n\n")
            
            f.write("## 2. Distribución por Capas Ambientales (Top 15)\n")
            f.write(df1.to_markdown(index=False) + "\n\n")
            
            f.write("## 3. Afectación por Tipo de Permiso\n")
            f.write(df3.to_markdown(index=False) + "\n\n")
            
            f.write("## 4. Intensidad de Solapamiento (Proyectos con múltiples capas)\n")
            f.write(df4.to_markdown(index=False) + "\n\n")

except Exception as e:
    with open('analisis_error.txt', 'w') as f:
        f.write(str(e))
