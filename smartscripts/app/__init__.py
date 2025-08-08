import os
import sys
import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, g, current_app
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

# Load .env before anything else
load_dotenv()

# Import extensions (no models here!)
from smartscripts.extensions import db, login_manager, mail, migrate, celery, configure_login_manager
from smartscripts.config import config_by_name
from smartscripts.database import get_engine, get_session

# Import blueprints (safe because they don’t pull models at import time)
from smartscripts.app.auth import auth_bp
from smartscripts.app.main import main_bp
from smartscripts.app.teacher import teacher_bp
from smartscripts.app.teacher.ai_marking_routes import ai_marking_bp
from smartscripts.app.teacher.analytics_routes import analytics_bp
from smartscripts.app.teacher.upload_routes import upload_bp
from smartscripts.app.student import student_bp
from smartscripts.app.admin.routes import admin_bp
from smartscripts.app.teacher.profile_routes import teacher_profile_bp

csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_by_name[config_name])

    # === UPLOAD FOLDER PATH ===
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, "static", "uploads")

    # Ensure upload dirs exist
    if hasattr(config_by_name[config_name], 'init_upload_dirs'):
        config_by_name[config_name].init_upload_dirs()

    # Secret key fallback
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-default-secret-key')

    # === EXTENSIONS INIT ===
    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)
    configure_login_manager(app)

    # === CORS ===
    if config_name == 'development':
        CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
    else:
        CORS(app, supports_credentials=True)

    # === LOGGING ===
    setup_logging(app)

    # === Upload subfolders ===
    create_upload_folders(app)

    # === DB Engine/Session ===
    try:
        engine = get_engine(config_name)
        session = get_session(engine)
        app.db_engine = engine
        app.db_session = session
        app.logger.info("DB engine and session initialized.")
    except Exception as e:
        app.logger.error(f"DB setup error: {e}")
        traceback.print_exc()

    @app.before_request
    def set_session():
        g.db_session = get_session(app.db_engine)

    @app.teardown_appcontext
    def cleanup_session(exception=None):
        session = g.pop('db_session', None)
        if session:
            try:
                if exception:
                    session.rollback()
                    app.logger.warning("DB session rolled back due to exception.")
                    app.logger.warning(traceback.format_exc())
                session.close()
            except Exception as e:
                app.logger.error(f"DB session cleanup error: {e}")
                traceback.print_exc()

    # === BLUEPRINTS ===
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ai_marking_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(teacher_profile_bp, url_prefix='/teacher/profile')

    # === USER LOADER ===
    from smartscripts.models.user import User  # import only here to avoid circular imports

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[load_user] DB error: {e}")
            return None

    # === Auto Alembic in Dev ===
    if app.config.get("ENV") == "development":
        run_alembic_migrations(app)

    # === ERROR HANDLERS ===
    register_error_handlers(app)

    # === CONTEXT PROCESSORS ===
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.utcnow().year}

    @app.shell_context_processor
    def make_shell_context():
        from smartscripts.models.test import Test
        from smartscripts.models.student_submission import StudentSubmission
        return {'db': db, 'Test': Test, 'StudentSubmission': StudentSubmission}

    app.logger.info("App created successfully.")
    app.logger.info(f"Uploads folder: {app.config['UPLOAD_FOLDER']}")
    return app


def create_upload_folders(app):
    base_folder = app.config.get('UPLOAD_FOLDER')
    if not base_folder:
        app.logger.error("UPLOAD_FOLDER config not set!")
        return

    subfolders = [
        "answered_scripts",
        "audit_logs",
        "class_lists",
        "combined_scripts",
        "extracted",
        "feedback",
        "manifests",
        "marked",
        "marking_guides",
        "question_papers",
        "resources",
        "rubrics",
        "student_lists",
        "student_scripts",
        "submissions",
        "tmp",
        "exports",
        "guides",
    ]

    for subfolder in subfolders:
        try:
            os.makedirs(os.path.join(base_folder, subfolder), exist_ok=True)
            app.logger.debug(f"Ensured upload subfolder exists: {subfolder}")
        except Exception as e:
            app.logger.error(f"Failed to create upload subfolder {subfolder}: {e}")


def run_alembic_migrations(app):
    try:
        ini_path = os.path.abspath(os.path.join(app.root_path, '..', '..', 'alembic.ini'))
        alembic_cfg = Config(ini_path)
        command.upgrade(alembic_cfg, 'head')
        app.logger.info("Alembic migrations applied.")
    except Exception as e:
        app.logger.error(f"Alembic migration error: {e}")
        traceback.print_exc()


def setup_logging(app):
    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

    if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)

    logs_dir = app.config.get('LOG_DIR', os.path.join(app.root_path, '..', 'logs'))
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, 'app.log')

    if not any(isinstance(h, RotatingFileHandler) for h in app.logger.handlers):
        file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    app.logger.info(f"Logging initialized at {log_path}")


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning("403 Forbidden", exc_info=error)
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning("404 Not Found", exc_info=error)
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error("500 Internal Server Error", exc_info=error)
        return render_template("errors/500.html"), 500
