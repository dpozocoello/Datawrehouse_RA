import os
import pandas as pd
import datetime
import json
import csv

def scan_sources(root_dir):
    inventory = []
    extensions = ['.csv', '.xlsx', '.json', '.parquet', '.sql']
    
    for root, dirs, files in os.walk(root_dir):
        # Excluir carpetas irrelevantes
        if any(exc in root for exc in ['.venv', '.git', 'qa_rg_v1_01']):
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                path = os.path.join(root, file)
                try:
                    stats = os.stat(path)
                    size_kb = stats.st_size / 1024
                    mtime = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Basic profiling
                    row_count = 0
                    cols = []
                    
                    if ext == '.csv':
                        try:
                            df = pd.read_csv(path, nrows=5, encoding='latin-1')
                            cols = df.columns.tolist()
                            with open(path, 'rb') as f:
                                row_count = sum(1 for _ in f) - 1
                        except:
                            pass
                    elif ext == '.xlsx':
                        try:
                            # Solo leer columnas para rapidez, conteo de filas opcional
                            xl = pd.ExcelFile(path)
                            cols = pd.read_excel(path, nrows=1).columns.tolist()
                            row_count = "N/A (Large File)"
                            # Si no es gigante, intentar contar
                            if stats.st_size < 10 * 1024 * 1024:
                                df_xl = pd.read_excel(path, usecols=[0])
                                row_count = len(df_xl)
                        except:
                            pass
                    elif ext == '.json':
                        try:
                            with open(path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if isinstance(data, list):
                                    row_count = len(data)
                                    if row_count > 0 and isinstance(data[0], dict):
                                        cols = list(data[0].keys())
                                elif isinstance(data, dict):
                                    row_count = 1
                                    cols = list(data.keys())
                        except:
                            pass
                    
                    inventory.append({
                        'FullName': path,
                        'FileName': file,
                        'Ext': ext,
                        'Size_KB': f"{size_kb:.2f}",
                        'LastWriteTime': mtime,
                        'EstimatedRows': row_count,
                        'ColumnsDetected': "|".join(cols[:10]) + ("..." if len(cols) > 10 else "")
                    })
                except Exception as e:
                    print(f"Error procesando {path}: {e}")
                    
    return inventory

if __name__ == "__main__":
    ROOT = "d:\\Datawrehouse_RA"
    OUTPUT = os.path.join(ROOT, "qa_rg_v1_01", "scripts", "sources_inventory.csv")
    
    print(f"Iniciando escaneo en {ROOT}...")
    results = scan_sources(ROOT)
    
    if results:
        df_inv = pd.DataFrame(results)
        df_inv.to_csv(OUTPUT, index=False, quoting=csv.QUOTE_ALL)
        print(f"Inventario generado exitosamente en: {OUTPUT}")
        print(f"Total de archivos detectados: {len(results)}")
    else:
        print("No se detectaron archivos de fuente.")
