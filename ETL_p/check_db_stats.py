import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connections import get_connection
from config import CONN_DWH_LOCAL

with get_connection(CONN_DWH_LOCAL) as conn:
    with conn.cursor() as cur:
        cur.execute("""SELECT schemaname, relname,
                              n_live_tup, n_dead_tup,
                              last_vacuum, last_autovacuum,
                              last_analyze,
                              pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) as size
                       FROM pg_stat_user_tables
                       WHERE schemaname IN ('dw','stg')
                       ORDER BY n_dead_tup DESC NULLS LAST LIMIT 15""")
        print('TABLA | LIVE | DEAD | LAST_VACUUM | SIZE')
        for r in cur.fetchall():
            print(f'{r[0]}.{r[1]:<40} live={r[2]:>8,} dead={r[3]:>8,} vac={str(r[4])[:10] if r[4] else "nunca":>12} {r[7]:>10}')

        cur.execute("SELECT version()")
        print('\nPG VERSION:', cur.fetchone()[0][:70])

        cur.execute("SELECT name, setting FROM pg_settings WHERE name IN ('autovacuum','autovacuum_vacuum_threshold','autovacuum_analyze_threshold','autovacuum_vacuum_scale_factor','autovacuum_vacuum_cost_delay','maintenance_work_mem','max_connections','shared_buffers')")
        print('\nSETTINGS:')
        for r in cur.fetchall(): print(f'  {r[0]:<45}: {r[1]}')

        cur.execute("SELECT pg_size_pretty(pg_database_size('dw_reg_v1'))")
        print('\nDB SIZE:', cur.fetchone()[0])

        cur.execute("SELECT COUNT(*) FROM pg_stat_activity WHERE state='active' AND datname='dw_reg_v1'")
        print('ACTIVE CONNECTIONS:', cur.fetchone()[0])
