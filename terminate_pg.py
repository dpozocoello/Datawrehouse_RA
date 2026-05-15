
import sqlalchemy as sa

def terminate_pid(pid):
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    try:
        engine.execute(f"SELECT pg_terminate_backend({pid});")
        print(f"PID {pid} terminated.")
    except Exception as e:
        print(f"Error terminating PID {pid}: {e}")

if __name__ == "__main__":
    terminate_pid(22116)
