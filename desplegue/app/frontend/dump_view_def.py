from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def dump_view():
    q = "SELECT view_definition FROM information_schema.views WHERE table_schema = 'dw' AND table_name = 'v_dashboard_regularizacion'"
    with engine.connect() as conn:
        res = conn.execute(text(q)).fetchone()
        if res:
            with open('d:/DashboardRA/view_def.sql', 'w') as f:
                f.write(res[0])
            print("View definition saved to d:/DashboardRA/view_def.sql")
        else:
            print("View not found!")

if __name__ == "__main__":
    dump_view()
