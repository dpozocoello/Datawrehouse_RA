import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Functions to restore
functions_to_restore = """
def fuse_payments_dataframe(df):
    if df.empty: return df
    def get_real_id(row):
        nt = str(row['numero_transaccion']) if 'numero_transaccion' in row and pd.notna(row['numero_transaccion']) else ''
        ntr = str(row['numero_tramite']) if 'numero_tramite' in row and pd.notna(row['numero_tramite']) else ''
        if 'tramite' in row and pd.notna(row['tramite']): ntr = str(row['tramite'])
        if nt and nt not in ['0000000000', 'None', 'nan']: return nt
        if ntr and ntr not in ['0000000000', 'None', 'nan']: return ntr
        return f"DESC_{row['fecha_pago']}_{row.name}"

    df['clave_pago'] = df.apply(get_real_id, axis=1)
    fusionados = []
    group_cols = ['clave_pago']
    if 'codigo_proyecto' in df.columns: group_cols.append('codigo_proyecto')
        
    for keys, group in df.groupby(group_cols):
        monto = group['monto_pagado'].dropna().max()
        tarea = next((t for t in group['tarea_bpm'].dropna() if str(t) not in ['None', 'nan', '']), None)
        proceso = next((p for p in group['proceso_bpm'].dropna() if str(p) not in ['None', 'nan', '']), None)
        origenes = group['origen'].dropna().unique() if 'origen' in group else []
        origen_n = 'Fusionado (JBPM/SUIA)' if len(origenes) > 1 else (origenes[0] if len(origenes)>0 else None)
        
        nt_val = '0000000000'
        if 'numero_transaccion' in group:
            nt_valid = [x for x in group['numero_transaccion'].dropna() if str(x) not in ['0000000000', 'None']]
            nt_val = nt_valid[0] if nt_valid else '0000000000'
        
        res = {
            'monto_pagado': monto,
            'fecha_pago': group['fecha_pago'].iloc[0],
            'proceso_bpm': proceso,
            'tarea_bpm': tarea,
        }
        if 'numero_tramite' in group: res['numero_tramite'] = group['numero_tramite'].dropna().iloc[0] if not group['numero_tramite'].dropna().empty else None
        if 'numero_transaccion' in group: res['numero_transaccion'] = nt_val
        if 'tramite' in group: res['tramite'] = keys[0] if isinstance(keys, tuple) else keys
        if 'origen' in group: res['origen'] = origen_n
        if 'secuencia_pago' in group: res['secuencia_pago'] = group['secuencia_pago'].min()
        for col in ['codigo_proyecto', 'nombre_proyecto', 'tipo_permiso_ambiental', 'provincia', 'canton', 'oficina_tecnica', 'tipo_pago']:
            if col in group.columns: res[col] = group[col].iloc[0]
        fusionados.append(res)
        
    df_f = pd.DataFrame(fusionados)
    sort_cols = ["fecha_pago"]
    if 'secuencia_pago' in df_f.columns: sort_cols.append("secuencia_pago")
    return df_f.sort_values(by=sort_cols, ascending=[True] * len(sort_cols)).reset_index(drop=True)

@st.cache_data(ttl=600)
def load_project_history(codigo_proyecto):
    query = text('''
    SELECT 
        f.proceso, 
        f.tarea, 
        e.estado_proceso, 
        e.estado_tramite, 
        f.fecha_inicio_tarea, 
        COALESCE(f.fecha_fin_tarea, CURRENT_TIMESTAMP) as fecha_fin_tarea,
        u.usuario_tarea
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
    LEFT JOIN dw.dim_usuario u ON f.sk_usuario = u.sk_usuario
    WHERE p.codigo_proyecto = :cp
    AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
    ORDER BY f.fecha_inicio_tarea ASC;
    ''')
    return pd.read_sql(query, get_engine(), params={"cp": codigo_proyecto})

@st.cache_data(ttl=600)
def load_project_payments(codigo_proyecto):
    query = text('''
    SELECT 
        fp.numero_tramite,
        fp.numero_transaccion,
        fp.monto_pagado,
        dp.tipo_pago,
        dt.fecha as fecha_pago,
        fp.proceso_bpm,
        fp.tarea_bpm,
        fp.origen,
        fp.secuencia_pago
    FROM dw.fact_pago fp
    JOIN dw.dim_proyecto p ON fp.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_pago dp ON fp.sk_pago = dp.sk_pago
    LEFT JOIN dw.dim_tiempo dt ON fp.sk_fecha_pago = dt.sk_tiempo
    WHERE p.codigo_proyecto = :cp
    AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
    ORDER BY dt.fecha ASC, fp.secuencia_pago ASC
    ''')
    df = pd.read_sql(query, get_engine(), params={"cp": codigo_proyecto})
    return fuse_payments_dataframe(df)

@st.cache_data(ttl=600)
def load_management_summary(start_date, end_date, codigo_proyecto=None):
    if not codigo_proyecto:
        query = text('''
        SELECT 
            COUNT(DISTINCT p.codigo_proyecto) as total_proyectos
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        WHERE f.fecha_inicio_proceso BETWEEN :sd AND :ed
        AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        ''')
        return pd.read_sql(query, get_engine(), params={"sd": start_date, "ed": end_date})
    else:
        query = text('''
        SELECT 
            p.codigo_proyecto,
            p.nombre_proyecto,
            p.tipo_permiso_ambiental,
            p.tipo_sector,
            p.tipo_ente,
            p.sistema,
            p.estrategico,
            p.area_responsable,
            prop.nombre_proponente,
            prop.ced_ruc_proponente,
            geo.provincia,
            geo.canton,
            geo.parroquia,
            da.nombre_area as oficina_tecnica,
            f.superficie_proyecto,
            f.interseccion_snap,
            f.numero_resolucion,
            f.fecha_resolucion,
            f.ente_acreditado,
            MIN(f.fecha_inicio_proceso) as primera_fecha_inicio,
            MAX(f.fecha_fin_proceso) as ultima_fecha_fin,
            COUNT(DISTINCT f.tarea) as total_tareas_realizadas,
            MAX(e.estado_proceso) as estado_actual
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
        LEFT JOIN dw.dim_proponente prop ON f.sk_proponente = prop.sk_proponente
        LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
        WHERE p.codigo_proyecto = :cp
        GROUP BY 
            p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental, p.tipo_sector,
            p.tipo_ente, p.sistema, p.estrategico, p.area_responsable,
            prop.nombre_proponente, prop.ced_ruc_proponente,
            geo.provincia, geo.canton, geo.parroquia, da.nombre_area,
            f.superficie_proyecto, f.interseccion_snap, f.numero_resolucion,
            f.fecha_resolucion, f.ente_acreditado
        ''')
        return pd.read_sql(query, get_engine(), params={"cp": codigo_proyecto})
"""

