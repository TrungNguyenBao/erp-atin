
import psycopg2
trials = [
    (None, 'postgres'),
    ('postgres', 'postgres'),
    ('workboard', 'workboard'),
    ('odoo', 'odoo'),
    ('admin', 'postgres')
]
for pwd, user in trials:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user=user,
            password=pwd,
            connect_timeout=2
        )
        print(f"SUCCESS: {user}:{pwd}")
        conn.close()
    except Exception as e:
        print(f"FAIL: {user}:{pwd} - {str(e)[:50]}")
