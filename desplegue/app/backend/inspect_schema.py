from sqlalchemy import create_engine, inspect
import sys
import os
import pandas as pd
from ETL_p.config import CONN_DWH_LOCAL

uri = f'postgresql://{CONN_DWH_LOCAL["user"]}:{CONN_DWH_LOCAL["password"]}@{CONN_DWH_LOCAL["host"]}:{CONN_DWH_LOCAL["port"]}/{CONN_DWH_LOCAL["database"]}'
engine = create_engine(uri)
inspector = inspect(engine)

def get_columns(schema, table):
    cols = inspector.get_columns(table, schema=schema)
    return ', '.join([f'{c["name"]}({c["type"]})' for c in cols])

data = []
for schema in ['dw', 'stg']:
    for table in inspector.get_table_names(schema=schema):
        data.append({
            'schema': schema,
            'table': table,
            'columns': get_columns(schema, table)
        })

df = pd.DataFrame(data)
print(df.to_string())
