import pandas as pd
from sqlalchemy import create_engine
import sys
import os

sys.path.append(r'F:/Datawrehouse_RA/etl')
try:
    from config import CONN_DWH_LOCAL, CONN_SUIA_ENLISY, CONN_JBPM
except ImportError:
    print("No se pudo importar config.py")
    sys.exit(1)

def get_engine(conn_dict):
    uri = f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"
    return create_engine(uri)

def buscar_recuperados():
    print("Iniciando análisis forense de proyectos RECUPERADOS...")
    engine_dwh = get_engine(CONN_DWH_LOCAL)
    
    # 1. Obtener proyectos recuperados del DWH local
    query_local = """
        SELECT codigo_proyecto 
        FROM dw.dim_proyecto 
        WHERE nombre_proyecto ILIKE '%%Recuperado%%' OR nombre_proyecto = 'RECUPERADO';
    """
    df_recuperados = pd.read_sql(query_local, engine_dwh)
    
    if df_recuperados.empty:
        print("No se encontraron proyectos marcados como RECUPERADO en dw.dim_proyecto.")
        return
        
    codigos_buscar = df_recuperados['codigo_proyecto'].dropna().unique().tolist()
    print(f"Se encontraron {len(codigos_buscar)} códigos de proyectos RECUPERADOS en el DWH.")
    
    # Limitar la lista para la clausula IN en SQL (manejar listas grandes si aplica)
    # Formatear para IN ('c1', 'c2')
    codigos_str = "'" + "','".join([str(c) for c in codigos_buscar]) + "'"
    
    # 2. Configurar búsquedas en servidores origen
    servidores = [
        {"nombre": "SUIA (172.16.0.179)", "engine": get_engine(CONN_SUIA_ENLISY)},
        {"nombre": "JBPM (172.16.0.226)", "engine": get_engine(CONN_JBPM)}
    ]
    
    resultados = []
    
    # Columnas sospechosas de contener el código de proyecto
    columnas_objetivo = ['codigo_proyecto', 'project_id', 'project_code', 'tramit_number']
    
    for srv in servidores:
        print(f"/nBuscando en servidor {srv['nombre']}...")
        engine = srv['engine']
        
        # Encontrar todas las tablas que tienen las columnas objetivo
        query_columns = f"""
            SELECT table_schema, table_name, column_name
            FROM information_schema.columns
            WHERE column_name IN ({",".join([f"'{c}'" for c in columnas_objetivo])})
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
              -- Evitar vistas materializadas complejas o de sistema si es necesario
        """
        try:
            df_tablas = pd.read_sql(query_columns, engine)
        except Exception as e:
            print(f"Error consultando information_schema en {srv['nombre']}: {e}")
            continue
            
        print(f"Se identificaron {len(df_tablas)} columnas potenciales a buscar en {srv['nombre']}.")
        
        for index, row in df_tablas.iterrows():
            schema = row['table_schema']
            tabla = row['table_name']
            columna = row['column_name']
            
            # Construir query dinámica para buscar los códigos
            # Solo buscamos si la tabla no es muy grande o si está indexada. Para no colgar la BD, usamos IN
            query_search = f"""
                SELECT DISTINCT '{srv['nombre']}' AS servidor, 
                       '{schema}' AS esquema, 
                       '{tabla}' AS tabla, 
                       {columna} AS codigo_encontrado
                FROM {schema}.{tabla}
                WHERE {columna} IN ({codigos_str});
            """
            try:
                # print(f"  Consultando {schema}.{tabla}...")
                df_res = pd.read_sql(query_search, engine)
                if not df_res.empty:
                    print(f"  --> Encontrados {len(df_res)} coincidencias en {schema}.{tabla}")
                    resultados.append(df_res)
            except Exception as e:
                # Silenciar errores por tablas inaccesibles o vistas corruptas
                pass
                
    # 3. Consolidar y guardar resultados
    if resultados:
        df_final = pd.concat(resultados, ignore_index=True)
        # Agrupar por código de proyecto
        
        output_file = r'F:/Datawrehouse_RA/etl/reporte_proyectos_recuperados.csv'
        df_final.to_csv(output_file, index=False, encoding='utf-8')
        print(f"/nBúsqueda completada. Resultados guardados en: {output_file}")
        
        # Mostrar resumen en consola por tabla
        resumen = df_final.groupby(['servidor', 'esquema', 'tabla']).size().reset_index(name='cantidad_encontrados')
        print("/n=== RESUMEN DE HALLAZGOS ===")
        print(resumen.to_string(index=False))
        
        print(f"/nTotal de ocurrencias encontradas: {len(df_final)}")
    else:
        print("/nNo se encontraron los códigos de proyecto en ninguna de las tablas analizadas de los servidores origen.")

if __name__ == "__main__":
    buscar_recuperados()
