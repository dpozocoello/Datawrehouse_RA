import pandas as pd
from sqlalchemy import create_engine
import datetime

DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dw_reg_v1"

def get_engine():
    conn_str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"
    return create_engine(conn_str)

def get_geo_provincias():
    try:
        query = "SELECT DISTINCT provincia FROM dw.dim_geografia WHERE provincia IS NOT NULL ORDER BY 1"
        df = pd.read_sql(query, get_engine())
        return ["TODAS"] + df['provincia'].tolist()
    except Exception as e:
        print(f"Error provinces: {e}")
        return ["TODAS"]

def get_geo_cantones(provincia):
    try:
        query = "SELECT DISTINCT canton FROM dw.dim_geografia WHERE provincia = %(p)s ORDER BY 1"
        df = pd.read_sql(query, get_engine(), params={"p": provincia})
        return ["TODOS"] + df['canton'].tolist()
    except Exception as e:
        print(f"Error cantons: {e}")
        return ["TODOS"]

def load_geo_filtered_data(provincia, canton, sd, ed):
    try:
        params = {"sd": sd, "ed": ed}
        where = "f.fecha_inicio_proceso BETWEEN %(sd)s AND %(ed)s"
        if provincia != "TODAS":
            where += " AND geo.provincia = %(prov)s"
            params["prov"] = provincia
        if canton != "TODOS":
            where += " AND geo.canton = %(cant)s"
            params["cant"] = canton
            
        query = f'''
        SELECT 
            p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental,
            geo.provincia, geo.canton, f.superficie_proyecto, f.fecha_inicio_proceso,
            e.estado_proceso
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
        WHERE {where} AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        LIMIT 10
        '''
        return pd.read_sql(query, get_engine(), params=params)
    except Exception as e:
        print(f"Error data: {e}")
        return pd.DataFrame()

print("Provincias:", get_geo_provincias()[:5])
print("Cantones de PICHINCHA:", get_geo_cantones("PICHINCHA")[:5])
sd = datetime.date(2000, 1, 1)
ed = datetime.date(2026, 12, 31)
df = load_geo_filtered_data("TODAS", "TODOS", sd, ed)
print("Data sample size:", len(df))
if not df.empty:
    print(df.head(2))
