import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_flow_block = """                    with st.expander("🔄 Diagrama de Flujo Analítico (HD)", expanded=False):
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

new_flow_block = """                    with st.expander("🔄 Diagrama de Flujo Analítico (BPMN / Bizagi Style)", expanded=False):
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
                        st.graphviz_chart(flow)"""

if old_flow_block in content:
    content = content.replace(old_flow_block, new_flow_block)
    print("SUCCESS: Bizagi Style BPMN applied to Flowchart")
else:
    print("FAILED TO FIND TARGET BLOCK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
