import os
import sys

# Ensure the parent 'smartscripts' directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Default to 'production' config unless explicitly set
config_name = os.getenv('FLASK_CONFIG', 'production')

from smartscripts.app import create_app

app = create_app(config_name)
