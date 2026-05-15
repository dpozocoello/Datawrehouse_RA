import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

legal_ux_func = """
def render_legal_framework_info():
    with st.expander("📚 Información Legal y Normativa Aplicable (Jerarquía)", expanded=False):
        st.markdown('''
        **Resumen de Jerarquía Legal Gubernamental**
        
        | Acrónimo / Referencia | Nombre Formal del Cuerpo Legal |
        | :--- | :--- |
        | **COA** | Código Orgánico del Ambiente |
        | **RCOA** | Reglamento al Código Orgánico del Ambiente |
        | **A.M. 061** | Reforma al Libro VI del TULSMA |
        | **A.M. 028** | Catálogo de Actividades Sujetas a Regularización |
        | **D.E. 1215** | Reglamento Ambiental de Hidrocarburos |
        
        ---
        
        **1. JBPM_HIDRO: Módulo de Hidrocarburos**
        Se rige principalmente por la normativa técnica ambiental para actividades hidrocarburíferas.
        * **Nombre Formal**: Reglamento Ambiental para las Actividades Hidrocarburíferas (RAAH).
        * **Normativa**: Decreto Ejecutivo 1215. Es la norma específica que regula el control de contaminación ambiental en la fase de prospección, explotación, transporte e industrialización de hidrocarburos.
        
        **2. JBPM_SECTOR: Sector/Subsector A.M. 028**
        Este código hace referencia a la clasificación de actividades según el impacto.
        * **Nombre Formal**: Sustitución del Texto Unificado de Legislación Secundaria del Ministerio del Ambiente (TULSMA), Libro VI.
        * **Normativa**: Acuerdo Ministerial No. 028. Es el instrumento que establece el Catálogo Nacional de Actividades Sujetas a Regularización Ambiental y los criterios para determinar si un proyecto requiere Licencia, Registro o Certificado Ambiental.
        
        **3. JBPM_4CAT: Las 4 Categorías**
        En la normativa ecuatoriana, los proyectos se categorizan según su impacto ambiental para determinar el tipo de permiso.
        * **Nombre Formal**: Categorización Ambiental Nacional. Las 4 Categorías son:
            - Impacto No Significativo: (Certificado Ambiental)
            - Bajo Impacto: (Registro Ambiental)
            - Mediano Impacto: (Licencia Ambiental)
            - Alto Impacto: (Licencia Ambiental)
        * **Normativa**: Definidas en el Código Orgánico del Ambiente (COA) y detalladas en el Acuerdo Ministerial 013 (que actualizó la tabla de categorización del AM 028).
        
        **4. COA / SUIA VERDE: A.M. 061**
        El SUIA (Sistema Único de Información Ambiental) es la plataforma donde se procesan estos trámites.
        * **Nombre Formal**: Reforma al Libro VI del Texto Unificado de Legislación Secundaria del Ministerio del Ambiente (TULSMA).
        * **Normativa**: Acuerdo Ministerial No. 061. Es la norma fundamental que operativiza el proceso de regularización, control y seguimiento ambiental en el país antes de la plena vigencia de todos los reglamentos del COA.
        
        **5. RCOA: Reglamento al Código Orgánico Ambiental**
        Es el cuerpo legal que detalla cómo aplicar lo que dice la ley principal (COA).
        * **Nombre Formal**: Reglamento al Código Orgánico del Ambiente.
        * **Normativa**: Decreto Ejecutivo No. 752. Este reglamento desarrolla los procedimientos administrativos para la regularización, gestión de residuos, reparación integral y sanciones.
        ''')

@st.cache_data(ttl=3600)
def get_unique_tramites():
    try:
        query = "SELECT DISTINCT proceso FROM dw.fact_regularizacion WHERE proceso IS NOT NULL AND proceso != '' ORDER BY proceso"
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + df['proceso'].tolist()
    except:
        return ["TODOS"]
"""

# Inject definitions
if "def render_legal_framework_info" not in content:
    content = content.replace("# --- INTERFAZ DE USUARIO ---", legal_ux_func + "\n# --- INTERFAZ DE USUARIO ---")
elif "def get_unique_tramites" not in content:
    content = content.replace("def render_legal_framework_info():", "@st.cache_data(ttl=3600)\ndef get_unique_tramites():\n    try:\n        query = \"SELECT DISTINCT proceso FROM dw.fact_regularizacion WHERE proceso IS NOT NULL AND proceso != '' ORDER BY proceso\"\n        df = pd.read_sql(query, get_engine())\n        return [\"TODOS\"] + df['proceso'].tolist()\n    except:\n        return [\"TODOS\"]\n\ndef render_legal_framework_info():")

# Render legal info in Tab 1
if 'st.header("📊 Resumen de Integridad - DWH")' in content and 'render_legal_framework_info()' not in content.split('active_tab == "tab2"')[0]:
    content = content.replace('st.header("📊 Resumen de Integridad - DWH")', 'st.header("📊 Resumen de Integridad - DWH")\n    render_legal_framework_info()')

# Render legal info in Tab 2
if 'st.header("🔍 Orígenes de los Proyectos según Normativa")' in content:
    content = content.replace('st.header("🔍 Orígenes de los Proyectos según Normativa")', 'st.header("🔍 Orígenes de los Proyectos según Normativa")\n    render_legal_framework_info()')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS REPAIRS AND UX INJECTION")
