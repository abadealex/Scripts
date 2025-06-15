import os
import logging
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import config_by_name  # your config dict or object mapping

# Initialize extensions (do not bind to app here)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_upload_folders(app):
    """
    Create upload folders if they don't exist.
    Raises RuntimeError if expected config keys are missing.
    """
    try:
        folders = [
            app.config['UPLOAD_FOLDER_GUIDES'],
            app.config['UPLOAD_FOLDER_ANSWERS'],
            app.config['UPLOAD_FOLDER_MARKED']
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            app.logger.info(f"[INIT] Ensured upload folder: {folder}")
    except KeyError as e:
        raise RuntimeError(f"Missing expected config key: {e}")

def setup_logging(app):
    """
    Setup file logging if not in debug mode.
    """
    if not app.debug:
        handler = logging.FileHandler('app.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('App started')

def register_error_handlers(app):
    """
    Register custom error pages.
    """
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

def create_app(config_name='default'):
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'  # Redirect unauthorized users here

    # Ensure upload folders exist
    create_upload_folders(app)

    # Setup logging for production
    setup_logging(app)

    # Register error handlers
    register_error_handlers(app)

    # Inject current year globally in templates
    @app.context_processor
    def inject_year():
        return {'current_year': datetime.now().year}

    # Import User model here to avoid circular imports
    from .app.models import User

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from .app.auth.routes import auth as auth_blueprint
    from .app.main.routes import main as main_blueprint
    from .app.student.routes import student_bp as student_blueprint
    from .app.teacher.routes import teacher_bp as teacher_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(student_blueprint)
    app.register_blueprint(teacher_blueprint)

    return app
