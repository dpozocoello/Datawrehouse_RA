import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def map_areas():
    query = """
    WITH AreaGeoCount AS (
        SELECT 
            da.sk_area,
            da.nombre_area,
            geo.provincia,
            geo.canton,
            geo.parroquia,
            COUNT(*) as freq,
            RANK() OVER (PARTITION BY da.sk_area ORDER BY COUNT(*) DESC) as rank
        FROM dw.fact_regularizacion f
        JOIN dw.dim_area da ON f.sk_area = da.sk_area
        JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        GROUP BY 1, 2, 3, 4, 5
    )
    SELECT * FROM AreaGeoCount WHERE rank = 1 LIMIT 30
    """
    df = pd.read_sql(query, engine)
    print(df.to_string())

if __name__ == "__main__":
    map_areas()
