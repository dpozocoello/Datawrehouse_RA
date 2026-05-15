import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_func = """@st.cache_data(ttl=600)
def load_integrity_summary():
    query = "SELECT * FROM dw.v_integridad_dashboard ORDER BY total_dwh DESC"
    return pd.read_sql(query, get_engine())

@st.cache_data(ttl=600)
def load_tramites_detail(origen):
    query = '''
    SELECT 
        TO_CHAR(f.fecha_inicio_proceso, 'YYYY-MM') as periodo_cronologico,
        f.proceso as tipo_de_tramite,
        COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    WHERE f.origen = %(origen)s 
      AND f.fecha_inicio_proceso IS NOT NULL 
      AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
      AND f.proceso IS NOT NULL
      AND f.proceso != ''
    GROUP BY 1, 2
    ORDER BY 1 ASC, 3 DESC
    '''
    return pd.read_sql(query, get_engine(), params={"origen": origen})"""

if "def load_tramites_detail" not in content:
    content = content.replace("@st.cache_data(ttl=600)\ndef load_integrity_summary():\n    query = \"SELECT * FROM dw.v_integridad_dashboard ORDER BY total_dwh DESC\"\n    return pd.read_sql(query, get_engine())", new_func)


# Now update Tab 1
old_tab1 = """if active_tab == "tab1":
    st.header("📊 Resumen de Integridad - DWH")
    df_integrity = load_integrity_summary()
    if not df_integrity.empty:
        cols = st.columns(4)
        for i, row in df_integrity.iterrows():
            with cols[i % 4]:
                st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-label">{row['origen']}</div>
                    <div class="kpi-value">{row['total_dwh']:,}</div>
                    <div class="kpi-label">Proyectos Registrados</div>
                </div>
                ''', unsafe_allow_html=True)
        st.subheader("Detalle Cronológico por Origen")"""

new_tab1 = """if active_tab == "tab1":
    st.header("📊 Resumen de Integridad - DWH")
    df_integrity = load_integrity_summary()
    if not df_integrity.empty:
        cols = st.columns(4)
        for i, row in df_integrity.iterrows():
            with cols[i % 4]:
                st.markdown(f'''
                <div class="kpi-card" style="margin-bottom: 5px; padding: 1.5rem !important;">
                    <div class="kpi-label">{row['origen']}</div>
                    <div class="kpi-value">{row['total_dwh']:,}</div>
                    <div class="kpi-label" style="font-size: 0.8rem !important;">Proyectos Registrados</div>
                </div>
                ''', unsafe_allow_html=True)
                if st.button(f"🔍 Ver Trámites", key=f"btn_det_{row['origen']}", use_container_width=True):
                    st.session_state['selected_origin_detail'] = row['origen']
        
        if 'selected_origin_detail' in st.session_state:
            sel_origen = st.session_state['selected_origin_detail']
            st.markdown("---")
            col_t, col_b = st.columns([5, 1])
            with col_t:
                st.subheader(f"Desglose Cronológico de Trámites: {sel_origen}")
            with col_b:
                if st.button("❌ Cerrar Detalle", use_container_width=True):
                    del st.session_state['selected_origin_detail']
                    st.rerun()
            
            df_detail = load_tramites_detail(sel_origen)
            if not df_detail.empty:
                st.dataframe(df_detail, use_container_width=True)
            else:
                st.info(f"No hay detalles cronológicos disponibles para {sel_origen}.")
                
        st.markdown("---")
        st.subheader("Cuadro de Producción Histórico vs DWH")"""

if old_tab1 in content:
    content = content.replace(old_tab1, new_tab1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("TARGET NOT FOUND. RETRYING WITH REGEX.")
    # Fallback with regex
    pattern = r'if active_tab == "tab1":.*?st\.subheader\("Detalle Cronológico por Origen"\)'
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, new_tab1, content, flags=re.DOTALL)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("SUCCESS (REGEX)")
    else:
        print("FAILED TO FIND TARGET BLOCKS")
