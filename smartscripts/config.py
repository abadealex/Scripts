import os
from dotenv import load_dotenv

# Load environment variables from .env for local development
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- General ---
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable not set!")

    print(f"[DEBUG] SECRET_KEY loaded: {SECRET_KEY[:6]}...")

    # --- Logging ---
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')

    # --- SQLAlchemy ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Uploads ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    UPLOAD_FOLDER_GUIDES = os.path.join(UPLOAD_FOLDER, 'guides')
    UPLOAD_FOLDER_ANSWERS = os.path.join(UPLOAD_FOLDER, 'answers')
    UPLOAD_FOLDER_MARKED = os.path.join(UPLOAD_FOLDER, 'marked')
    UPLOAD_FOLDER_RUBRICS = os.path.join(UPLOAD_FOLDER, 'rubrics')
    UPLOAD_FOLDER_BULK = os.path.join(UPLOAD_FOLDER, 'bulk')

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    # --- Mail ---
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CoGrader', MAIL_USERNAME)

    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("[WARNING] MAIL_USERNAME or MAIL_PASSWORD not set. Email features may fail.")

    # --- AI & API Keys ---
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    TROCR_MODEL = os.getenv('TROCR_MODEL', 'microsoft/trocr-base-handwritten')
    GPT_MODEL = os.getenv('GPT_MODEL', 'gpt-4')

    if not OPENAI_API_KEY:
        print("[WARNING] OPENAI_API_KEY not set. GPT features may not work.")
    if not HUGGINGFACE_API_KEY:
        print("[WARNING] HUGGINGFACE_API_KEY not set. TrOCR features may not work.")

    # --- Celery ---
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

    # --- Flags ---
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = False
    TESTING = False

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL environment variable not set for Production!")


# --- Flask configuration map ---
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
