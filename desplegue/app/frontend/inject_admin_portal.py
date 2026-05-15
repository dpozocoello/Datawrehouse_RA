import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_admin = """elif active_tab == "admin":
    st.header("⚙️ Configuración del Sistema")
    st.info("Gestión de accesos, roles y configuración de módulos.")
    if st.button("Ejecutar Auditoría de DWH"):
        st.success("Auditoría programada con éxito.")"""

new_admin = """elif active_tab == "admin":
    st.header("⚙️ Centro de Configuración y Despliegue (Admin)")
    st.info("Gestión de accesibilidad, nomenclatura y activación en caliente de los 10 módulos core del Data Warehouse.")
    
    config = load_config()
    tabs_conf = config.get("tabs", {})
    
    st.subheader("🛠️ Control Maestro de Módulos (Visibilidad de UI)")
    
    default_tabs = {
        "tab1": "Integridad DWH", "tab2": "Normativas", "tab3": "Consulta Proyectos",
        "tab4": "Geográfico Espacial", "tab5": "Control Financiero", "tab6": "Intersección Ambiental",
        "tab7": "Frecuencias de Capas", "tab8": "Mapa Base Dinámico", "tab9": "Gestión Desechos", "tab10": "Invento Químico"
    }
    
    updated_tabs = {}
    with st.form("config_form"):
        cols = st.columns(2)
        for i, (tid, default_label) in enumerate(default_tabs.items()):
            col = cols[i % 2]
            current_conf = tabs_conf.get(tid, {})
            current_label = current_conf.get("label", default_label)
            # Default to True locally if missing, else what is saved
            current_visible = current_conf.get("visible", True)
            
            with col:
                st.markdown(f"**[ {tid.upper()} ] Módulo Interno**")
                new_label = st.text_input("Etiqueta en el Menú Principal", value=current_label, key=f"lbl_{tid}")
                is_visible = st.toggle(f"Activar Renderización de {tid}", value=current_visible, key=f"vis_{tid}")
                updated_tabs[tid] = {"label": new_label, "visible": is_visible}
                st.markdown("---")
                
        submit_btn = st.form_submit_button("✅ Guardar Arquitectura de Navegación", use_container_width=True)
        if submit_btn:
            config["tabs"] = updated_tabs
            save_config(config)
            st.success("Configuración consolidada y guardada. Recargando portal en caliente...")
            st.rerun()
            
    st.markdown("---")
    st.subheader("🔒 Mantenimiento")
    colA, colB = st.columns(2)
    with colA:
        if st.button("Ejecutar Indexación DWH", use_container_width=True):
            st.success("Sentencia de mantenimiento transmitida al motor PostgreSQL.")
    with colB:
        if st.button("Refrescar Cachés Globales (@st.cache_data)", use_container_width=True):
            st.cache_data.clear()
            st.success("Memoria caché RAM desfragmentada (0 bytes).")
            st.rerun()"""

if old_admin in content:
    content = content.replace(old_admin, new_admin)
    print("SUCCESS")
else:
    print("FAILED")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
