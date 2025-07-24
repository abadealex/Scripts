import logging
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from smartscripts.config import config_by_name  # <--- correct import here

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("db_connection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_engine(env='default'):
    try:
        db_uri = config_by_name[env].SQLALCHEMY_DATABASE_URI
        if not db_uri:
            raise ValueError(f"Database URI not set for environment '{env}'")

        engine = create_engine(
            db_uri,
            echo=False,
            pool_pre_ping=True,
            connect_args={"sslmode": "require"}  # This ensures SSL is used
        )
        logging.info(f"Connected to DB successfully: {db_uri}")
        return engine
    except Exception as e:
        logging.error(f"Failed to connect to DB: {e}")
        raise

def get_session(engine):
    try:
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        logging.error(f"Failed to create DB session: {e}")
        raise
