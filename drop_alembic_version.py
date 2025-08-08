import psycopg2

# Connect to your Render-hosted PostgreSQL database using your actual credentials
conn = psycopg2.connect(
    host="dpg-d1dcl4p5pdvs73aljk6g-a.oregon-postgres.render.com",
    port=5432,
    dbname="sscripts_db",
    user="sscripts_db_user",
    password="y2DlVmMojK62dSc3fpPd2outKZ7Cpg8w"
)

cur = conn.cursor()

# Drop the Alembic version table
cur.execute("DROP TABLE IF EXISTS alembic_version;")
conn.commit()

# Clean up
cur.close()
conn.close()

print("✅ Dropped alembic_version table successfully.")

