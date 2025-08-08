import os
from flask_migrate import Migrate
from smartscripts.app import create_app
from smartscripts.extensions import db

# Default to 'production' config unless explicitly set
config_name = os.getenv('FLASK_CONFIG', 'production')
app = create_app(config_name)

# ✅ Add this to bind Migrate CLI commands
migrate = Migrate(app, db)

