from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Initialize extensions (to be initialized later in app factory)
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

# Optional: configure login view and messages here if needed
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."
