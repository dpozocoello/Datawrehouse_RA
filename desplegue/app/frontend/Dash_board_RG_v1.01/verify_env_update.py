import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os

# Añadir el directorio al path para importar el environmental_engine
sys.path.append(r'd:\DashboardRA\Dash_board_RG_v1.01')
from environmental_engine import load_environmental_analytic_data

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def verify_categorization():
    engine = get_engine()
    print("--- Verificando Categorización Ambiental Actualizada ---")
    
    try:
        df = load_environmental_analytic_data(engine)
        if not df.empty:
            summary = df['categoria_ambiental'].value_counts()
            print("\nResumen de Categorías:")
            print(summary.to_string())
            
            print("\nEjemplos de cada categoría:")
            for cat in df['categoria_ambiental'].unique():
                sample = df[df['categoria_ambiental'] == cat].head(1)
                print(f"\nCategoría: {cat}")
                print(f"Proyecto: {sample['nombre_proyecto'].iloc[0]}")
                print(f"Áreas: {sample['areas_protegidas'].iloc[0]}")
        else:
            print("No se obtuvieron datos.")
    except Exception as e:
        print(f"Error en verificación: {e}")

if __name__ == "__main__":
    verify_categorization()
