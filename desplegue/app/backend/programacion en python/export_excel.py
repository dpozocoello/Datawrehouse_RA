import pandas as pd
import psycopg2
import os

# Configuration
DB_HOST = "172.16.0.182"
DB_NAME = "area_stage_saf_suia"
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

OUTPUT_FILE = "matriz_regularizacion_ambiental_10_años.xlsx"
# Sheet name limited to 31 chars
SHEET_NAME = "Regularizacion_10_anios"

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
        return

    try:
        print("Executing query...")
        df = pd.read_sql(SQL_QUERY, conn)
        print(f"Query executed. Retrieved {len(df)} rows.")
        
        if df.empty:
            print("No data found. Exiting.")
            return

        print(f"Writing to {OUTPUT_FILE} (Sheet: {SHEET_NAME})...")
        # Direct export to single sheet
        df.to_excel(OUTPUT_FILE, sheet_name=SHEET_NAME, index=False)
            
        print("Export completed successfully.")
        print(f"File saved at: {os.path.abspath(OUTPUT_FILE)}")

    except Exception as e:
        print(f"An error occurred during processing: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
