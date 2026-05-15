"""
inspect_dw_schema.py
Muestra las columnas reales de las tablas dw.dim_* y dw.fact_* en dw_otrs.
Ejecutar: python d:\DashboardRA\inspect_dw_schema.py
"""
import sys
sys.path.insert(0, r"d:\dashboard_otrsV1")

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(r"d:\dashboard_otrsV1") / "env" / ".env")

from sqlalchemy import create_engine, text
import os

DB_URL = (
    "postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}".format(
        user=os.getenv("DB_USER", "postgres"),
        pwd =os.getenv("DB_PASS", "postgres"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432"),
        db  =os.getenv("DB_NAME", "dw_otrs"),
    )
)
engine = create_engine(DB_URL, pool_pre_ping=True)

SQL_COLS = text("""
    SELECT table_name, column_name, data_type
    FROM   information_schema.columns
    WHERE  table_schema = 'dw'
      AND  table_name   IN ('fact_ticket','dim_date','dim_queue',
                            'dim_state','dim_priority','dim_agent',
                            'dim_customer','dim_type')
    ORDER  BY table_name, ordinal_position
""")

print("=" * 65)
print("Columnas del esquema dw en dw_otrs")
print("=" * 65)

current_table = None
with engine.connect() as conn:
    for r in conn.execute(SQL_COLS):
        if r.table_name != current_table:
            current_table = r.table_name
            print(f"\n── {current_table} ──────────────────────────────────")
        print(f"   {r.column_name:35s}  {r.data_type}")
