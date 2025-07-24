import os
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import Flask, render_template
from flask_cors import CORS
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# Extensions
from smartscripts.extensions import db, login_manager, mail, migrate, celery
from smartscripts.config import config_by_name

# Your DB engine/session helper (new file)
from smartscripts.database import get_engine, get_session

# Load environment variables
load_dotenv()

csrf = CSRFProtect()
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    UPLOAD_FOLDER_GUIDES = os.path.join(os.path.join(basedir, 'static', 'uploads'), 'marking_guides')
    UPLOAD_FOLDER_RUBRICS = os.path.join(os.path.join(basedir, 'static', 'uploads'), 'rubrics')
    UPLOAD_FOLDER_ANSWERS = os.path.join(os.path.join(basedir, 'static', 'uploads'), 'answered_scripts')
    UPLOAD_FOLDER_SUBMISSIONS = os.path.join(os.path.join(basedir, 'static', 'uploads'), 'student_scripts')


def create_app(config_name='default'):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Setup logging before anything else
    setup_logging(app)

    # Load and update configuration
    app.config.from_object(config_by_name[config_name])
    app.config.from_object(BaseConfig)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', app.config.get('SECRET_KEY', 'your-default-secret-key'))

    # Initialize extensions
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)

    # CORS
    if config_name == 'development':
        CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
    else:
        CORS(app, supports_credentials=True)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Ensure upload folders exist
    create_upload_folders(app)

    # Initialize DB engine and session with logging
    try:
        engine = get_engine(config_name)
        session = get_session(engine)
        app.db_engine = engine
        app.db_session = session
        app.logger.info("Database engine and session initialized successfully.")
    except Exception as e:
        app.logger.error(f"Failed to initialize database engine/session: {e}")
        traceback.print_exc()

    # Import models and register blueprints here to avoid circular imports
    from smartscripts.models import User
    from smartscripts.app.auth import auth_bp
    from smartscripts.app.main import main_bp
    from smartscripts.app.teacher.routes import teacher_bp
    from smartscripts.app.student import student_bp
    from smartscripts.app.teacher.routes.file_routes import file_routes_bp

    # Register blueprints with appropriate URL prefixes
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(file_routes_bp, url_prefix='/teacher/files')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Auto-run migrations in development
    if app.config.get("ENV") == "development":
        run_alembic_migrations(app)

    # Register error handlers
    register_error_handlers(app)

    # Global context processor
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.utcnow().year}

    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        from smartscripts.models import Test, StudentSubmission
        return {'db': db, 'Test': Test, 'StudentSubmission': StudentSubmission}

    app.logger.info("Application startup complete.")
    return app


def create_upload_folders(app):
    folders = [
        app.config['UPLOAD_FOLDER'],
        app.config['UPLOAD_FOLDER_GUIDES'],
        app.config['UPLOAD_FOLDER_RUBRICS'],
        app.config['UPLOAD_FOLDER_ANSWERS'],
        app.config['UPLOAD_FOLDER_SUBMISSIONS'],
    ]
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as e:
            app.logger.error(f"Failed to create upload folder {folder}: {e}")


def run_alembic_migrations(app):
    try:
        ini_path = os.path.abspath(os.path.join(app.root_path, '..', '..', 'alembic.ini'))
        alembic_cfg = Config(ini_path)
        command.upgrade(alembic_cfg, 'head')
        app.logger.info("Database migrated successfully.")
    except Exception as e:
        app.logger.error(f"Alembic migration failed: {e}")
        traceback.print_exc()


def setup_logging(app):
    app.logger.setLevel(logging.DEBUG)

    if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        stream_handler.setFormatter(stream_formatter)
        app.logger.addHandler(stream_handler)

    logs_dir = app.config.get('LOG_DIR', os.path.abspath(os.path.join(app.root_path, '..', 'logs')))
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, 'app.log')

    if not any(isinstance(h, RotatingFileHandler) for h in app.logger.handlers):
        file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        file_handler.setFormatter(file_formatter)
        app.logger.addHandler(file_handler)

    app.logger.debug("Debug logging enabled.")
    app.logger.info(f"Logging initialized. Writing logs to {log_path}")


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500
