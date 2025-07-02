import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local dev
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # General
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable not set!")

    # Debug info for SECRET_KEY load (trimmed)
    print(f"[DEBUG] SECRET_KEY loaded: {SECRET_KEY[:6]}...")

    # Logging
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')

    # SQLAlchemy config
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders
    UPLOAD_FOLDER_GUIDES = os.path.join(BASE_DIR, 'uploads', 'guides')
    UPLOAD_FOLDER_ANSWERS = os.path.join(BASE_DIR, 'uploads', 'answers')
    UPLOAD_FOLDER_MARKED = os.path.join(BASE_DIR, 'uploads', 'marked')
    UPLOAD_FOLDER_RUBRICS = os.path.join(BASE_DIR, 'uploads', 'rubrics')

    # Upload settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max

    # Email server settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CoGrader', MAIL_USERNAME)

    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("[WARNING] MAIL_USERNAME or MAIL_PASSWORD not set. Email sending may fail.")

    # AI-related environment keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

    if not OPENAI_API_KEY:
        print("[WARNING] OPENAI_API_KEY not set. Some AI features may not work.")

    if not HUGGINGFACE_API_KEY:
        print("[WARNING] HUGGINGFACE_API_KEY not set. Some AI features may not work.")

    # Flags (can be overridden)
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


# Flask config mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
