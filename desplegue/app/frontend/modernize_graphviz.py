import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_flow_block = """                    with st.expander("🔄 Diagrama de Flujo (Procesal Avanzado - BPM)", expanded=False):
                        flow = 'digraph Process {\\n'
                        flow += 'rankdir=TB;\\n'
                        flow += 'node [shape=Mrecord, style="rounded,filled", fontname="Helvetica", fontsize=10];\\n'
                        
                        # Definir Nodos Parametrizados
                        for i in range(len(df_hist)):
                            row = df_hist.iloc[i]
                            task_id = f"n{i}"
                            t_name = str(row['tarea']).replace('"', "'")
                            estado = str(row['estado_proceso']).replace('"', "'")
                            
                            f_ini = row['fecha_inicio_tarea'].strftime('%Y-%m-%d %H:%M') if pd.notnull(row['fecha_inicio_tarea']) else 'N/A'
                            f_fin = row['fecha_fin_tarea'].strftime('%Y-%m-%d %H:%M') if pd.notnull(row['fecha_fin_tarea']) else 'N/A'
                            
                            label_content = f"{t_name}\\\\n[{estado}]\\\\nInicio: {f_ini}\\\\nFin: {f_fin}"
                            
                            # Coloreado Semántico (Detección de Pagos)
                            t_upper = t_name.upper()
                            if any(k in t_upper for k in ['PAGO', 'LIQUIDACION', 'FACTURA', 'COMPROB', 'TRANSF', 'FINAN', 'ORDEN_PAGO']):
                                bg_color = "#27AE60" # Emerald Green for Payments
                            else:
                                bg_color = "#0A3D62" # Navy Blue for Standard BPM Tasks
                                
                            flow += f'{task_id} [label="{label_content}", color="{bg_color}", fillcolor="{bg_color}", fontcolor="white"];\\n'
                            
                        # Conectar Aristas Secuenciales
                        for i in range(len(df_hist)-1):
                            flow += f'n{i} -> n{i+1} [color="#7f8c8d"];\\n'
                            
                        flow += '}'
                        st.graphviz_chart(flow)"""

new_flow_block = """                    with st.expander("🔄 Diagrama de Flujo Analítico (HD)", expanded=False):
                        flow = 'digraph Process {\\n'
                        flow += 'rankdir=TB;\\n'
                        flow += 'bgcolor="transparent";\\n'
                        flow += 'splines=ortho;\\n'
                        flow += 'nodesep=0.6;\\n'
                        flow += 'node [shape=box, style="rounded,filled", fontname="Segoe UI, sans-serif", penwidth=0, margin="0.2,0.1"];\\n'
                        flow += 'edge [color="#95a5a6", penwidth=2.5, arrowsize=0.8];\\n'
                        
                        # Definir Nodos Parametrizados (HTML-Like)
                        for i in range(len(df_hist)):
                            row = df_hist.iloc[i]
                            task_id = f"n{i}"
                            
                            # Limpieza de strings para evitar romper la sintaxis XML de Graphviz
                            t_name = str(row['tarea']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            estado = str(row['estado_proceso']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            
                            f_ini = row['fecha_inicio_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_inicio_tarea']) else 'N/A'
                            f_fin = row['fecha_fin_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_fin_tarea']) else 'En Proceso'
                            
                            # Coloreado Semántico Dinámico
                            t_upper = t_name.upper()
                            if any(k in t_upper for k in ['PAGO', 'LIQUIDACION', 'FACTURA', 'COMPROB', 'TRANSF', 'FINAN', 'ORDEN_PAGO']):
                                bg_color = "#27AE60" # Verde Esmeralda
                            elif estado.upper() in ['RECHAZADO', 'ANULADO', 'ARCHIVADO']:
                                bg_color = "#E74C3C" # Rojo Alerta
                            else:
                                bg_color = "#0A3D62" # Navy Institucional
                                
                            # Construcción de la etiqueta moderna en formato de Tabla HTML
                            html_label = f'''<
                            <table border="0" cellborder="0" cellspacing="0" cellpadding="2">
                              <tr><td align="center"><b><font point-size="12" color="white">{t_name}</font></b></td></tr>
                              <tr><td align="center"><font point-size="10" color="#ecf0f1">Estatus: {estado}</font></td></tr>
                              <tr><td align="center"><font point-size="9" color="#bdc3c7">{f_ini} ➔ {f_fin}</font></td></tr>
                            </table>
                            >'''
                            
                            flow += f'{task_id} [label={html_label}, fillcolor="{bg_color}"];\\n'
                            
                        # Conectar Aristas Secuenciales
                        for i in range(len(df_hist)-1):
                            flow += f'n{i} -> n{i+1};\\n'
                            
                        flow += '}'
                        st.graphviz_chart(flow)"""

if old_flow_block in content:
    content = content.replace(old_flow_block, new_flow_block)
    print("SUCCESS: Flowchart upgraded to Modern HTML-like Nodes.")
else:
    print("FAILED TO FIND TARGET BLOCK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