if "def load_management_summary" not in content:
    content = content.replace("# --- INTERFAZ DE USUARIO ---", functions_to_restore + "\n# --- INTERFAZ DE USUARIO ---")
    print("SUCCESS: Injected missing analytic functions.")
else:
    print("FUNCTIONS PREVIOUSLY EXISTENT")


# 2. Re-wire Tab 3 to include Visualizers (Gantt and Flowchart)
old_tab3_ui = """                st.info("No hay historial de tareas para este proyecto.")
                
            st.subheader("Registro de Pagos Asociados")"""

new_tab3_ui = """                st.info("No hay historial de tareas para este proyecto.")

            # --- VISUALIZADORES AVANZADOS (Flujo y Gantt) ---
            if not df_hist.empty:
                st.markdown("---")
                col_g, col_f = st.columns(2)
                with col_g:
                    with st.expander("📊 Diagrama de Gantt (Trazabilidad Temporal)", expanded=False):
                        # Ensure timestamps
                        df_hist['fecha_inicio_tarea'] = pd.to_datetime(df_hist['fecha_inicio_tarea'])
                        df_hist['fecha_fin_tarea'] = pd.to_datetime(df_hist['fecha_fin_tarea'])
                        if 'usuario_tarea' not in df_hist.columns:
                            df_hist['usuario_tarea'] = 'Sistema'
                            
                        fig_gantt = px.timeline(df_hist, x_start="fecha_inicio_tarea", x_end="fecha_fin_tarea", 
                                                y="tarea", color="estado_proceso", hover_name="usuario_tarea",
                                                title="Línea de Vida del Proyecto")
                        fig_gantt.update_yaxes(autorange="reversed")
                        st.plotly_chart(fig_gantt, use_container_width=True)
                        
                with col_f:
                    with st.expander("🔄 Diagrama de Flujo (Procesal)", expanded=False):
                        flow = "digraph Process {\\n"
                        flow += "node [shape=box, style=filled, color=\\\"#0A3D62\\\", fontcolor=white];\\n"
                        # Generate nodes
                        for i in range(len(df_hist)-1):
                            t1 = str(df_hist.iloc[i]['tarea']).replace('"', '')
                            t2 = str(df_hist.iloc[i+1]['tarea']).replace('"', '')
                            flow += f'"{t1}" -> "{t2}";\\n'
                        flow += "}"
                        st.graphviz_chart(flow)
                
            st.subheader("Registro de Pagos Asociados")"""

if old_tab3_ui in content:
    content = content.replace(old_tab3_ui, new_tab3_ui)
    print("SUCCESS: Integrated frontend UX visualizers (Gantt/Graphviz).")
else:
    print("FAILED TO FIND TAB 3 UI BLOCK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
