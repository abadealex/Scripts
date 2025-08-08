# smartscripts/extensions.py

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

# Initialize Celery instance (adjust broker URL as needed)
celery = Celery(__name__, broker='redis://localhost:6379/0')

def configure_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."

# Optional: explicit exports if you use __all__
__all__ = [
    'db',
    'login_manager',
    'mail',
    'migrate',
    'celery',
    'configure_login_manager',
]
