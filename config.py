import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # General
    SECRET_KEY = os.getenv('SECRET_KEY', 'thisissecret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders for each document type
    UPLOAD_FOLDER_GUIDES = os.path.join(BASE_DIR, 'uploads', 'guides')    # Teacher uploads
    UPLOAD_FOLDER_ANSWERS = os.path.join(BASE_DIR, 'uploads', 'answers')  # Student uploads
    UPLOAD_FOLDER_MARKED = os.path.join(BASE_DIR, 'uploads', 'marked')    # AI-marked output

    # Upload settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Email (Phase 3: optional results delivery)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CoGrader', os.getenv('MAIL_USERNAME'))

    # Debugging flags
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    DEBUG = True

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
