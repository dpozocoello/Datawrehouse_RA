import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove LIMIT 5000 from SQL build logic
old_func_end = """        
    base_query += " ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC LIMIT 5000"
    return pd.read_sql(base_query, get_engine(), params=params)"""

new_func_end = """        
    base_query += " ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC"
    return pd.read_sql(base_query, get_engine(), params=params)"""

if old_func_end in content:
    content = content.replace(old_func_end, new_func_end)
    print("SUCCESS: Removed LIMIT 5000 from SQL builder")
else:
    print("FAILED 1")

# 2. Inject python-based visual pagination into UI tab2
old_ui_block = """    if st.button("Aplicar Filtros y Consultar", type="primary", use_container_width=True):
        with st.spinner("Consultando al Data Warehouse..."):
            df_norm = load_projects_advanced_filter(origen_val, sel_tramite, apply_dates, start_date_in, end_date_in)
            if not df_norm.empty:
                st.success(f"Se encontraron {len(df_norm)} proyectos coincidentes (mostrando máx. 5000).")
                st.dataframe(df_norm, use_container_width=True)
            else:
                st.warning("No se encontraron proyectos bajo los criterios seleccionados.")"""

new_ui_block = """    # Using session state to allow slider interaction without losing data
    if st.button("Aplicar Filtros y Consultar", type="primary", use_container_width=True):
        st.session_state['run_advanced_query'] = True
        
    if st.session_state.get('run_advanced_query', False):
        with st.spinner("Extrayendo volúmenes del Data Warehouse (Puede tardar unos segundos)..."):
            df_norm = load_projects_advanced_filter(origen_val, sel_tramite, apply_dates, start_date_in, end_date_in)
            if not df_norm.empty:
                total_records = len(df_norm)
                st.success(f"✅ Se encontraron **{total_records:,}** proyectos coincidentes. Toda la información ha sido cargada exitosamente.")
                
                # Estrategia de Paginación Frontend (Eficiencia en Renderizado del Navegador)
                page_size = 5000
                total_pages = (total_records // page_size) + (1 if total_records % page_size > 0 else 0)
                
                if total_pages > 1:
                    page = st.slider(f"Navegación Paginada (Visualizando bloques de {page_size:,} registros)", 1, total_pages, 1)
                    start_idx = (page - 1) * page_size
                    end_idx = start_idx + page_size
                    st.info(f"Mostrando registros {start_idx + 1:,} al {min(end_idx, total_records):,} (Página {page} de {total_pages})")
                    st.dataframe(df_norm.iloc[start_idx:end_idx], use_container_width=True)
                else:
                    st.dataframe(df_norm, use_container_width=True)
            else:
                st.warning("No se encontraron proyectos bajo los criterios seleccionados.")"""

if old_ui_block in content:
    content = content.replace(old_ui_block, new_ui_block)
    print("SUCCESS: Injected frontend pagination")
else:
    print("FAILED 2")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
