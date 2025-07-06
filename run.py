import os
import sys

# Ensure the parent directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from smartscripts.app import create_app

# Get config name from environment, default to 'development'
config_name = os.getenv('FLASK_CONFIG', 'development')

# This must be available at the top level so Hypercorn can see it
app = create_app(config_name)

# Only use app.run() for local debugging with Hypercorn
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Run the application using Hypercorn instead of Flask's built-in server
    import hypercorn.asyncio
    from hypercorn.config import Config
    import asyncio

    # Setup Hypercorn config
    hypercorn_config = Config()
    hypercorn_config.bind = [f"0.0.0.0:{port}"]
    hypercorn_config.debug = debug

    # Run the app with Hypercorn
    asyncio.run(hypercorn.asyncio.serve(app, hypercorn_config))
