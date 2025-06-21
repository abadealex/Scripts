import os
import logging
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from alembic.config import Config
from alembic import command
import traceback

from smartscripts.app.models import db, User
from smartscripts.app.auth.routes import auth
from smartscripts.app.main.routes import main
from smartscripts.app.teacher.routes import teacher_bp
from smartscripts.app.student.routes import student_bp
from smartscripts.config import config_by_name


login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app(config_name='default'):
    try:
        app = Flask(__name__)
        app.config.from_object(config_by_name[config_name])

        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        migrate.init_app(app, db)
        mail.init_app(app)

        login_manager.login_view = "auth.login"
        login_manager.login_message = "Please log in to access this page."
        login_manager.login_message_category = "info"

        # Register blueprints
        app.register_blueprint(auth)
        app.register_blueprint(main)
        app.register_blueprint(teacher_bp)
        app.register_blueprint(student_bp)

        # Create upload folders if not exist
        def create_upload_folders():
            folders = [
                app.config.get('UPLOAD_FOLDER', 'uploads'),
                app.config.get('UPLOAD_FOLDER_GUIDES', 'uploads/guides')
            ]
            for folder in folders:
                try:
                    os.makedirs(folder, exist_ok=True)
                except Exception as e:
                    app.logger.error(f"Failed to create folder {folder}: {e}")

        create_upload_folders()

        # Run DB migrations
        try:
            alembic_cfg = Config(os.path.join(app.root_path, 'migrations', 'alembic.ini'))
            command.upgrade(alembic_cfg, 'head')
            app.logger.info("Database migrated successfully.")
        except Exception as e:
            app.logger.error(f"DB migration failed: {e}")
            # Print full traceback to console/log
            traceback.print_exc()

        # Setup logging to file
        if not app.debug:
            log_file = os.path.join(app.root_path, 'app.log')
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        return app

    except Exception as e:
        print("[ERROR] create_app failed:")
        traceback.print_exc()
        raise
