from sqlalchemy import create_engine, inspect
engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8')
inspector = inspect(engine)
print('--- dim_waste_generator ---')
for c in inspector.get_columns('dim_waste_generator', schema='dw'):
    print(c['name'], c['type'])
print('\n--- fact_waste_generation ---')
for c in inspector.get_columns('fact_waste_generation', schema='dw'):
    print(c['name'], c['type'])
