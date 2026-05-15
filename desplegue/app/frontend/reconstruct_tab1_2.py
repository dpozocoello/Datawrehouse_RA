import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# RECONSTRUCCIÓN TAB 1 & 2
tab1_logic = """
if active_tab == "tab1":
    st.header("📊 Resumen de Integridad - DWH")
    df_integrity = load_integrity_summary()
    if not df_integrity.empty:
        cols = st.columns(4)
        for i, row in df_integrity.iterrows():
            with cols[i % 4]:
                st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-label">{row['origen']}</div>
                    <div class="kpi-value">{row['cantidad_proyectos']:,}</div>
                    <div class="kpi-label">Proyectos Registrados</div>
                </div>
                ''', unsafe_allow_html=True)
        st.subheader("Detalle Cronológico por Origen")
        st.dataframe(df_integrity, use_container_width=True)
    else:
        st.warning("No se encontraron datos de integridad.")

elif active_tab == "tab2":
    st.header("🔍 Identificación de Discrepancias")
    st.info("Top 200 proyectos en Staging que no han sido migrados al DWH (Fact o Dim Proyectos).")
    
    source_map = {
        "SUIA (Proyectos v2)": "stg.suia_proyectos_all",
        "JBPM (Histórico)": "stg.jbpm_proyectos_all",
        "RCOA (Especial)": "stg.rcoa_proyectos_all"
    }
    sel_source = st.selectbox("Seleccione Fuente de Datos", list(source_map.keys()))
    
    df_disc = load_discrepancies(source_map[sel_source])
    if not df_disc.empty:
        st.success(f"Se encontraron {len(df_disc)} proyectos pendientes de migración.")
        st.dataframe(df_disc, use_container_width=True)
    else:
        st.info("Sin discrepancias detectadas para esta fuente.")
"""

# Inyectar después de la declaración de active_tab
if 'if active_tab == "tab1":' in content:
    import re
    # Reemplazar el bloque vacío de Tab 1
    content = re.sub(r'if active_tab == "tab1":.*?else:.*?break', tab1_logic, content, flags=re.DOTALL)
    # Nota: la regex anterior es delicada, usaré una más simple si falla.
    # Pero como yo escribí el reconstruct_v2, sé cómo se ve.
    content = content.replace('if active_tab == "tab1":\n    st.header("📊 Resumen de Integridad - DWH")\n    # Lógica de Tab 1...\nelif active_tab == "tab2":\n    st.header("🔍 Identificación de Discrepancias")\n    # Lógica de Tab 2...', tab1_logic)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
