# smartscripts/app/__init__.py

import os
import logging
import traceback

from flask import Flask
from alembic.config import Config
from alembic import command

from smartscripts.extensions import db, login_manager, mail, migrate
from smartscripts.app.models import User
from smartscripts.app.auth.routes import auth
from smartscripts.app.main.routes import main
from smartscripts.app.teacher.routes import teacher_bp
from smartscripts.app.student.routes import student_bp
from smartscripts.config import config_by_name


def create_app(config_name='default'):
    try:
        app = Flask(__name__)
        app.config.from_object(config_by_name[config_name])

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

        # Register blueprints
        app.register_blueprint(auth)
        app.register_blueprint(main)
        app.register_blueprint(teacher_bp)
        app.register_blueprint(student_bp)

        # Create upload folders
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

        # Run Alembic migrations
        try:
            alembic_cfg = Config(os.path.join(app.root_path, 'migrations', 'alembic.ini'))
            command.upgrade(alembic_cfg, 'head')
            app.logger.info("Database migrated successfully.")
        except Exception as e:
            app.logger.error(f"DB migration failed: {e}")
            traceback.print_exc()

        # Logging setup for production
        if not app.debug:
            log_file = os.path.join(app.root_path, 'app.log')
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)

        return app

    except Exception as e:
        print("[ERROR] create_app failed:")
        traceback.print_exc()
        raise
