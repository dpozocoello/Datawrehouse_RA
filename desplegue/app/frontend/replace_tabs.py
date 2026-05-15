import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old block for Tab 2
old_tab2 = """elif active_tab == "tab2":
    st.header("🔍 Identificación de Discrepancias")
    st.info("Top 200 proyectos en Staging que no han sido migrados al DWH (Fact o Dim Proyectos).")
    
    source_map = {
        "SUIA (Proyectos v2)": "stg.suia_coa_bi",
        "JBPM (Histórico)": "stg.jbpm_sector_bi",
        "RCOA (Especial)": "stg.suia_rcoa_bi"
    }
    sel_source = st.selectbox("Seleccione Fuente de Datos", list(source_map.keys()))
    
    df_disc = load_discrepancies(source_map[sel_source])
    if not df_disc.empty:
        st.success(f"Se encontraron {len(df_disc)} proyectos pendientes de migración.")
        st.dataframe(df_disc, use_container_width=True)
    else:
        st.info("Sin discrepancias detectadas para esta fuente.")"""

# Define the old block for Tab 3
old_tab3 = """elif active_tab == "tab3":
    st.header("📁 Validación de Proyectos")
    df_origin = load_projects_by_origin_summary()
    if not df_origin.empty:
        st.subheader("Distribución de Proyectos por Sistema de Origen")
        fig_origin = px.pie(df_origin, values='cantidad_proyectos', names='origen', 
                            title="Proyectos por Fuente", hole=.4,
                            color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_origin, use_container_width=True)
        st.dataframe(df_origin, use_container_width=True)
    else:
        st.info("No hay datos de proyectos para mostrar.")"""

# Define the new blocks
new_tab2 = """elif active_tab == "tab2":
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

new_tab3 = """elif active_tab == "tab3":
    st.header("📁 Validador y Verificación de Proyectos")
    st.info("Funcionalidad de Consulta: Ingrese el código de proyecto para acceder a su trazabilidad completa.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_codigo = st.text_input("Código de Proyecto", help="Ejemplo: MAAE-SUIA-RA-DPAT-2022-XXXX")
    with col2:
        st.write("")
        st.write("")
        btn_search = st.button("🔍 Buscar Proyecto", use_container_width=True, type="primary")
        
    if search_codigo and btn_search:
        df_proj = load_management_summary(start_date_in, end_date_in, codigo_proyecto=search_codigo)
        if not df_proj.empty:
            st.success(f"Proyecto Encontrado: {df_proj['nombre_proyecto'].iloc[0]}")
            st.subheader("Resumen de Gestión")
            st.dataframe(df_proj.T, use_container_width=True)
            
            st.subheader("Historial de Trámites y Tareas")
            df_hist = load_project_history(search_codigo)
            if not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True)
            else:
                st.info("No hay historial de tareas para este proyecto.")
                
            st.subheader("Registro de Pagos Asociados")
            df_pay = load_project_payments(search_codigo)
            if not df_pay.empty:
                st.dataframe(df_pay, use_container_width=True)
            else:
                st.info("No hay pagos registrados para este proyecto.")
        else:
            st.error("Proyecto no encontrado en el Data Warehouse. Verifique el código e intente nuevamente.")"""

if old_tab2 in content and old_tab3 in content:
    content = content.replace(old_tab2, new_tab2)
    content = content.replace(old_tab3, new_tab3)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("FAILED TO FIND TARGET BLOCKS")
    # Imprime un poco para ver por qué falla
    print("old_tab2 in content:", old_tab2 in content)
    print("old_tab3 in content:", old_tab3 in content)
