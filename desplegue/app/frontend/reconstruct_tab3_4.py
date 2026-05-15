import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# RECONSTRUCCIÓN TAB 3 & 4
tab3_4_logic = """
elif active_tab == "tab3":
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
        st.info("No hay datos de proyectos para mostrar.")

elif active_tab == "tab4":
    st.header("🌎 Análisis Geográfico")
    st.info("Visualización de carga de procesos por ubicación política (Provincia/Cantón).")
    # Nota: Aquí irían los mapas si el código previo los cargaba. 
    # Por ahora restauramos la tabla resumen.
    st.subheader("Reporte de Actividad por Periodo")
    df_period = load_origin_period_report(start_date_in, end_date_in)
    if not df_period.empty:
        st.success(f"Se han identificado {len(df_period)} procesos en el rango seleccionado.")
        st.dataframe(df_period, use_container_width=True)
    else:
        st.warning("No se encontraron procesos en el rango de fechas especificado.")
"""

# Inyectar después de tab2
if 'elif active_tab == "tab2":' in content:
    content = content.replace('# ... (Continuar con el resto de tabs)', tab3_4_logic + "\n# ... (Continuar con el resto de tabs)")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
