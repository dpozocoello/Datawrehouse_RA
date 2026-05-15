import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_header_html = """        <div>
            <h1 style='margin:0; color:white; font-size: 2.2rem; letter-spacing: 1px;'>ECO-SIEAA</h1>
            <p class="header-subtitle" style='margin:0; font-size: 1rem;'>Ministerio de Ambiente y Energía - El Nuevo Ecuador</p>
            <p class="header-analyst" style='margin-top: 5px; font-size: 0.85rem;'>{st.session_state['user_data']['full_name']} | Intel-Environment Analyst</p>
        </div>"""

new_header_html = """        <div>
            <h1 style='margin:0; color:white; font-size: 2.2rem; letter-spacing: 1px;'>ECO-SIEAA</h1>
            <p class="header-subtitle" style='color: #0A3D62 !important; margin:0; font-size: 1.1rem; font-weight: 700;'>Ministerio de Ambiente y Energía - El Nuevo Ecuador</p>
            <p class="header-analyst" style='margin-top: 5px; font-size: 0.85rem;'>{st.session_state['user_data']['full_name']} | Intel-Environment Analyst</p>
        </div>"""

if old_header_html in content:
    content = content.replace(old_header_html, new_header_html)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("HTML FIX FAILED")
