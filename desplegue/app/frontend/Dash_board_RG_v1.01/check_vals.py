import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def check_intersections():
    engine = get_engine()
    with engine.connect() as conn:
        print("DISTINCT VALUES FOR interseccion_snap:")
        res = conn.execute(text("SELECT DISTINCT interseccion_snap FROM dw.fact_regularizacion"))
        for row in res:
            print(f"|{row[0]}|")

if __name__ == "__main__":
    check_intersections()
