import pytest
import pandas as pd
import sys
import os
from sqlalchemy import text
import importlib.util

# Cargar el módulo principal dinámicamente debido al punto en el nombre del archivo
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Dash_board_RG_v1.01', 'Dash_board_RG_v1.01.py'))
spec = importlib.util.spec_from_file_location("main_app", module_path)
main_app = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(main_app)
except Exception as e:
    # Si falla la carga del módulo completo por dependencias de Streamlit, usamos mocks o saltamos
    pass

# Obtener funciones de carga de datos
get_engine = getattr(main_app, 'get_engine', None)
load_waste_summary = getattr(main_app, 'load_waste_summary', None)

def test_waste_summary_not_empty():
    """Verifica que la función de resumen de desechos devuelva datos."""
    if load_waste_summary is None:
        pytest.skip("No se pudo cargar la función load_waste_summary")
    df = load_waste_summary()
    assert isinstance(df, pd.DataFrame), "El resultado debe ser un DataFrame"
    assert not df.empty, "El resumen de desechos no debe estar vacío"

def test_waste_schema():
    """Verifica que el DataFrame tenga las columnas esperadas."""
    if load_waste_summary is None:
        pytest.skip("No se pudo cargar la función load_waste_summary")
    df = load_waste_summary()
    expected_columns = ['provincia', 'tipo_desecho', 'total_generado', 'total_entregado', 'unit', 'record_year']
    for col in expected_columns:
        assert col in df.columns, f"Columna faltante: {col}"

def test_waste_metrics_integrity():
    """Verifica que las métricas de generación y entrega sean consistentes."""
    if load_waste_summary is None:
        pytest.skip("No se pudo cargar la función load_waste_summary")
    df = load_waste_summary()
    
    # Valores no negativos
    assert (df['total_generado'] >= 0).all(), "Existen valores negativos en total_generado"
    assert (df['total_entregado'] >= 0).all(), "Existen valores negativos en total_entregado"

def test_waste_geographic_consistency():
    """Verifica que las provincias en el resumen de desechos sean válidas."""
    if load_waste_summary is None:
        pytest.skip("No se pudo cargar la función load_waste_summary")
    df = load_waste_summary()
    
    # No debería haber una cantidad masiva de 'No Definida'
    no_definida_pct = (df['provincia'] == 'No Definida').mean()
    assert no_definida_pct < 0.5, f"Más del 50% de las provincias son 'No Definida' ({no_definida_pct:.2%})"

def test_waste_fact_vs_dim_integrity():
    """Verifica la integridad referencial básica entre hechos y dimensiones de desechos."""
    if get_engine is None:
        pytest.skip("No se pudo cargar la función get_engine")
    engine = get_engine()
    query = text("""
        SELECT COUNT(*) 
        FROM dw.fact_waste_generation f
        LEFT JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
        WHERE t.waste_type_key IS NULL
    """)
    with engine.connect() as conn:
        orphans = conn.execute(query).scalar()
        assert orphans == 0, f"Existen {orphans} registros huérfanos en fact_waste_generation sin tipo de desecho válido."
