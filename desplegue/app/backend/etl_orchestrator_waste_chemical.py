import psycopg2
import sys

# Configuraciones de Conexión (Ajustar según ambiente final)
# Origen: suia_enlisy
CONN_ORIGIN = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres"
}

# Destino: DWH Local (Ajustar credenciales)
CONN_DEST = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def execute_etl():
    try:
        print("Iniciando ETL de Desechos y Sustancias Químicas...")
        
        # 1. Leer los scripts SQL
        with open('etl_waste_chemical_extract.sql', 'r', encoding='utf-8') as f:
            extract_sql = f.read()
            
        with open('etl_waste_chemical_load.sql', 'r', encoding='utf-8') as f:
            load_sql = f.read()
            
        # 2. Conexiones
        print("Conectando a base de datos de origen y destino...")
        # (Aquí normalmente se usaría Pandas o copy_expert para pasar datos por STG, 
        #  o si están en el mismo server se usa dblink. Para este template, simularemos 
        # la ejecución de los scripts asumiendo que el DW los lee vía FDW o dblink).
        
        conn_dest = psycopg2.connect(**CONN_DEST)
        cur_dest = conn_dest.cursor()
        
        # 3. Ejecutar Carga a STAGING (asumiendo FDW implementado en DW)
        # print("Ejecutando Extracción a Staging...")
        # cur_dest.execute(extract_sql) # o lógica de copia
        
        # 4. Ejecutar Carga DW (Dimensiones y Hechos)
        print("Ejecutando Carga a STG, Dimensiones y Hechos...")
        cur_dest.execute(load_sql)
        
        conn_dest.commit()
        print("ETL completado exitosamente.")
        
    except Exception as e:
        print(f"Error durante la ejecución del ETL: {e}")
        if 'conn_dest' in locals():
            conn_dest.rollback()
    finally:
        if 'cur_dest' in locals(): cur_dest.close()
        if 'conn_dest' in locals(): conn_dest.close()

if __name__ == "__main__":
    execute_etl()
