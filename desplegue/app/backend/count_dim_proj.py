
import sqlalchemy as sa

def count_rows():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    try:
        with engine.connect() as conn:
            count = conn.execute(sa.text("SELECT count(*) FROM dw.dim_proyecto")).fetchone()[0]
            print(f"dim_proyecto count: {count}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_rows()
