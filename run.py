import os
import sys

# Ensure the parent directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from smartscripts.app import create_app

# Get config name from environment, default to 'development'
config_name = os.getenv('FLASK_CONFIG', 'development')

# This must be available at the top level so Gunicorn can see it
app = create_app(config_name)

# Only use app.run() for local debugging
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
