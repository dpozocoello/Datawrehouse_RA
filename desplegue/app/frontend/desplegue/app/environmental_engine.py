import pandas as pd
from sqlalchemy import text

def load_environmental_analytic_data(engine, prov='TODAS', cant='TODOS', parr='TODAS', ofic='TODAS', sd=None, ed=None, selected_cats=None, solo_emisoras_aaa=False, tipo_area='TODOS'):
    try:
        params = {}
        where = "1=1"
        if prov != 'TODAS':
            where += " AND geo.provincia = :prov"
            params['prov'] = prov
        if cant != 'TODOS':
            where += " AND geo.canton = :cant"
            params['cant'] = cant
        if parr != 'TODAS':
            where += " AND geo.parroquia = :parr"
            params['parr'] = parr
        if ofic != 'TODAS':
            where += " AND da.nombre_area = :ofic"
            params['ofic'] = ofic
        if tipo_area != 'TODOS':
            where += " AND da.siglas_tipo_area = :tipo_area"
            params['tipo_area'] = tipo_area
        if solo_emisoras_aaa:
            where += " AND da.es_emisora_aaa = TRUE"
        if sd and ed:
            where += " AND f.fecha_inicio_proceso BETWEEN :sd AND :ed"
            params['sd'] = sd
            params['ed'] = ed

        # SQL classification with Hierarchical Logic (Executive Consistency)
        # Priority: SNAP (1) > Intangible (2) > Bosque (3) > Patrimonio (4) > N/A (5)
        query = f'''
        WITH ranked_inter AS (
            SELECT 
                p.codigo_proyecto,
                p.nombre_proyecto,
                geo.provincia,
                geo.canton,
                geo.parroquia,
                da.nombre_area as oficina_tecnica,
                f.interseccion_snap,
                f.areas_protegidas,
                f.superficie_proyecto,
                p.tipo_permiso_ambiental,
                CASE 
                    WHEN f.interseccion_snap = 'SI' OR f.areas_protegidas ILIKE '%%SNAP%%' THEN 1
                    WHEN f.areas_protegidas ILIKE '%%INTANGIBLE%%' THEN 2
                    WHEN f.areas_protegidas ILIKE '%%BOSQUE%%' THEN 3
                    WHEN f.areas_protegidas ILIKE '%%PATRIMONIO FORESTAL%%' THEN 4
                    ELSE 5
                END as prioridad
            FROM dw.fact_regularizacion f
            JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
            JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
            LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
            WHERE {where}
              AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
              AND p.codigo_proyecto != 'N/A'
              AND p.nombre_proyecto != 'N/A'
        ),
        unique_inter AS (
            SELECT DISTINCT ON (codigo_proyecto) 
                codigo_proyecto,
                nombre_proyecto,
                provincia,
                canton,
                parroquia,
                oficina_tecnica,
                NULLIF(REPLACE(areas_protegidas, '|', ''), '') as areas_protegidas,
                superficie_proyecto,
                tipo_permiso_ambiental,
                prioridad,
                CASE 
                    WHEN prioridad = 1 THEN '🛡️ SNAP'
                    WHEN prioridad = 2 THEN '🔒 ZONAS INTANGIBLES'
                    WHEN prioridad = 3 THEN '🌳 BOSQUES PROTECTORES'
                    WHEN prioridad = 4 THEN '🌲 PATRIMONIO FORESTAL DEL ESTADO'
                    ELSE '⚪ SIN INTERSECCIÓN'
                END as categoria_ambiental
            FROM ranked_inter
            ORDER BY codigo_proyecto, prioridad ASC
        )
        SELECT * FROM unique_inter
        '''
        
        df = pd.read_sql(text(query), engine, params=params)
        
        # Filtrado adicional por categorías seleccionadas (Front-end level for responsiveness)
        if selected_cats and len(selected_cats) > 0:
            df = df[df['categoria_ambiental'].isin(selected_cats)]
            
        return df
    except Exception as e:
        print(f"Error en environmental_engine: {e}")
        return pd.DataFrame()

def get_environmental_kpis(df):
    if df.empty:
        return {"total_proyectos": 0, "total_has": 0, "capas_activas": 0}
    
    # As the DF is already unique by project code, we just sum/count
    total_proj = len(df)
    total_has = df['superficie_proyecto'].sum()
    capas_activas = df[df['categoria_ambiental'] != '⚪ SIN INTERSECCIÓN']['categoria_ambiental'].nunique()
    
    return {
        "total_proyectos": total_proj,
        "total_has": total_has,
        "capas_activas": capas_activas
    }

def get_heatmap_data(df, level='provincia'):
    if df.empty:
        return pd.DataFrame()
    
    col = 'provincia' if level == 'provincia' else 'canton'
    df_inter = df[df['categoria_ambiental'] != '⚪ SIN INTERSECCIÓN']
    
    if df_inter.empty:
        return pd.DataFrame()
        
    return df_inter.groupby(col)['codigo_proyecto'].nunique().reset_index(name='densidad')
