"""
deploy_etl_sync_views.py
========================
Despliega las vistas ctl.v_etl_sync_status y ctl.v_etl_last_run_summary
en la base de datos dw_otrs.

Ejecutar desde la raíz del proyecto:
    python deploy_etl_sync_views.py
"""
import sys
import os

# ── Añadir la raíz del dashboard al path ────────────────────────────────────
DASHBOARD_ROOT = r"d:\dashboard_otrsV1"
sys.path.insert(0, DASHBOARD_ROOT)

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv(Path(DASHBOARD_ROOT) / "env" / ".env")

from core.db import get_engine

SQL_FILE = Path(DASHBOARD_ROOT) / "core" / "sql" / "etl_sync_view.sql"

def main():
    print("=" * 60)
    print("Desplegando vistas de sincronización ETL en dw_otrs...")
    print("=" * 60)

    engine = get_engine()

    with open(SQL_FILE, encoding="utf-8") as f:
        sql_raw = f.read()

    # Separar en statements individuales (ignorar comentarios puros)
    statements = []
    for stmt in sql_raw.split(";"):
        cleaned = stmt.strip()
        if cleaned and not all(line.startswith("--") for line in cleaned.splitlines() if line.strip()):
            statements.append(cleaned)

    errors = []
    with engine.begin() as conn:
        for stmt in statements:
            preview = stmt[:80].replace("\n", " ")
            try:
                conn.execute(text(stmt))
                print(f"  ✔  {preview}...")
            except Exception as e:
                print(f"  ✘  {preview}...")
                print(f"     ERROR: {e}")
                errors.append(str(e))

    print()
    if errors:
        print(f"⚠️  Completado con {len(errors)} advertencia(s).")
    else:
        print("✅  Vistas desplegadas exitosamente.")

    # ── Verificación rápida ──────────────────────────────────────────────────
    print()
    print("── Verificando ctl.v_etl_sync_status ──")
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT tabla, descripcion,
                       ultima_fecha_dato::TEXT AS fecha,
                       registros_totales
                FROM   ctl.v_etl_sync_status
                WHERE  tabla IN ('fact_ticket', 'dim_date')
                ORDER  BY tabla
            """)).fetchall()
            if rows:
                for r in rows:
                    m = dict(r._mapping)
                    print(f"  {m['tabla']:20s} | {m['fecha'] or 'NULL':12s} | {m['registros_totales']:>10,} regs")
            else:
                print("  (sin filas — las tablas dw.fact_ticket / dw.dim_date pueden estar vacías)")
    except Exception as e:
        print(f"  ERROR en verificación: {e}")

    print()
    print("── Verificando ctl.v_etl_last_run_summary ──")
    try:
        with engine.connect() as conn:
            r = conn.execute(text("""
                SELECT min_fecha_sincronizada::TEXT,
                       max_fecha_sincronizada::TEXT,
                       rango_dias,
                       total_registros_dw
                FROM   ctl.v_etl_last_run_summary
            """)).fetchone()
            if r:
                m = dict(r._mapping)
                print(f"  Min fecha : {m['min_fecha_sincronizada']}")
                print(f"  Max fecha : {m['max_fecha_sincronizada']}")
                print(f"  Rango días: {m['rango_dias']}")
                print(f"  Total regs: {m['total_registros_dw']:,}" if m['total_registros_dw'] else "  Total regs: N/A")
    except Exception as e:
        print(f"  ERROR en verificación: {e}")

    print()
    print("Done. Puedes iniciar el dashboard con: streamlit run app.py")


if __name__ == "__main__":
    main()
