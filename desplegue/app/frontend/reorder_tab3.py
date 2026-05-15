import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the 'Resumen de Gestion' DataFrame to rename column 0
old_df_t = """            st.subheader("Resumen de Gestión")
            st.dataframe(df_proj.T, use_container_width=True)"""

new_df_t = """            st.subheader("Resumen de Gestión")
            st.dataframe(df_proj.T.rename(columns={0: "Detalle Extendido"}), use_container_width=True)"""

if old_df_t in content:
    content = content.replace(old_df_t, new_df_t)
    print("SUCCESS: Renamed T dataframe columns")
else:
    print("FAILED TO RENAME DF PROJ T")

# 2. Extract and move 'Registro de Pagos Asociados' block above Visualizadores
# The structure is:
# st.info("No hay historial de tareas para este proyecto.")
# # --- VISUALIZADORES AVANZADOS (Flujo y Gantt) ---
# ...
# st.subheader("Registro de Pagos Asociados")
# ...

# We will replace the entire block from "st.info("No hay historial...")" to the end of Tab 3
old_tab_3 = """            else:
                st.info("No hay historial de tareas para este proyecto.")

            # --- VISUALIZADORES AVANZADOS (Flujo y Gantt) ---
            if not df_hist.empty:
                st.markdown("---")
                col_g, col_f = st.columns(2)
                with col_g:
                    with st.expander("📊 Diagrama de Gantt (Trazabilidad Temporal)", expanded=False):
                        # Ensure timestamps (Force timezone removal to prevent tz-naive vs tz-aware subtraction errors)
                        df_hist['fecha_inicio_tarea'] = pd.to_datetime(df_hist['fecha_inicio_tarea'], utc=True).dt.tz_localize(None)
                        df_hist['fecha_fin_tarea'] = pd.to_datetime(df_hist['fecha_fin_tarea'], utc=True).dt.tz_localize(None)
                        if 'usuario_tarea' not in df_hist.columns:
                            df_hist['usuario_tarea'] = 'Sistema'
                            
                        fig_gantt = px.timeline(df_hist, x_start="fecha_inicio_tarea", x_end="fecha_fin_tarea", 
                                                y="tarea", color="estado_proceso", hover_name="usuario_tarea",
                                                title="Línea de Vida del Proyecto")
                        fig_gantt.update_yaxes(autorange="reversed")
                        st.plotly_chart(fig_gantt, use_container_width=True)
                        
                with col_f:
                    with st.expander("🔄 Diagrama de Flujo Analítico (BPMN / Bizagi Style)", expanded=False):
                        flow = 'digraph BizagiProcess {\\n'
                        flow += 'rankdir=TB;\\n'
                        flow += 'bgcolor="transparent";\\n'
                        flow += 'splines=ortho;\\n'
                        flow += 'nodesep=0.5;\\n'
                        flow += 'node [fontname="Segoe UI, sans-serif"];\\n'
                        flow += 'edge [color="#2C3E50", penwidth=1.5, arrowsize=0.8];\\n'
                        
                        # [BPMN] Evento de Inicio (Círculo verde delgado)
                        flow += 'start_event [shape=circle, style=filled, fillcolor="#D5F5E3", color="#2ECC71", penwidth=2, label="Inicio", width=0.6, height=0.6];\\n'
                        
                        for i in range(len(df_hist)):
                            row = df_hist.iloc[i]
                            task_id = f"n{i}"
                            t_name = str(row['tarea']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            estado = str(row['estado_proceso']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            
                            f_ini = row['fecha_inicio_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_inicio_tarea']) else 'N/A'
                            f_fin = row['fecha_fin_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_fin_tarea']) else 'En Proceso'
                            
                            # Paleta de Colores Bizagi BPM
                            t_upper = t_name.upper()
                            if any(k in t_upper for k in ['PAGO', 'LIQUIDACION', 'FACTURA', 'COMPROB', 'TRANSF', 'FINAN', 'ORDEN_PAGO', 'REGISTRO PAGO']):
                                bg_color = "#E8F8F5" # Fondo menta muy claro
                                border_color = "#1ABC9C" # Borde esmeralda oscuro
                                font_color = "#117A65"
                            elif estado.upper() in ['RECHAZADO', 'ANULADO', 'ARCHIVADO']:
                                bg_color = "#FDEDEC" # Fondo rosa pastel
                                border_color = "#E74C3C" # Borde rojo puro
                                font_color = "#922B21"
                            else:
                                bg_color = "#EBF5FB" # Fondo azul cielo (Default Bizagi Activity)
                                border_color = "#2980B9" # Borde azul corporativo
                                font_color = "#154360"
                                
                            html_label = f'''<
                            <table border="0" cellborder="0" cellspacing="0" cellpadding="2">
                              <tr><td align="center"><b><font point-size="11" color="{font_color}">{t_name}</font></b></td></tr>
                              <tr><td align="center"><font point-size="9" color="#7F8C8D">[{estado}]</font></td></tr>
                              <tr><td align="center"><font point-size="8" color="#95A5A6">{f_ini} ➔ {f_fin}</font></td></tr>
                            </table>
                            >'''
                            
                            # [BPMN] Actividad (Rectángulo redondeado claro con doble borde colorido)
                            flow += f'{task_id} [shape=box, style="rounded,filled", fillcolor="{bg_color}", color="{border_color}", penwidth=1.5, label={html_label}, margin="0.2,0.1"];\\n'
                            
                        # [BPMN] Evento de Fin (Círculo rojo grueso)
                        flow += 'end_event [shape=circle, style=filled, fillcolor="#FADBD8", color="#E74C3C", penwidth=3, label="Fin", width=0.6, height=0.6];\\n'
                            
                        # Enrutamiento y Conexiones Ortogonales
                        if len(df_hist) > 0:
                            flow += 'start_event -> n0;\\n'
                            for i in range(len(df_hist)-1):
                                flow += f'n{i} -> n{i+1};\\n'
                            flow += f'n{len(df_hist)-1} -> end_event;\\n'
                        else:
                            flow += 'start_event -> end_event;\\n'
                            
                        flow += '}'
                        st.graphviz_chart(flow)
                
            st.subheader("Registro de Pagos Asociados")
            df_pay = load_project_payments(search_codigo)
            if not df_pay.empty:
                st.dataframe(df_pay, use_container_width=True)
            else:
                st.info("No hay pagos registrados para este proyecto.")
        else:
            st.error("Proyecto no encontrado en el Data Warehouse. Verifique el código e intente nuevamente.")"""

