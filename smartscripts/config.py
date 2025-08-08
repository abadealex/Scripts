import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base project directory (assumed smartscripts/smartscripts/app)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # points to smartscripts root

# Base upload folder inside static
UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

# Upload subfolders (your desired Smartscripts structure)
ANSWERED_SCRIPTS_FOLDER = UPLOAD_FOLDER / 'answered_scripts'
AUDIT_LOG_FOLDER = UPLOAD_FOLDER / 'audit_logs'
CLASS_LISTS_FOLDER = UPLOAD_FOLDER / 'class_lists'  # deprecated, keep for backward compatibility
COMBINED_SCRIPTS_FOLDER = UPLOAD_FOLDER / 'combined_scripts'
EXTRACTED_FOLDER = UPLOAD_FOLDER / 'extracted'
FEEDBACK_FOLDER = UPLOAD_FOLDER / 'feedback'
MANIFEST_FOLDER = UPLOAD_FOLDER / 'manifests'
MARKED_FOLDER = UPLOAD_FOLDER / 'marked'
MARKING_GUIDE_FOLDER = UPLOAD_FOLDER / 'marking_guides'
QUESTION_PAPER_FOLDER = UPLOAD_FOLDER / 'question_papers'
RESOURCES_FOLDER = UPLOAD_FOLDER / 'resources'
RUBRIC_FOLDER = UPLOAD_FOLDER / 'rubrics'
STUDENT_LIST_FOLDER = UPLOAD_FOLDER / 'student_lists'  # preferred over class_lists
STUDENT_SCRIPTS_FOLDER = UPLOAD_FOLDER / 'student_scripts'  # optional
SUBMISSIONS_FOLDER = UPLOAD_FOLDER / 'submissions'
TMP_FOLDER = UPLOAD_FOLDER / 'tmp'
EXPORTS_FOLDER = UPLOAD_FOLDER / 'exports'

# Nested resource folders (optional)
RESOURCE_IMAGES = RESOURCES_FOLDER / 'images'
RESOURCE_CODE = RESOURCES_FOLDER / 'code'
RESOURCE_DATASETS = RESOURCES_FOLDER / 'datasets'

# Question paper rubrics subfolder (optional)
QUESTION_PAPER_RUBRICS = QUESTION_PAPER_FOLDER / 'rubrics'

# Logging folder and file
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'app.log'


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set!")

    DEBUG = False
    TESTING = False
    ENABLE_SUBMISSIONS = os.getenv('ENABLE_SUBMISSIONS', 'True').lower() in ['true', '1', 'yes']
    WTF_CSRF_ENABLED = False

    # Upload folders
    UPLOAD_FOLDER = UPLOAD_FOLDER
    ANSWERED_SCRIPTS_FOLDER = ANSWERED_SCRIPTS_FOLDER
    AUDIT_LOG_FOLDER = AUDIT_LOG_FOLDER
    CLASS_LISTS_FOLDER = CLASS_LISTS_FOLDER
    COMBINED_SCRIPTS_FOLDER = COMBINED_SCRIPTS_FOLDER
    EXTRACTED_FOLDER = EXTRACTED_FOLDER
    FEEDBACK_FOLDER = FEEDBACK_FOLDER
    MANIFEST_FOLDER = MANIFEST_FOLDER
    MARKED_FOLDER = MARKED_FOLDER
    MARKING_GUIDE_FOLDER = MARKING_GUIDE_FOLDER
    QUESTION_PAPER_FOLDER = QUESTION_PAPER_FOLDER
    QUESTION_PAPER_RUBRICS = QUESTION_PAPER_RUBRICS
    RESOURCES_FOLDER = RESOURCES_FOLDER
    RESOURCE_IMAGES = RESOURCE_IMAGES
    RESOURCE_CODE = RESOURCE_CODE
    RESOURCE_DATASETS = RESOURCE_DATASETS
    RUBRIC_FOLDER = RUBRIC_FOLDER
    STUDENT_LIST_FOLDER = STUDENT_LIST_FOLDER
    STUDENT_SCRIPTS_FOLDER = STUDENT_SCRIPTS_FOLDER
    SUBMISSIONS_FOLDER = SUBMISSIONS_FOLDER
    TMP_FOLDER = TMP_FOLDER
    EXPORTS_FOLDER = EXPORTS_FOLDER

    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    # Logging
    LOG_DIR = LOG_DIR
    LOG_FILE = LOG_FILE

    # Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CoGrader', MAIL_USERNAME)

    # AI API Keys and models
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    TROCR_MODEL = os.getenv('TROCR_MODEL', 'microsoft/trocr-base-handwritten')
    GPT_MODEL = os.getenv('GPT_MODEL', 'gpt-4')

    # Celery config
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def init_upload_dirs(cls):
        # Create all required directories on startup
        required_dirs = [
            cls.UPLOAD_FOLDER,
            cls.ANSWERED_SCRIPTS_FOLDER,
            cls.AUDIT_LOG_FOLDER,
            cls.CLASS_LISTS_FOLDER,
            cls.COMBINED_SCRIPTS_FOLDER,
            cls.EXTRACTED_FOLDER,
            cls.FEEDBACK_FOLDER,
            cls.MANIFEST_FOLDER,
            cls.MARKED_FOLDER,
            cls.MARKING_GUIDE_FOLDER,
            cls.QUESTION_PAPER_FOLDER,
            cls.QUESTION_PAPER_RUBRICS,
            cls.RESOURCES_FOLDER,
            cls.RESOURCE_IMAGES,
            cls.RESOURCE_CODE,
            cls.RESOURCE_DATASETS,
            cls.RUBRIC_FOLDER,
            cls.STUDENT_LIST_FOLDER,
            cls.STUDENT_SCRIPTS_FOLDER,
            cls.SUBMISSIONS_FOLDER,
            cls.TMP_FOLDER,
            cls.EXPORTS_FOLDER,
            cls.LOG_DIR,
        ]
        for folder in required_dirs:
            folder.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'dev.sqlite3'}")
    BaseConfig.init_upload_dirs()


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL must be set in production!")
    BaseConfig.init_upload_dirs()


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    BaseConfig.init_upload_dirs()


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
