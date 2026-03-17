
import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="workboard",
        password="workboard"
    )
    cur = conn.cursor()
    cur.execute("SELECT rolname, rolcreatedb FROM pg_roles WHERE rolname = 'workboard';")
    role = cur.fetchone()
    if role:
        print(f"Role: {role[0]}, Can Create DB: {role[1]}")
    else:
        print("Role 'workboard' not found in pg_roles")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
