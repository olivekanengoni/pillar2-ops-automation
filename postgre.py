import psycopg2

conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="KtJKUtJKNwtCtvBepUAgkFsYbwpwMFXV",
    host="postgres-production-6ff9.up.railway.app",
    port=5432
)
cursor = conn.cursor()
cursor.execute("SELECT 1;")
print(cursor.fetchone())
conn.close()
