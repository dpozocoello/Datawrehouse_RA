
import sqlalchemy as sa
import pandas as pd

def full_audit():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        "dw.fact_chemical_import",
        "dw.fact_chemical_movement",
        "dw.fact_chemical_declaration"
    ]
    for table in tables:
        query = f"""
        SELECT 
            (sk_proyecto = 0) as is_orphan,
            count(*) as count,
            sum(CASE WHEN sk_proyecto != 0 THEN 1 ELSE 0 END) as linked,
            sum(CASE WHEN sk_proyecto = 0 THEN 1 ELSE 0 END) as orphan
        FROM {table}
        GROUP BY 1;
        """
        try:
            df = pd.read_sql(query, engine)
            print(f"\nAudit for {table}:")
            print(df)
        except Exception as e:
            print(f"Error auditing {table}: {e}")

if __name__ == "__main__":
    full_audit()
