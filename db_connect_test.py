import logging
import psycopg2
from psycopg2 import OperationalError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("db_connection.log"),
        logging.StreamHandler()
    ]
)

conn_str = (
    "dbname=testdb user=user password=password "
    "host=dpg-d1dcl4p5pdvs73aljk6g-a.oregon-postgres.render.com "
    "port=5432 sslmode=require"
)

try:
            connection = psycopg2.connect(conn_str)
    logging.info("Database connection established successfully")
except OperationalError as e:
    logging.error(f"Database connection failed: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")

