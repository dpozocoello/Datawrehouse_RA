import pandas as pd
import psycopg2
import math
import os

# Configuration
DB_HOST = "172.16.0.182"
DB_NAME = "area_stage_saf_suia" # Updated to likely database based on context
DB_USER = "postgres"
DB_PASS = "postgres"
DB_PORT = "5432"

SQL_QUERY = """
select distinct "CÓDIGO ACTIVIDAD" AS "Código CIIU",
    "ACTIVIDAD ECONÓMICA" AS "Actividad Económica",
    "CÓDIGO PROYECTO" as "Código de Proyecto",
    "NOMBRE PROYECTO" AS "Nombre Proyecto",
    "ESTADO PROCESO" AS "Estado",
    CASE
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Licencia%' THEN 'Medio/Alto Impacto'
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Registro%' THEN 'Bajo Impacto'
        WHEN "TIPO PERMISO AMBIENTAL" ILIKE '%Certificado%' THEN 'No Requiere Permiso'
        ELSE 'Desconocido'
    END AS "Impacto Ambiental",
    "TIPO PERMISO AMBIENTAL" AS "Tipo Permiso",
    "PROVINCIA" || ' - ' || "CANTON" || ' - ' || "PARROQUIA" AS "Ubicación Geográfica",
    "ÁREA RESPONSABLE PROYECTO" AS "ÁREA RESPONSABLE PROYECTO",
    CASE
    WHEN "INTERSECTA CON" is null THEN 'Sin Intersección SNAP'
    ELSE "INTERSECTA CON"
	END AS "Intersección SNAP",
    "FECHA REGISTRO" AS "Fecha Registro"
FROM bi_dashboard.vm_unificado_sistemas_bi
WHERE "FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '10 years'
    AND "ESTADO PROCESO" = 'Completado'
ORDER BY "FECHA REGISTRO" ASC;
"""

OUTPUT_FILE = "reporte_ciiu_split.xlsx"

def main():
    print(f"Connecting to {DB_HOST}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        print("Connection successful.")
    except Exception as e:
        print(f"Error connecting to database '{DB_NAME}' on {DB_HOST}: {e}")
        print("Please verify the database name and connection details.")
        return

    try:
        print("Executing query...")
        df = pd.read_sql(SQL_QUERY, conn)
        print(f"Query executed. Retrieved {len(df)} rows.")
        
        if df.empty:
            print("No data found. Exiting.")
            return

        # Split logic
        total_rows = len(df)
        split_idx = math.ceil(total_rows / 2)
        
        df1 = df.iloc[:split_idx]
        df2 = df.iloc[split_idx:]
        
        print(f"Splitting data into two sheets: {len(df1)} rows and {len(df2)} rows.")
        
        print(f"Writing to {OUTPUT_FILE}...")
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            df1.to_excel(writer, sheet_name='Part 1', index=False)
            df2.to_excel(writer, sheet_name='Part 2', index=False)
            
        print("Export completed successfully.")
        print(f"File saved at: {os.path.abspath(OUTPUT_FILE)}")

    except Exception as e:
        print(f"An error occurred during processing: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
