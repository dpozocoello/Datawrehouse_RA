import time
import pandas as pd
from sqlalchemy import create_engine
from environmental_engine import load_environmental_analytic_data

# Configuration
DB_URL = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
engine = create_engine(DB_URL)

def run_performance_test():
    print("--- INICIANDO PRUEBA DE RENDIMIENTO: MÓDULO GEOPOLÍTICO ---")
    
    # 1. Medir carga de datos real
    start_time = time.time()
    df = load_environmental_analytic_data(engine)
    load_time = time.time() - start_time
    print(f"Carga de datos (Query + Pre-procesamiento): {load_time:.4f} s")
    print(f"Registros recuperados: {len(df)}")

    if df.empty:
        print("Dataset vacío. Generando datos sintéticos para prueba de estrés...")
        # Simulación de 50,000 registros si el DB está vacío o es muy pequeño
        df = pd.DataFrame({
            'codigo_proyecto': [f'PROJ-{i}' for i in range(50000)],
            'prioridad': [1, 2, 3, 4, 5] * 10000,
            'superficie_proyecto': [10.5 * i for i in range(50000)],
            'categoria_ambiental': ['🛡️ SNAP'] * 10000 + ['🔒 ZONAS INTANGIBLES'] * 10000 + 
                                   ['🌳 BOSQUES PROTECTORES'] * 10000 + ['🌲 PATRIMONIO FORESTAL'] * 10000 + 
                                   ['⚪ SIN INTERSECCIÓN'] * 10000
        })

    # 2. Medir ordenamiento jerárquico (Punto crítico de KeyError corregido)
    start_sort = time.time()
    df_sorted = df.sort_values(by=["prioridad", "superficie_proyecto"], ascending=[True, False])
    sort_time = time.time() - start_sort
    print(f"Ordenamiento Jerárquico (5 columnas): {sort_time:.4f} s")

    # 3. Medir filtrado dinámico (Simulación de cambio de categoría)
    start_filter = time.time()
    df_filtered = df[df['categoria_ambiental'] != '⚪ SIN INTERSECCIÓN']
    filter_time = time.time() - start_filter
    print(f"Filtrado de Intersecciones (Exclusión): {filter_time:.4f} s")

    # 4. Medir Agrupación para Gráficos
    start_agg = time.time()
    df_agg = df_filtered.groupby('provincia').size() if 'provincia' in df_filtered.columns else df_filtered.groupby('categoria_ambiental').size()
    agg_time = time.time() - start_agg
    print(f"Agrupación para Gráficos (Top 10): {agg_time:.4f} s")

    print("\n--- RESUMEN ---")
    total_processing = sort_time + filter_time + agg_time
    print(f"Total Procesamiento Frontend (Pandas): {total_processing:.4f} s")
    print("ESTADO: OPTIMIZADO" if total_processing < 0.5 else "ESTADO: REQUIERE INDEXACIÓN")

if __name__ == "__main__":
    run_performance_test()
