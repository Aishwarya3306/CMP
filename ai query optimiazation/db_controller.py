import psycopg2

conn = psycopg2.connect(
    dbname="ai_query_optimiazation",
    user="postgres",
    password="Aish1311",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

query_text = "SELECT * FROM students WHERE marks > 90;"
cursor.execute("EXPLAIN ANALYZE " + query_text)
plan = cursor.fetchall()
plan_text = " ".join(row[0] for row in plan)

if "Seq Scan" in plan_text:
    print("BAD QUERY detected")
    print("SUGGESTED FIX: CREATE INDEX ON students(marks);")
else:
    print("Query is already optimized")

cursor.close()
conn.close()
