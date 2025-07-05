from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from celery import Celery

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

# Optional: configure login view and messages
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."

# Celery instance (to be configured in app factory)
celery = Celery(__name__)
