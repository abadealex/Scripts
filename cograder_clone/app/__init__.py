import os
import logging
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import config_by_name

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_upload_folders(app):
    uploads_root = os.path.abspath(os.path.join(app.root_path, '..', '..', 'uploads'))
    folders = [
        os.path.join(uploads_root, 'guides'),
        os.path.join(uploads_root, 'answers'),
        os.path.join(uploads_root, 'marked')
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        app.logger.info(f"[INIT] Ensured upload folder: {folder}")

def setup_logging(app):
    if not app.debug and not app.testing:
        log_file = app.config.get('LOG_FILE', os.path.join(app.root_path, 'app.log'))
        if not any(isinstance(h, logging.FileHandler) for h in app.logger.handlers):
            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application started')

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

def create_app(config_name='default'):
    base_dir = os.path.abspath(os.path.dirname(__file__))  # cograder_clone/app
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

    # Setup
    create_upload_folders(app)
    setup_logging(app)
    register_error_handlers(app)

    @app.context_processor
    def inject_year():
        return {'current_year': datetime.now().year}

    from cograder_clone.app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import blueprints
    from cograder_clone.app.auth.routes import auth as auth_blueprint
    from cograder_clone.app.main.routes import main as main_blueprint
    from cograder_clone.app.student.routes import student_bp as student_blueprint
    from cograder_clone.app.teacher.routes import teacher_bp as teacher_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(student_blueprint)
    app.register_blueprint(teacher_blueprint)

    return app
