import os
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate, upgrade
from flask_mail import Mail
from config import config_by_name

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return "404 Not Found", 404

    @app.errorhandler(500)
    def internal_error(error):
        return "500 Internal Server Error", 500

def create_upload_folders(app):
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

def setup_logging(app):
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/smartscripts.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Smartscripts startup')

def create_app(config_name='default'):
    base_dir = os.path.abspath(os.path.dirname(__file__))  # smartscripts/app
    template_dir = os.path.abspath(os.path.join(base_dir, '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(base_dir, '..', 'static'))

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'

    create_upload_folders(app)
    setup_logging(app)
    register_error_handlers(app)

    @app.context_processor
    def inject_year():
        return {'current_year': datetime.now().year}

    from smartscripts.app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🔁 Automatically run DB migration (for Render free tier)
    with app.app_context():
        try:
            upgrade()
            print("[INFO] Database migrated successfully.")
        except Exception as e:
            print(f"[ERROR] Database migration failed: {e}")

    # Register blueprints
    from smartscripts.app.auth.routes import auth as auth_blueprint
    from smartscripts.app.main.routes import main as main_blueprint
    from smartscripts.app.student.routes import student_bp as student_blueprint
    from smartscripts.app.teacher.routes import teacher_bp as teacher_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(student_blueprint)
    app.register_blueprint(teacher_blueprint)

    return app
