
import sqlalchemy as sa

def run_cleanup():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    try:
        with open('d:/Datawrehouse_RA/cleanup_chemical_orphans.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        with engine.connect() as conn:
            conn.execute(sa.text(sql))
            print("Cleanup successful.")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    run_cleanup()
