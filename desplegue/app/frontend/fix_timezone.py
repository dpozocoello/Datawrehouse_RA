import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                        # Ensure timestamps
                        df_hist['fecha_inicio_tarea'] = pd.to_datetime(df_hist['fecha_inicio_tarea'])
                        df_hist['fecha_fin_tarea'] = pd.to_datetime(df_hist['fecha_fin_tarea'])"""

new_block = """                        # Ensure timestamps (Force timezone removal to prevent tz-naive vs tz-aware subtraction errors)
                        df_hist['fecha_inicio_tarea'] = pd.to_datetime(df_hist['fecha_inicio_tarea'], utc=True).dt.tz_localize(None)
                        df_hist['fecha_fin_tarea'] = pd.to_datetime(df_hist['fecha_fin_tarea'], utc=True).dt.tz_localize(None)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("SUCCESS")
else:
    print("FAILED")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
