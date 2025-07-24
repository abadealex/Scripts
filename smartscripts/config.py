import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project base directory
BASE_DIR = Path(__file__).resolve().parent

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}


class BaseConfig:
    # --- General ---
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set in the environment!")

    DEBUG = False
    TESTING = False
    ENABLE_SUBMISSIONS = os.getenv('ENABLE_SUBMISSIONS', 'True').lower() in ['true', '1', 'yes']

    # --- Logging ---
    LOG_DIR = Path(os.getenv('LOGS_DIR', BASE_DIR / 'logs'))
    LOG_FILE = LOG_DIR / 'app.log'

    # --- Upload Base Folder ---
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'  # Can be overridden in child configs

    # These will be finalized below
    UPLOAD_FOLDER_GUIDES = None
    UPLOAD_FOLDER_RUBRICS = None
    UPLOAD_FOLDER_ANSWERS = None
    UPLOAD_FOLDER_SUBMISSIONS = None
    UPLOAD_FOLDER_AUDIT_LOGS = None

    # --- File Settings ---
    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # --- Mail ---
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CoGrader', MAIL_USERNAME)

    # --- AI Keys ---
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    TROCR_MODEL = os.getenv('TROCR_MODEL', 'microsoft/trocr-base-handwritten')
    GPT_MODEL = os.getenv('GPT_MODEL', 'gpt-4')

    # --- Celery ---
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

    # --- SQLAlchemy ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def init_upload_dirs(cls):
        cls.UPLOAD_FOLDER_GUIDES = cls.UPLOAD_FOLDER / 'marking_guides'
        cls.UPLOAD_FOLDER_RUBRICS = cls.UPLOAD_FOLDER / 'rubrics'
        cls.UPLOAD_FOLDER_ANSWERS = cls.UPLOAD_FOLDER / 'answered_scripts'
        cls.UPLOAD_FOLDER_SUBMISSIONS = cls.UPLOAD_FOLDER / 'student_scripts'
        cls.UPLOAD_FOLDER_AUDIT_LOGS = cls.UPLOAD_FOLDER / 'audit_logs'

        for folder in [
            cls.UPLOAD_FOLDER,
            cls.UPLOAD_FOLDER_GUIDES,
            cls.UPLOAD_FOLDER_RUBRICS,
            cls.UPLOAD_FOLDER_ANSWERS,
            cls.UPLOAD_FOLDER_SUBMISSIONS,
            cls.UPLOAD_FOLDER_AUDIT_LOGS,
            cls.LOG_DIR,
        ]:
            folder.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'dev.sqlite3'}")

    # Custom path for dev uploads
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    BaseConfig.init_upload_dirs()


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL must be set in production!")

    # Use mounted Docker volume or external path
    UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', '/app/uploads'))
    BaseConfig.init_upload_dirs()


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Separate folder to isolate test artifacts
    UPLOAD_FOLDER = BASE_DIR / 'test_uploads'
    BaseConfig.init_upload_dirs()


# Config loader for app factory
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
