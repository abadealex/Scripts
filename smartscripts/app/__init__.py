import os
import logging
import traceback
from datetime import datetime

from flask import Flask, render_template
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

from smartscripts.extensions import db, login_manager, mail, migrate
from smartscripts.app.models import User
from smartscripts.app.auth import auth_bp
from smartscripts.app.main import main_bp
from smartscripts.app.teacher import teacher_bp
from smartscripts.app.student import student_bp
from smartscripts.config import config_by_name

# Load environment variables
load_dotenv()
print("DATABASE_URL used:", os.getenv("DATABASE_URL"))


def create_app(config_name='default'):
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        template_dir = os.path.join(base_dir, 'templates')
        static_dir = os.path.join(base_dir, 'static')

        app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
        app.config.from_object(config_by_name[config_name])

        # Override DB URI from environment
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url

        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        migrate.init_app(app, db)

        login_manager.login_view = "auth.login"
        login_manager.login_message = "Please log in to access this page."
        login_manager.login_message_category = "info"

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Register Blueprints (assuming url_prefix is set inside each blueprint)
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(teacher_bp)
        app.register_blueprint(student_bp)

        # Create necessary folders
        create_upload_folders(app, base_dir)

        # Run Alembic migrations in dev mode
        if app.config.get("ENV") == "development":
            run_alembic_migrations(app)

        # Logging setup
        if not app.debug and not app.testing:
            setup_file_logging(app)

        register_error_handlers(app)

        @app.context_processor
        def inject_current_year():
            return {'current_year': datetime.utcnow().year}

        return app

    except Exception:
        print("[ERROR] create_app failed:")
        traceback.print_exc()
        raise


def create_upload_folders(app, base_dir):
    folders = [
        app.config.get('UPLOAD_FOLDER', os.path.join(base_dir, '..', 'uploads')),
        app.config.get('UPLOAD_FOLDER_GUIDES', os.path.join(base_dir, '..', 'uploads', 'guides'))
    ]
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as e:
            app.logger.error(f"Failed to create folder {folder}: {e}")


def run_alembic_migrations(app):
    try:
        ini_path = os.path.abspath(os.path.join(app.root_path, '..', '..', 'alembic.ini'))
        print("[DEBUG] Alembic ini path:", ini_path)
        alembic_cfg = Config(ini_path)
        command.upgrade(alembic_cfg, 'head')
        app.logger.info("Database migrated successfully.")
    except Exception as e:
        app.logger.error(f"Alembic migration failed: {e}")
        traceback.print_exc()


def setup_file_logging(app):
    log_file = os.path.join(app.root_path, 'app.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)


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
