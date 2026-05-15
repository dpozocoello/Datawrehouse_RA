import psycopg2
import pandas as pd
import warnings
import os

warnings.filterwarnings('ignore')

def generate_matrix():
    print("1. Conectando a la base remota (suia_bpms_enlisy) para obtener proyectos SNAP...")
    conn_remote = psycopg2.connect(
        host="172.16.0.179",
        database="suia_bpms_enlisy",
        user="postgres",
        password="postgres",
        port="5632"
    )

    q_snap = """
    SELECT DISTINCT v_proj.value as project_code
    FROM variableinstancelog v_snap
    JOIN variableinstancelog v_proj ON v_snap.processinstanceid = v_proj.processinstanceid
    WHERE v_snap.variableid ILIKE '%SNAP%'
    AND v_proj.variableid IN ('tramite', 'numero_tramite')
    """
    df_snap = pd.read_sql(q_snap, conn_remote)
    conn_remote.close()
    
    snap_projects = set(df_snap['project_code'].dropna().astype(str).str.strip())
    print(f"   -> Encontrados {len(snap_projects)} proyectos únicos que intersecan con SNAP.")

    print("\n2. Conectando a la base local (area_stage_saf_suia) para obtener proyectos completados...")
    conn_local = psycopg2.connect(
        host="172.16.0.182",
        database="area_stage_saf_suia",
        user="postgres",
        password="postgres",
        port="5432"
    )

    q_bi = """
    SELECT 
        "CÓDIGO ACTIVIDAD" AS "Código CIIU",
        "ACTIVIDAD ECONÓMICA" AS "Actividad Económica",
        "CÓDIGO PROYECTO" AS "Código de Proyecto",
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
        "FECHA REGISTRO" AS "Fecha Registro"
    FROM bi_dashboard.vm_unificado_sistemas_bi
    WHERE "ESTADO PROCESO" = 'Completado'
    AND "FECHA REGISTRO" >= CURRENT_DATE - INTERVAL '10 years'
    """
    
    df_bi = pd.read_sql(q_bi, conn_local)
    conn_local.close()

    print(f"   -> Encontrados {len(df_bi)} proyectos en estado 'Completado'.")

    print("\n3. Calculando la intersección boolean...")
    # Clean project codes for comparison
    df_bi['Código de Proyecto'] = df_bi['Código de Proyecto'].astype(str).str.strip()
    
    # Create the boolean column
    df_bi['Intersección SNAP'] = df_bi['Código de Proyecto'].apply(lambda x: x in snap_projects)
    
    # Ensure columns match exactly the requested format and order
    columns_order = [
        'Código CIIU', 
        'Actividad Económica', 
        'Código de Proyecto', 
        'Nombre Proyecto', 
        'Estado', 
        'Impacto Ambiental', 
        'Tipo Permiso', 
        'Ubicación Geográfica', 
        'ÁREA RESPONSABLE PROYECTO', 
        'Intersección SNAP', 
        'Fecha Registro'
    ]
    
    df_final = df_bi[columns_order]

    output_file = 'matriz_regularizacion_ambiental_completados_snap_10_anios.xlsx'
    print(f"\n4. Exportando matriz a un solo archivo con multiples hojas ({output_file})...")
    
    chunk_size = 1000000
    num_chunks = (len(df_final) // chunk_size) + 1
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(df_final))
            chunk_df = df_final.iloc[start_idx:end_idx]
            
            sheet_name = f"Proyectos_Parte_{i+1}"
            print(f"   -> Guardando hoja '{sheet_name}' (filas {start_idx} a {end_idx})...")
            chunk_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
    print("   -> Exportación exitosa.")
    print(f"      - Total proyectos exportados: {len(df_final)}")
    print(f"      - Proyectos CON intersección SNAP (True): {df_final['Intersección SNAP'].sum()}")
    print(f"      - Proyectos SIN intersección SNAP (False): {len(df_final) - df_final['Intersección SNAP'].sum()}")

if __name__ == '__main__':
    generate_matrix()