new_tab_3 = """            else:
                st.info("No hay historial de tareas para este proyecto.")

            st.markdown("---")
            st.subheader("Registro de Pagos Asociados")
            df_pay = load_project_payments(search_codigo)
            if not df_pay.empty:
                st.dataframe(df_pay, use_container_width=True)
            else:
                st.info("No hay pagos registrados para este proyecto.")

            # --- VISUALIZADORES AVANZADOS (Flujo y Gantt) ---
            if not df_hist.empty:
                st.markdown("---")
                col_g, col_f = st.columns(2)
                with col_g:
                    with st.expander("📊 Diagrama de Gantt (Trazabilidad Temporal)", expanded=False):
                        # Ensure timestamps (Force timezone removal to prevent tz-naive vs tz-aware subtraction errors)
                        df_hist['fecha_inicio_tarea'] = pd.to_datetime(df_hist['fecha_inicio_tarea'], utc=True).dt.tz_localize(None)
                        df_hist['fecha_fin_tarea'] = pd.to_datetime(df_hist['fecha_fin_tarea'], utc=True).dt.tz_localize(None)
                        if 'usuario_tarea' not in df_hist.columns:
                            df_hist['usuario_tarea'] = 'Sistema'
                            
                        fig_gantt = px.timeline(df_hist, x_start="fecha_inicio_tarea", x_end="fecha_fin_tarea", 
                                                y="tarea", color="estado_proceso", hover_name="usuario_tarea",
                                                title="Línea de Vida del Proyecto")
                        fig_gantt.update_yaxes(autorange="reversed")
                        st.plotly_chart(fig_gantt, use_container_width=True)
                        
                with col_f:
                    with st.expander("🔄 Diagrama de Flujo Analítico (BPMN / Bizagi Style)", expanded=False):
                        flow = 'digraph BizagiProcess {\\n'
                        flow += 'rankdir=TB;\\n'
                        flow += 'bgcolor="transparent";\\n'
                        flow += 'splines=ortho;\\n'
                        flow += 'nodesep=0.5;\\n'
                        flow += 'node [fontname="Segoe UI, sans-serif"];\\n'
                        flow += 'edge [color="#2C3E50", penwidth=1.5, arrowsize=0.8];\\n'
                        
                        # [BPMN] Evento de Inicio (Círculo verde delgado)
                        flow += 'start_event [shape=circle, style=filled, fillcolor="#D5F5E3", color="#2ECC71", penwidth=2, label="Inicio", width=0.6, height=0.6];\\n'
                        
                        for i in range(len(df_hist)):
                            row = df_hist.iloc[i]
                            task_id = f"n{i}"
                            t_name = str(row['tarea']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            estado = str(row['estado_proceso']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            
                            f_ini = row['fecha_inicio_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_inicio_tarea']) else 'N/A'
                            f_fin = row['fecha_fin_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_fin_tarea']) else 'En Proceso'
                            
                            # Paleta de Colores Bizagi BPM
                            t_upper = t_name.upper()
                            if any(k in t_upper for k in ['PAGO', 'LIQUIDACION', 'FACTURA', 'COMPROB', 'TRANSF', 'FINAN', 'ORDEN_PAGO', 'REGISTRO PAGO']):
                                bg_color = "#E8F8F5" # Fondo menta muy claro
                                border_color = "#1ABC9C" # Borde esmeralda oscuro
                                font_color = "#117A65"
                            elif estado.upper() in ['RECHAZADO', 'ANULADO', 'ARCHIVADO']:
                                bg_color = "#FDEDEC" # Fondo rosa pastel
                                border_color = "#E74C3C" # Borde rojo puro
                                font_color = "#922B21"
                            else:
                                bg_color = "#EBF5FB" # Fondo azul cielo (Default Bizagi Activity)
                                border_color = "#2980B9" # Borde azul corporativo
                                font_color = "#154360"
                                
                            html_label = f'''<
                            <table border="0" cellborder="0" cellspacing="0" cellpadding="2">
                              <tr><td align="center"><b><font point-size="11" color="{font_color}">{t_name}</font></b></td></tr>
                              <tr><td align="center"><font point-size="9" color="#7F8C8D">[{estado}]</font></td></tr>
                              <tr><td align="center"><font point-size="8" color="#95A5A6">{f_ini} ➔ {f_fin}</font></td></tr>
                            </table>
                            >'''
                            
                            # [BPMN] Actividad (Rectángulo redondeado claro con doble borde colorido)
                            flow += f'{task_id} [shape=box, style="rounded,filled", fillcolor="{bg_color}", color="{border_color}", penwidth=1.5, label={html_label}, margin="0.2,0.1"];\\n'
                            
                        # [BPMN] Evento de Fin (Círculo rojo grueso)
                        flow += 'end_event [shape=circle, style=filled, fillcolor="#FADBD8", color="#E74C3C", penwidth=3, label="Fin", width=0.6, height=0.6];\\n'
                            
                        # Enrutamiento y Conexiones Ortogonales
                        if len(df_hist) > 0:
                            flow += 'start_event -> n0;\\n'
                            for i in range(len(df_hist)-1):
                                flow += f'n{i} -> n{i+1};\\n'
                            flow += f'n{len(df_hist)-1} -> end_event;\\n'
                        else:
                            flow += 'start_event -> end_event;\\n'
                            
                        flow += '}'
                        st.graphviz_chart(flow)
        else:
            st.error("Proyecto no encontrado en el Data Warehouse. Verifique el código e intente nuevamente.")"""

if old_tab_3 in content:
    content = content.replace(old_tab_3, new_tab_3)
    print("SUCCESS: UI Block layout repositioned perfectly.")
else:
    print("FAILED TO MOVE PAYMENT BLOCK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
