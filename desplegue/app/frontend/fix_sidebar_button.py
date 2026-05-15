import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_css = """st.sidebar.markdown(f'''
<style>
div[data-testid="stSidebar"] .stButton > button {{
    background-color: #E74C3C !important;
    color: white !important;
    border: none !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 20px;
}}
div[data-testid="stSidebar"] .stButton > button:hover {{
    background-color: #C0392B !important;
    color: white !important;
}}
</style>
''', unsafe_allow_html=True)"""

new_css = """st.sidebar.markdown(f'''
<style>
/* Forzar estilo del botón de cerrar sesión por todos los selectores posibles */
[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: #E74C3C !important;
    border: 1px solid #C0392B !important;
    border-radius: 8px !important;
    padding: 10px !important;
    margin-bottom: 20px !important;
}}
[data-testid="stSidebar"] button[kind="secondary"] p,
[data-testid="stSidebar"] button[kind="secondary"] span,
[data-testid="stSidebar"] button[kind="secondary"] div {{
    color: #FFFFFF !important;
    font-weight: bold !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background-color: #C0392B !important;
    border: 1px solid #FFFFFF !important;
}}
</style>
''', unsafe_allow_html=True)"""

if old_css in content:
    content = content.replace(old_css, new_css)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("CSS block not found!")
