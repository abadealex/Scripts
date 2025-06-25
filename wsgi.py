import os
from smartscripts.app import create_app

# Default to 'production' config unless explicitly set
config_name = os.getenv('FLASK_CONFIG', 'production')

app = create_app(config_name)
