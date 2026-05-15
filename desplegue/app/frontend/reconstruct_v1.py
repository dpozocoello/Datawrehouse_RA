import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_mode = False
for line in lines:
    # 1. Inject design system at the top
    if 'st.set_page_config' in line:
        new_lines.append(line)
        new_lines.append("\n# --- ECO-SIEAA DESIGN SYSTEM ---\n")
        new_lines.append("apply_custom_theme()\n")
        new_lines.append("apply_global_frame()\n")
        continue
    
    # 2. Skip legacy CSS
    if '# --- ESTILOS CSS ---' in line:
        skip_mode = True
        continue
    if skip_mode and '""", unsafe_allow_html=True)' in line:
        skip_mode = False
        continue
    if skip_mode:
        continue

    # 3. Handle Header and Navigation
    if 'st.markdown(f"")' in line or '<div style="display: flex;' in line:
        # We'll just append it later when we reach the main loop
        pass

    new_lines.append(line)

# Now manually rebuild the navigation and main loop at the end of the file
# Since we know the file ends with Tab 10 logic (truncated)
# We will clean up the bottom and add the proper active_tab structure.

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
