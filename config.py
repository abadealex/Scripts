import os
from dotenv import load_dotenv

# Load environment variables from .env (for local development only)
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # General
    SECRET_KEY = os.getenv('SECRET_KEY')

    # TEMP DEBUG: Check if SECRET_KEY is loaded properly
    print(f"[DEBUG] SECRET_KEY starts with: {SECRET_KEY[:6] + '...' if SECRET_KEY else 'None'}")

    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable not set!")

    # Logging
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')  # Central place for logs

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders (local paths; ephemeral on some platforms)
    UPLOAD_FOLDER_GUIDES = os.path.join(BASE_DIR, 'uploads', 'guides')    # Teacher uploads
    UPLOAD_FOLDER_ANSWERS = os.path.join(BASE_DIR, 'uploads', 'answers')  # Student uploads
    UPLOAD_FOLDER_MARKED = os.path.join(BASE_DIR, 'uploads', 'marked')    # AI-marked output

    # Upload settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size

    # Email settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CoGrader', MAIL_USERNAME)

    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("[WARNING] MAIL_USERNAME or MAIL_PASSWORD not set. Email sending may fail.")

    # Flags (can be overridden in subclasses)
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


# Configuration mapping for use in Flask app
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
