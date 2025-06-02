import psycopg2

try:
    conn = psycopg2.connect(
        dbname='bank',
        user='postgres',
        password='1111',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("Connected to:", version)
    cur.close()
    conn.close()
except Exception as e:
    print("Connection failed:", e)
