import subprocess
import os
import datetime
import pandas as pd

def run_script(script_path):
    print(f"\n>>> Ejecutando: {os.path.basename(script_path)}")
    try:
        if script_path.endswith('.py'):
            result = subprocess.run(['python', script_path], capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
                return True, result.stdout
            else:
                print(f"Error en script: {result.stderr}")
                return False, result.stderr
        elif script_path.endswith('.sql'):
            print(f"Ejecutando consultas SQL en {script_path}...")
            # Leer SQL y ejecutarlo contra la DB
            with open(script_path, 'r', encoding='latin-1') as f:
                sql_content = f.read()
            
            import psycopg2
            import pandas as pd
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(host="localhost", database="dw_reg_v1", user="postgres", password="postgres", client_encoding="utf8")
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # El archivo dq_checks.sql contiene múltiples SELECTs
            # Los ejecutamos uno por uno (separados por ;)
            queries = [q.strip() for q in sql_content.split(';') if q.strip()]
            all_results = []
            for q in queries:
                if q.lower().startswith('select'):
                    cur.execute(q)
                    res = cur.fetchall()
                    all_results.extend(res)
            
            cur.close()
            conn.close()
            
            # Guardar resultados de DQ
            dq_output = "d:\\Datawrehouse_RA\\qa_rg_v1_01\\reports\\dq_results.csv"
            pd.DataFrame(all_results).to_csv(dq_output, index=False)
            print(f"Resultados de DQ guardados en: {dq_output}")
            return True, str(all_results)
            
    except Exception as e:
        print(f"Exception en {script_path}: {e}")
        return False, str(e)

def main():
    print("="*50)
    print("QA RUNNER - DASHBOARD RG v1.01")
    print(f"Inicio: {datetime.datetime.now()}")
    print("="*50)
    
    scripts_dir = "d:\\Datawrehouse_RA\\qa_rg_v1_01\\scripts"
    scripts_to_run = [
        os.path.join(scripts_dir, "data_profiler.py"),
        os.path.join(scripts_dir, "reconciliation.py"),
        os.path.join(scripts_dir, "timeliness_check.py"),
        os.path.join(scripts_dir, "dq_checks.sql")
    ]
    
    summary = []
    for script in scripts_to_run:
        success, output = run_script(script)
        summary.append({
            "script": os.path.basename(script),
            "status": "SUCCESS" if success else "FAILED"
        })
    
    print("\n" + "="*50)
    print("RESUMEN DE EJECUCIÓN")
    print("="*50)
    for s in summary:
        print(f"{s['script']}: {s['status']}")
    print("="*50)
    print(f"Fin: {datetime.datetime.now()}")
    
    # Crear archivo de log final
    with open("d:\\Datawrehouse_RA\\qa_rg_v1_01\\reports\\execution_log.txt", 'w') as f:
        f.write(f"QA Execution Log - {datetime.datetime.now()}\n")
        f.write("-" * 30 + "\n")
        for s in summary:
            f.write(f"{s['script']}: {s['status']}\n")

if __name__ == "__main__":
    main()
