import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "utf8"
}

def deploy_ddl():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        with open('f:/Datawrehouse_RA/ddl_waste_chemical.sql', 'r', encoding='utf-8') as f:
            ddl_sql = f.read()
            
        cur.execute(ddl_sql)
        conn.commit()
        print("¡DDL desplegado exitosamente!")
        
    except Exception as e:
        print(repr(e))
        if 'conn' in locals(): conn.rollback()
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    deploy_ddl()
