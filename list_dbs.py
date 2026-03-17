
import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="workboard",
        password="workboard"
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database;")
    dbs = cur.fetchall()
    print("Databases:")
    for db in dbs:
        print(f"- {db[0]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
