import os
import shutil
import glob

def create_distribution():
    base_dir = "d:/Datawrehouse_RA"
    dist_dir = os.path.join(base_dir, "desplegue")
    db_dir = os.path.join(dist_dir, "db")
    install_dir = os.path.join(dist_dir, "install")
    backend_dist = os.path.join(dist_dir, "app", "backend")
    frontend_dist = os.path.join(dist_dir, "app", "frontend")

    # Create directories
    for d in [db_dir, install_dir, backend_dist, frontend_dist]:
        os.makedirs(d, exist_ok=True)

    print("--- Consolidando Base de Datos ---")
    ddl_file = os.path.join(base_dir, "ddl_dwh_completo_v1_9_5.sql")
    ref_file = os.path.join(base_dir, "setup_reference_data_v1_4.sql")
    output_db = os.path.join(db_dir, "01_install_db.sql")

    with open(output_db, "w", encoding="utf-8") as outfile:
        if os.path.exists(ddl_file):
            with open(ddl_file, "r", encoding="utf-8") as infile:
                outfile.write("-- ESTRUCTURA DDL --\n")
                outfile.write(infile.read())
                outfile.write("\n\n")
        
        if os.path.exists(ref_file):
            with open(ref_file, "r", encoding="utf-8") as infile:
                outfile.write("-- DATOS DE REFERENCIA Y CATALOGOS --\n")
                outfile.write(infile.read())
    
    print(f"Base de datos consolidada en: {output_db}")

    def copy_app(src, dst, ignore_patterns):
        if not os.path.exists(src):
            print(f"Advertencia: No se encontró la ruta {src}")
            return
        
        print(f"Copiando {src} a {dst}...")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore_patterns))

    # Backend Exclusions
    backend_ignore = [
        ".git", ".venv", ".venv_old", "backups", "log", "logs", 
        "desplegue", "__pycache__", "*.pyc", "*.log", "*.tmp",
        "pdi-ce-11.0.0.0-237.zip" # Exclude zip to avoid massive size, but add instructions
    ]
    
    # Frontend Exclusions
    frontend_ignore = [
        ".git", ".venv", "BACKUP_*", ".pytest_cache", "__pycache__", 
        "*.pyc", ".vscode", "Puerto"
    ]

    copy_app(base_dir, backend_dist, backend_ignore)
    copy_app("d:/DashboardRA", frontend_dist, frontend_ignore)

    print("\n--- Proceso de empaquetado completado ---")

if __name__ == "__main__":
    create_distribution()
