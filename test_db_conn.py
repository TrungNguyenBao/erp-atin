
import psycopg2
try:
    # Test connection to local postgres (default port 5432)
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
                password=pwd
            )
            print(f"Connected to default postgres on 5432 with user {user} and password {pwd}")
            conn.close()
            break
        except Exception as e:
            print(f"Failed with user {user}, password {pwd}: {e}")
except Exception as e:
    print(f"Failed to connect to 5432: {e}")

try:
    # Test connection to atin-retail postgres (port 5434)
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="retail_vision",
        user="postgres",
        password=None
    )
    print("Connected to retail-postgres on 5434")
    conn.close()
except Exception as e:
    print(f"Failed to connect to 5434: {e}")
