import pandas as pd
import psycopg2

# Conexiones
SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}
BPMS_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_bpms_enlisy_app", "user":"postgres", "password":"postgres"}
DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def run_audit():
    try:
        print("--- AUDITORÍA DE INTERSECCIONES (V1.8.5 - Final) ---")
        
        # 1. Capas y Proyectos
        print("Extrayendo capas de producción (suia_enlisy)...")
        conn_suia = psycopg2.connect(**SUIA_PARAMS)
        
        # Obtener nombres de proyectos y sus IDs de capa
        query_prod = """
            SELECT 
                plc.prco_cua as project_code,
                iplc.laye_id
            FROM coa_mae.intersections_project_licencing_coa iplc
            JOIN coa_mae.project_licencing_coa plc ON iplc.prco_id = plc.prco_id
            WHERE iplc.inpr_status = TRUE
        """
        df_prod_raw = pd.read_sql_query(query_prod, conn_suia)
        conn_suia.close()
        
        print(f"   [OK] {len(df_prod_raw)} registros de capas obtenidos.")
        
        # Mapeo de IDs (Basado en hallazgos previos y lógica de negocio)
        # SNAP: 11, 21 (según ingesta_intersection.py)
        # Bosques: 41? Patrimonio: 31? Intangibles: 51?
        # Usaremos sets para eficiencia
        snap_ids = {1, 11, 21}
        bosque_ids = {2, 3, 26, 41}
        patrimonio_ids = {27, 31}
        intangible_ids = {28, 51}
        
        def get_flags(layers):
            lset = set(layers)
            return pd.Series({
                'SNAP_PROD': not lset.isdisjoint(snap_ids),
                'BOSQUES_PROD': not lset.isdisjoint(bosque_ids),
                'PATRIMONIO_PROD': not lset.isdisjoint(patrimonio_ids),
                'INTANGIBLES_PROD': not lset.isdisjoint(intangible_ids)
            })
        
        df_prod_flags = df_prod_raw.groupby('project_code')['laye_id'].apply(list).apply(get_flags).reset_index()
        
        # 2. BPM SNAP (suia_enlisy_bpms)
        print("Extrayendo SNAP de BPM (suia_bpms_enlisy_app)...")
        conn_bpms = psycopg2.connect(**BPMS_PARAMS)
        query_bpm = """
            SELECT DISTINCT v.value as project_code 
            FROM variableinstancelog v 
            JOIN bamtasksummary b ON v.processinstanceid = b.processinstanceid 
            WHERE v.variableid ILIKE '%%snap%%' AND b.status = 'Completed'
        """
        df_bpm = pd.read_sql_query(query_bpm, conn_bpms)
        df_bpm['SNAP_BPM'] = True
        conn_bpms.close()
        
        df_prod_full = df_prod_flags.merge(df_bpm, on='project_code', how='outer').fillna(False)
        
        # 3. DWH Local
        print("Extrayendo datos de DWH local...")
        conn_dwh = psycopg2.connect(**DWH_PARAMS)
        query_dwh = """
            SELECT 
                dp.codigo_proyecto as project_code, 
                di.dictamen_final 
            FROM dw.dim_intersection di 
            JOIN dw.dim_proyecto dp ON di.sk_proyecto = dp.sk_proyecto 
            WHERE di.is_current = TRUE
        """
        df_dwh = pd.read_sql_query(query_dwh, conn_dwh)
        conn_dwh.close()
        
        def analyze_dwh(dictamen):
            d = str(dictamen).upper()
            return pd.Series({
                'SNAP_DWH': "SI INTERSECA" in d and "SNAP" in d,
                'BOSQUES_DWH': "BOSQUES PROTECTORES" in d,
                'PATRIMONIO_DWH': "PATRIMONIO FORESTAL" in d,
                'INTANGIBLES_DWH': "ZONAS INTANGIBLES" in d
            })
            
        df_dwh_flags = df_dwh['dictamen_final'].apply(analyze_dwh)
        df_dwh_final = pd.concat([df_dwh[['project_code']], df_dwh_flags], axis=1)
        
        # 4. Comparación
        print("Comparando consistencia...")
        df_audit = df_prod_full.merge(df_dwh_final, on='project_code', how='outer').fillna(False)
        
        df_audit['SNAP_CONSIST'] = (df_audit['SNAP_PROD'] | df_audit['SNAP_BPM']) == df_audit['SNAP_DWH']
        df_audit['BOSQUES_CONSIST'] = df_audit['BOSQUES_PROD'] == df_audit['BOSQUES_DWH']
        df_audit['PATRIMONIO_CONSIST'] = df_audit['PATRIMONIO_PROD'] == df_audit['PATRIMONIO_DWH']
        df_audit['INTANGIBLES_CONSIST'] = df_audit['INTANGIBLES_PROD'] == df_audit['INTANGIBLES_DWH']
        
        # Reporte
        total = len(df_audit)
        diff_total = len(df_audit[~(df_audit['SNAP_CONSIST'] & df_audit['BOSQUES_CONSIST'] & df_audit['PATRIMONIO_CONSIST'] & df_audit['INTANGIBLES_CONSIST'])])
        
        report = f"""# INFORME DE VALIDACIÓN DE INTERSECCIONES AMBIENTALES
Fecha Auditoría: {pd.Timestamp.now()}

## Resumen de Consistencia
- Total Proyectos Analizados: {total}
- Proyectos con Discrepancias: {diff_total}
- Consistencia General: {((total - diff_total)/total)*100:.2f}%

### Por Categoría
- SNAP: {df_audit['SNAP_CONSIST'].sum()} / {total} ({(df_audit['SNAP_CONSIST'].sum()/total)*100:.2f}%)
- Bosques Protectores: {df_audit['BOSQUES_CONSIST'].sum()} / {total} ({(df_audit['BOSQUES_CONSIST'].sum()/total)*100:.2f}%)
- Patrimonio Forestal: {df_audit['PATRIMONIO_CONSIST'].sum()} / {total} ({(df_audit['PATRIMONIO_CONSIST'].sum()/total)*100:.2f}%)
- Zonas Intangibles: {df_audit['INTANGIBLES_CONSIST'].sum()} / {total} ({(df_audit['INTANGIBLES_CONSIST'].sum()/total)*100:.2f}%)

## Proyectos en Producción INCORRECTOS o FALTANTES en DWH (Top 15)
{df_audit[~(df_audit['SNAP_CONSIST'] & df_audit['BOSQUES_CONSIST'])].head(15).to_string()}
        """
        
        print(report)
        with open('audit_results_intersection.txt', 'w', encoding='utf-8') as f:
            f.write(report)
            
        print("\n--- Auditoría finalizada correctamente ---")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_audit()
