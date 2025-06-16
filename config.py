import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # General
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable not set!")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders (local paths; note ephemeral on some hosts like Railway)
    UPLOAD_FOLDER_GUIDES = os.path.join(BASE_DIR, 'uploads', 'guides')    # Teacher uploads
    UPLOAD_FOLDER_ANSWERS = os.path.join(BASE_DIR, 'uploads', 'answers')  # Student uploads
    UPLOAD_FOLDER_MARKED = os.path.join(BASE_DIR, 'uploads', 'marked')    # AI-marked output

    # Upload settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Email settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CoGrader', MAIL_USERNAME)

    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("Warning: MAIL_USERNAME or MAIL_PASSWORD not set. Email sending may fail.")

    # Debug flags
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


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

"""
.env.example file sample you should add alongside your project root:

SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
MAIL_USERNAME=youremail@example.com
MAIL_PASSWORD=your-email-password

NOTE:
- On Railway or other ephemeral hosting, uploaded files saved to local disk (uploads/) may be lost on deploy/restart.
- Consider cloud storage (AWS S3, Railway Persistent Volumes) for production persistent uploads.
"""
