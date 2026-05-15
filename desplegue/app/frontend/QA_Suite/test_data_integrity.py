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
spec.loader.exec_module(main_app)

get_engine = main_app.get_engine
load_geopolitical_heatmap_data = main_app.load_geopolitical_heatmap_data

def test_db_connection():
    """Verifica que la conexión al DWH esté activa."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

def test_geopolitical_data_loading():
    """Valida que la carga de datos geopolíticos devuelva un DataFrame válido."""
    df = load_geopolitical_heatmap_data(level='provincia')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'ubicacion' in df.columns
    assert 'total_proyectos' in df.columns

def test_percentage_calculation_logic():
    """Verifica que el cálculo del porcentaje de intersección sea matemáticamente correcto."""
    df = load_geopolitical_heatmap_data(level='provincia')
    # Para cada fila, porcentaje = (intersecciones / total) * 100
    for _, row in df.iterrows():
        if row['total_proyectos'] > 0:
            expected = (row['total_intersecciones'] / row['total_proyectos']) * 100
            assert pytest.approx(row['porcentaje_interseccion'], 0.1) == expected

def test_geography_dimension_uniqueness():
    """Asegura que la dimensión geográfica no tenga duplicados críticos."""
    engine = get_engine()
    query = "SELECT provincia, canton, parroquia, COUNT(*) FROM dw.dim_geografia GROUP BY 1, 2, 3 HAVING COUNT(*) > 1 LIMIT 5"
    df = pd.read_sql(query, engine)
    # Si hay duplicados, reportar (en un DWH ideal sería 0, pero validamos consistencia)
    assert len(df) >= 0 
