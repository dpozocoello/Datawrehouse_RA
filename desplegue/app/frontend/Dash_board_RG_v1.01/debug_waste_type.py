from sqlalchemy import create_engine, inspect
engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8')
inspector = inspect(engine)
print('--- dim_waste_type ---')
for c in inspector.get_columns('dim_waste_type', schema='dw'):
    print(c['name'], c['type'])
