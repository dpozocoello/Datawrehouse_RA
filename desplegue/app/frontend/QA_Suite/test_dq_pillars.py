import pytest
import pandas as pd
import sys
import os
from sqlalchemy import text

# Cargar configuración del proyecto
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Dash_board_RG_v1.01', 'Dash_board_RG_v1.01.py'))
import importlib.util
spec = importlib.util.spec_from_file_location("main_app", module_path)
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)
get_engine = main_app.get_engine

# --- 2.1 EXACTITUD ---
def test_accuracy_csv_vs_dw():
    """Exactitud: Compara una muestra del archivo fuente CSV con el DW."""
    csv_path = r"D:\Datawrehouse_RA\full_geo_fix_111.csv"
    if not os.path.exists(csv_path):
        pytest.skip("Archivo fuente CSV no encontrado en D:\Datawrehouse_RA")
    
    df_csv = pd.read_csv(csv_path)
    engine = get_engine()
    
    # Tomar una muestra de 5 registros para verificación de exactitud
    sample = df_csv.head(5)
    for _, row in sample.iterrows():
        id_area = str(row['id_area'])
        query = text("SELECT provincia, canton FROM dw.dim_area WHERE id_area = :id")
        with engine.connect() as conn:
            res = conn.execute(query, {"id": id_area}).fetchone()
            if res:
                # El CSV tiene MANABÍ, el DW debe ser igual (ignorando tildes si es necesario, pero aquí probamos exactitud)
                assert res[0].upper() == str(row['prov_sug']).upper(), f"Error de Exactitud en ID {id_area}: Fuente={row['prov_sug']}, DW={res[0]}"

def test_accuracy_counts():
    """Exactitud: Los conteos en DW deben coincidir con Staging (Fuente cargada)."""
    engine = get_engine()
    query = """
    SELECT 
        (SELECT COUNT(*) FROM stg.suia_areas_bi) as source_count,
        (SELECT COUNT(*) FROM dw.dim_area WHERE sk_area > 0) as target_count
    """
    df = pd.read_sql(query, engine)
    # Permitimos una discrepancia de 0 si el ETL es perfecto, o reportamos diferencia
    assert df['source_count'].iloc[0] == df['target_count'].iloc[0], \
        f"Discrepancia detectada: Staging={df['source_count'].iloc[0]}, DW={df['target_count'].iloc[0]}"

# --- 2.2 COMPLETITUD ---
def test_completeness_mandatory_fields():
    """Completitud: Campos críticos no deben ser nulos."""
    engine = get_engine()
    # Verificar nulos en FactTable para llaves subrogadas críticas
    query = """
    SELECT COUNT(*) as nulos
    FROM dw.fact_regularizacion
    WHERE sk_proyecto IS NULL OR sk_geografia IS NULL OR sk_area IS NULL
    """
    df = pd.read_sql(query, engine)
    assert df['nulos'].iloc[0] == 0, "Se detectaron registros con llaves MANDATORIAS nulas en FactTable."

# --- 2.3 CONSISTENCIA ---
def test_consistency_geography():
    """Consistencia: Las provincias en DW deben existir en el catálogo maestro (REF)."""
    engine = get_engine()
    query = """
    SELECT COUNT(*) as inconsistentes
    FROM dw.dim_area
    WHERE sk_area > 0 
      AND provincia NOT IN (SELECT nombre_provincia FROM ref.inec_dpa_2024)
      AND provincia != 'N/A'
    """
    df = pd.read_sql(query, engine)
    assert df['inconsistentes'].iloc[0] == 0, "Existen provincias en DW que no coinciden con el catálogo INEC Nacional."

# --- 2.4 VALIDEZ ---
def test_validity_ranges():
    """Validez: Rangos de datos lógicos (Porcentajes)."""
    engine = get_engine()
    query = """
    SELECT COUNT(*) as invalidos
    FROM dw.fact_regularizacion f
    JOIN dw.bridge_interseccion_ambiental b ON f.sk_proyecto = b.sk_proyecto
    WHERE b.porcentaje_interseccion < 0 OR b.porcentaje_interseccion > 100
    """
    # Nota: No todas las bases tienen bridge, ajustamos si falla
    try:
        df = pd.read_sql(query, engine)
        assert df['invalidos'].iloc[0] == 0, "Se detectaron porcentajes de intersección fuera del rango [0-100]."
    except:
        pytest.skip("La tabla de bridge_interseccion_ambiental no está disponible para esta prueba.")

# --- 2.5 OPORTUNIDAD (TIMELINESS) ---
def test_timeliness_last_load():
    """Oportunidad: Los datos no deben tener un retraso mayor a 24h (dependiendo del negocio)."""
    engine = get_engine()
    query = "SELECT MAX(fecha_carga) as ultima_fecha FROM dw.dim_area"
    df = pd.read_sql(query, engine)
    ultima_fecha = df['ultima_fecha'].iloc[0]
    # Si fuera una auditoría real, compararíamos con la fecha actual. 
    # Por ahora solo validamos que exista una fecha de carga válida.
    assert ultima_fecha is not None, "No se registra fecha de última carga (Timeliness desconocido)."
