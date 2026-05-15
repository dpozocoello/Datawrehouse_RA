import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add get_unique_tramites and load_projects_advanced_filter functions
new_funcs = """@st.cache_data(ttl=3600)
def get_unique_tramites():
    try:
        query = "SELECT DISTINCT proceso FROM dw.fact_regularizacion WHERE proceso IS NOT NULL AND proceso != '' ORDER BY proceso"
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + df['proceso'].tolist()
    except:
        return ["TODOS"]

@st.cache_data(ttl=600)
def load_projects_advanced_filter(origen, tipo_tramite, apply_dates, start_date, end_date):
    base_query = '''
    SELECT DISTINCT ON (p.codigo_proyecto)
        p.codigo_proyecto,
        p.nombre_proyecto,
        p.tipo_permiso_ambiental,
        f.origen,
        f.proceso as tipo_tramite,
        e.estado_proceso,
        e.estado_tramite,
        f.fecha_inicio_proceso,
        f.fecha_fin_proceso
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
    WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
    '''
    params = {}
    if origen != "TODOS":
        base_query += " AND f.origen = %(origen)s"
        params["origen"] = origen
    if tipo_tramite != "TODOS":
        base_query += " AND f.proceso = %(tipo_tramite)s"
        params["tipo_tramite"] = tipo_tramite
    if apply_dates:
        base_query += " AND f.fecha_inicio_proceso BETWEEN %(sd)s AND %(ed)s"
        params["sd"] = start_date
        params["ed"] = end_date
        
    base_query += " ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC LIMIT 5000"
    return pd.read_sql(base_query, get_engine(), params=params)

@st.cache_data(ttl=600)
def load_projects_by_normativa"""

if "def load_projects_advanced_filter" not in content:
    content = content.replace("@st.cache_data(ttl=600)\ndef load_projects_by_normativa", new_funcs)

# 2. Update Tab 2 layout completely
old_tab2_pattern = r'elif active_tab == "tab2":.*?elif active_tab == "tab3":'

new_tab2_code = """elif active_tab == "tab2":
    st.header("🔍 Orígenes de los Proyectos según Normativa")
    
    st.subheader("Distribución Global por Fuente Múltiple")
    df_origin = load_projects_by_origin_summary()
    if not df_origin.empty:
        fig_origin = px.pie(df_origin, values='cantidad_proyectos', names='origen', 
                            title="Proyectos por Fuente General", hole=.4,
                            color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_origin, use_container_width=True)

    st.markdown("---")
    st.subheader("Buscador Avanzado de Proyectos (Data Warehouse)")
    st.info("Filtre la base de datos completa interactuando con los selectores. La consulta inicial abarca toda la base (sin filtro temporal obligatorio).")
    
    # Dropdowns for advanced filtering
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        diccionario_origenes = {
            "TODAS LAS BASES (DWH COMPLETO)": "TODOS",
            "Normativa COA": "COA",
            "Normativa RCOA": "RCOA",
            "Normativa 4 CATEGORIAS": "JBPM_4CAT",
            "Normativa SECTOR SUBSECTOR": "JBPM_SECTOR",
            "SIN NORMATIVA": "RECUPERADO",
            "Normativa HIDROCARBUROS": "JBPM_HIDRO"
        }
        sel_normativa_label = st.selectbox("Origen / Normativa", list(diccionario_origenes.keys()))
        origen_val = diccionario_origenes[sel_normativa_label]
        
    with col_f2:
        lista_tramites = get_unique_tramites()
        sel_tramite = st.selectbox("Tipo de Trámite / Proceso", lista_tramites)
        
    with col_f3:
        st.write("")
        st.write("")
        apply_dates = st.checkbox("Filtrar por rango de fechas (Globales)", value=False)
        
    if st.button("Aplicar Filtros y Consultar", type="primary", use_container_width=True):
        with st.spinner("Consultando al Data Warehouse..."):
            df_norm = load_projects_advanced_filter(origen_val, sel_tramite, apply_dates, start_date_in, end_date_in)
            if not df_norm.empty:
                st.success(f"Se encontraron {len(df_norm)} proyectos coincidentes (mostrando máx. 5000).")
                st.dataframe(df_norm, use_container_width=True)
            else:
                st.warning("No se encontraron proyectos bajo los criterios seleccionados.")
            
    st.markdown("---")
    with st.expander("🛠️ Ver Identificación de Discrepancias (Staging vs DWH)"):
        st.info("Top 200 proyectos en Staging que no han sido migrados al DWH (Fact o Dim Proyectos).")
        source_map = {
            "SUIA (Proyectos v2)": "stg.suia_coa_bi",
            "JBPM (Histórico)": "stg.jbpm_sector_bi",
            "RCOA (Especial)": "stg.suia_rcoa_bi"
        }
        sel_source_disc = st.selectbox("Seleccione Fuente de Datos", list(source_map.keys()), key="disc_selectbox")
        df_disc = load_discrepancies(source_map[sel_source_disc])
        if not df_disc.empty:
            st.warning(f"Se encontraron {len(df_disc)} proyectos pendientes de migración.")
            st.dataframe(df_disc, use_container_width=True)
        else:
            st.success("Sin discrepancias detectadas para esta fuente.")

elif active_tab == "tab3":"""

content = re.sub(old_tab2_pattern, new_tab2_code, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS")
