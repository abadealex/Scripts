import psycopg2

conn = psycopg2.connect(
    host="dpg-d1dcl4p5pdvs73aljk6g-a.oregon-postgres.render.com",
    port=5432,
    dbname="sscripts_db",
    user="sscripts_db_user",
    password="y2DlVmMojK62dSc3fpPd2outKZ7Cpg8w"
)

cur = conn.cursor()

# Set a placeholder filename where it's null
cur.execute("""
    UPDATE student_submissions
    SET filename = 'placeholder.txt'
    WHERE filename IS NULL;
""")

conn.commit()
cur.close()
conn.close()

print("✅ All NULL filenames updated with placeholder.")

