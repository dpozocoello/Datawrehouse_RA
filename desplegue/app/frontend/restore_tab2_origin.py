import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add load_projects_by_normativa function right before load_origin_period_report
new_func = """@st.cache_data(ttl=600)
def load_projects_by_normativa(origen, start_date, end_date):
    query = text('''
    SELECT DISTINCT ON (p.codigo_proyecto)
        p.codigo_proyecto,
        p.nombre_proyecto,
        p.tipo_permiso_ambiental,
        f.proceso,
        e.estado_proceso,
        e.estado_tramite,
        f.fecha_inicio_proceso,
        f.fecha_fin_proceso
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
    WHERE f.origen = :origen 
    AND f.fecha_inicio_proceso BETWEEN :sd AND :ed
    ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC
    ''')
    return pd.read_sql(query, get_engine(), params={"origen": origen, "sd": start_date, "ed": end_date})

@st.cache_data(ttl=600)
def load_origin_period_report"""
if 'load_projects_by_normativa' not in content:
    content = content.replace('@st.cache_data(ttl=600)\ndef load_origin_period_report', new_func)

# Now Tab 2 updates
old_tab2 = """elif active_tab == "tab2":
    st.header("🔍 Orígenes de los Proyectos según Normativa")
    df_origin = load_projects_by_origin_summary()
    if not df_origin.empty:
        fig_origin = px.pie(df_origin, values='cantidad_proyectos', names='origen', 
                            title="Proyectos por Fuente", hole=.4,
                            color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_origin, use_container_width=True)
        st.dataframe(df_origin, use_container_width=True)
    else:
        st.info("No hay datos de proyectos para mostrar.")
        
    with st.expander("🛠️ Ver Identificación de Discrepancias (Staging vs DWH)"):
        st.info("Top 200 proyectos en Staging que no han sido migrados al DWH (Fact o Dim Proyectos).")
        source_map = {
            "SUIA (Proyectos v2)": "stg.suia_coa_bi",
            "JBPM (Histórico)": "stg.jbpm_sector_bi",
            "RCOA (Especial)": "stg.suia_rcoa_bi"
        }
        sel_source = st.selectbox("Seleccione Fuente de Datos", list(source_map.keys()))
        df_disc = load_discrepancies(source_map[sel_source])
        if not df_disc.empty:
            st.warning(f"Se encontraron {len(df_disc)} proyectos pendientes de migración.")
            st.dataframe(df_disc, use_container_width=True)
        else:
            st.success("Sin discrepancias detectadas para esta fuente.")"""

new_tab2 = """elif active_tab == "tab2":
    st.header("🔍 Orígenes de los Proyectos según Normativa")
    
    # 1. Resumen Gráfico General
    st.subheader("Distribución Global por Fuente Múltiple")
    df_origin = load_projects_by_origin_summary()
    if not df_origin.empty:
        fig_origin = px.pie(df_origin, values='cantidad_proyectos', names='origen', 
                            title="Proyectos por Fuente General", hole=.4,
                            color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_origin, use_container_width=True)
    
    # 2. Funcionalidad de Selección de Origen (Requerida por el usuario)
    st.markdown("---")
    st.subheader("Consultar Detalle de Proyectos por Normativa Específica")
    diccionario_origenes = {
        "Normativa COA": "COA",
        "Normativa RCOA": "RCOA",
        "Normativa 4 CATEGORIAS": "JBPM_4CAT",
        "Normativa SECTOR SUBSECTOR": "JBPM_SECTOR",
        "SIN NORMATIVA": "RECUPERADO",
        "Normativa HIDROCARBUROS": "JBPM_HIDRO"
    }
    
    sel_normativa = st.selectbox("Seleccione el Origen / Normativa", list(diccionario_origenes.keys()))
    if st.button("Consultar Proyectos de esta Normativa", type="primary"):
        origen_val = diccionario_origenes[sel_normativa]
        df_norm = load_projects_by_normativa(origen_val, start_date_in, end_date_in)
        if not df_norm.empty:
            st.success(f"Se encontraron {len(df_norm)} proyectos bajo la normativa '{sel_normativa}' (Origen DWH: {origen_val}).")
            st.dataframe(df_norm, use_container_width=True)
        else:
            st.warning(f"No hay proyectos para '{sel_normativa}' en el rango de fechas seleccionado.")
            
    st.markdown("---")
    with st.expander("🛠️ Ver Identificación de Discrepancias (Staging vs DWH)"):
        st.info("Top 200 proyectos en Staging que no han sido migrados al DWH (Fact o Dim Proyectos).")
        source_map = {
            "SUIA (Proyectos v2)": "stg.suia_coa_bi",
            "JBPM (Histórico)": "stg.jbpm_sector_bi",
            "RCOA (Especial)": "stg.suia_rcoa_bi"
        }
        sel_source = st.selectbox("Seleccione Fuente de Datos", list(source_map.keys()))
        df_disc = load_discrepancies(source_map[sel_source])
        if not df_disc.empty:
            st.warning(f"Se encontraron {len(df_disc)} proyectos pendientes de migración.")
            st.dataframe(df_disc, use_container_width=True)
        else:
            st.success("Sin discrepancias detectadas para esta fuente.")"""

content = content.replace(old_tab2, new_tab2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS")
