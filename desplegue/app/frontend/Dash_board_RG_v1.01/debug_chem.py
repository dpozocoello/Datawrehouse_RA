from sqlalchemy import create_engine, inspect
engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8')
inspector = inspect(engine)
print('--- fact_chemical_import ---')
for c in inspector.get_columns('fact_chemical_import', schema='dw'):
    print(c['name'], c['type'])
print('\n--- dim_chemical_substance ---')
for c in inspector.get_columns('dim_chemical_substance', schema='dw'):
    print(c['name'], c['type'])
print('\n--- fact_chemical_declaration ---')
for c in inspector.get_columns('fact_chemical_declaration', schema='dw'):
    print(c['name'], c['type'])
