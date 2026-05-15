import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def generate_data_dictionary():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                table_name,
                table_schema
            FROM information_schema.columns 
            WHERE table_schema IN ('dw', 'stg') 
            ORDER BY table_schema DESC, table_name, ordinal_position
        """)
        
        rows = cur.fetchall()
        
        with open('F:/Datawrehouse_RA/documentación/DWH_Diccionario_Tecnico_Datos_v1_5.md', 'w', encoding='utf-8') as f:
            f.write("# 📖 Diccionario Técnico de Datos: DRE Regularización Ambiental (v1.5)\n\n")
            f.write("Este documento detalla la estructura técnica exhaustiva de los esquemas `dw` y `stg` del Data Warehouse.\n\n")
            
            f.write("## 1. Relación de Capas\n")
            f.write("- **Esquema `stg`**: Capa de aterrizaje de datos transaccionales.\n")
            f.write("- **Esquema `dw`**: Capa dimensional (Star Schema) para analítica.\n\n")
            f.write("---\n")
            
            current_table = None
            for col, dtype, null, table, schema in rows:
                full_table = f"{schema}.{table}"
                if full_table != current_table:
                    current_table = full_table
                    f.write(f"\n### Tabla: `{current_table}`\n\n")
                    f.write("| Columna | Tipo de Dato | Nulable | Propósito |\n")
                    f.write("| :--- | :--- | :--- | :--- |\n")
                
                f.write(f"| {col} | {dtype} | {null} | - |\n")
        
        print("Final data dictionary generated successfully at F:/Datawrehouse_RA/documentación/DWH_Diccionario_Tecnico_Datos_v1_5.md")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    generate_data_dictionary()
