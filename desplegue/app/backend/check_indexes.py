
import sqlalchemy as sa
import pandas as pd

def check_indexes():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    query = """
    SELECT
        t.relname as table_name,
        i.relname as index_name,
        a.attname as column_name
    FROM
        pg_class t,
        pg_class i,
        pg_index ix,
        pg_attribute a
    WHERE
        t.oid = ix.indrelid
        AND i.oid = ix.indexrelid
        AND a.attrelid = t.oid
        AND a.attnum = ANY(ix.indkey)
        AND t.relkind = 'r'
        AND t.relname IN ('dim_proponente', 'dim_proyecto', 'fact_regularizacion')
    ORDER BY
        t.relname,
        i.relname;
    """
    df = pd.read_sql(query, engine)
    print(df)

if __name__ == "__main__":
    check_indexes()
