import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_flow_block = """                    with st.expander("🔄 Diagrama de Flujo (Procesal)", expanded=False):
                        flow = "digraph Process {\\n"
                        flow += "node [shape=box, style=filled, color=\\\"#0A3D62\\\", fontcolor=white];\\n"
                        # Generate nodes
                        for i in range(len(df_hist)-1):
                            t1 = str(df_hist.iloc[i]['tarea']).replace('"', '')
                            t2 = str(df_hist.iloc[i+1]['tarea']).replace('"', '')
                            flow += f'"{t1}" -> "{t2}";\\n'
                        flow += "}"
                        st.graphviz_chart(flow)"""

new_flow_block = """                    with st.expander("🔄 Diagrama de Flujo (Procesal Avanzado - BPM)", expanded=False):
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

if old_flow_block in content:
    content = content.replace(old_flow_block, new_flow_block)
    print("SUCCESS: Graphviz Diagram Rebuilt")
else:
    print("FAILED TO FIND FLOW BLOCK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
