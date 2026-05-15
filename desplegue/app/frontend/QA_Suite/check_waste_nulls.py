import pandas as pd
from sqlalchemy import create_engine
import sys

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dwh_bi')
    query = "SELECT COUNT(*) as null_count FROM dw.fact_waste_generation WHERE quantity_generated IS NULL"
    df = pd.read_sql(query, engine)
    
    with open('waste_null_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"Conteo de Nulos en quantity_generated: {df['null_count'].iloc[0]}\n")
        
    print(f"Resultado guardado en waste_null_report.txt: {df['null_count'].iloc[0]}")
except Exception as e:
    with open('waste_null_error.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
    print(f"Error detectado y guardado en waste_null_error.txt")
