import pandas as pd
from sqlalchemy import create_engine
import sys

sys.path.append(r'F:\Datawrehouse_RA\ETL_p')
try:
    from config import CONN_DWH_LOCAL
except ImportError:
    print("No se pudo importar config.py")
    sys.exit(1)

def get_engine(conn_dict):
    uri = f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"
    return create_engine(uri)

def validar():
    print("Iniciando cruce y validación de proyectos recuperados...")
    engine = get_engine(CONN_DWH_LOCAL)
    
    # 1. Obtener los recuperados de la base de datos LOCAL (dim_proyecto)
    query_local = """
        SELECT dp.codigo_proyecto 
        FROM dw.dim_proyecto dp
        WHERE dp.nombre_proyecto ILIKE '%%Recuperado%%' OR dp.nombre_proyecto = 'RECUPERADO';
    """
    df_local = pd.read_sql(query_local, engine)
    codigos_locales = set(df_local['codigo_proyecto'].dropna())
    
    # Obtener un poco mas de contexto local para los "huerfanos" (que existen local pero NO en el CSV)
    query_local_detallada = """
        SELECT dp.codigo_proyecto, dp.nombre_proyecto, fp.origen as origen_pago
        FROM dw.dim_proyecto dp
        LEFT JOIN dw.fact_pago fp ON dp.sk_proyecto = fp.sk_proyecto
        WHERE dp.nombre_proyecto ILIKE '%%Recuperado%%' OR dp.nombre_proyecto = 'RECUPERADO';
    """
    df_local_det = pd.read_sql(query_local_detallada, engine)
    
    # 2. Cargar el CSV generado previamente
    csv_path = r'F:\Datawrehouse_RA\ETL_p\reporte_proyectos_recuperados.csv'
    try:
        df_csv = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        return
        
    codigos_origen = set(df_csv['codigo_encontrado'].dropna())
    
    # 3. Realizar los cruces
    encontrados = codigos_locales.intersection(codigos_origen)
    huerfanos_absolutos = codigos_locales - codigos_origen
    
    print("\n" + "="*50)
    print("RESULTADOS DE LA VALIDACIÓN FORENSE")
    print("="*50)
    print(f"Total Proyectos Marcados 'RECUPERADO' en DWH Local : {len(codigos_locales):,}")
    print(f"Total Encontrados en Servidores Origen (CSV)       : {len(encontrados):,}")
    print(f"Total Huérfanos Absolutos (No encontrados origen)  : {len(huerfanos_absolutos):,}")
    
    coverage = (len(encontrados) / len(codigos_locales)) * 100 if len(codigos_locales) > 0 else 0
    print(f"Nivel de Identidad Positiva en Origen              : {coverage:.2f}%")
    
    # 4. Detallar de donde vienen los que SI se encontraron
    if len(encontrados) > 0:
        df_encontrados_detalle = df_csv[df_csv['codigo_encontrado'].isin(encontrados)]
        
        print("\n=== DISTRIBUCIÓN POR TABLAS DE ORIGEN (Proyectos Identificados) ===")
        # Agrupar por servidor y tabla para identificar el peso relativo de cada origen
        dist = df_encontrados_detalle.groupby(['servidor', 'esquema', 'tabla'])['codigo_encontrado'].nunique().reset_index(name='proyectos_unicos')
        dist = dist.sort_values(by='proyectos_unicos', ascending=False)
        print(dist.to_string(index=False))
        
    # 5. Analizar los huérfanos absolutos (Si existen)
    if len(huerfanos_absolutos) > 0:
        print("\n=== ANÁLISIS DE HUÉRFANOS ABSOLUTOS ===")
        print("Trámites marcados como recuperados en DWH que no aparecieron en ninguna de las tablas analizadas en 179/226.")
        df_huerf = df_local_det[df_local_det['codigo_proyecto'].isin(huerfanos_absolutos)]
        
        # ¿Tienen pagos asociados? si tienen pagos, quiere decir que ingresaron por pagos pero ya no estan en las tablas base.
        origen_pagos = df_huerf.groupby('origen_pago')['codigo_proyecto'].nunique()
        print("\nOrigen (Según fact_pago) de los Huérfanos Absolutos:")
        if not origen_pagos.empty:
            print(origen_pagos)
        else:
            print("Ninguno de los huérfanos absolutos tiene un registro en dw.fact_pago.")
            
        print("\nEjemplo de Códigos Huérfanos:")
        print(list(huerfanos_absolutos)[:10])

    print("="*50 + "\n")

if __name__ == "__main__":
    validar()
