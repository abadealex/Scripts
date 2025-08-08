import os
import sys
import asyncio
import logging
import hypercorn.asyncio
from hypercorn.config import Config

# ---------- Enable detailed logging ----------
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture everything
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# Add the parent directory to the Python path so 'smartscripts' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from smartscripts.app import create_app  # Must come after sys.path adjustment

# Get config name from environment, default to 'development'
config_name = os.getenv('FLASK_CONFIG', 'development')
logging.debug(f"Using config: {config_name}")

# Create the Flask app instance
app = create_app(config_name)

if __name__ == '__main__':
    """
    Run the Flask app asynchronously with Hypercorn HTTP/2 server.
    Configurable via environment variables:
      - PORT: port to listen on (default 5000)
      - FLASK_DEBUG: enable debug mode (default False)
      - FLASK_CONFIG: config name passed to app factory (default 'development')
    """

    port = int(os.getenv("PORT", 5000))
    debug_env = os.getenv('FLASK_DEBUG', 'false').lower()
    debug = debug_env in ('true', '1', 'yes')

    host = os.getenv("HOST", "0.0.0.0")

    # Log resolved runtime config
    logging.info(f"Starting server on {host}:{port} (debug={debug})")

    # Configure Hypercorn server
    hypercorn_config = Config()
    hypercorn_config.bind = [f"{host}:{port}"]
    hypercorn_config.debug = debug
    hypercorn_config.reload = debug  # Enable auto reload in debug mode

    try:
                asyncio.run(hypercorn.asyncio.serve(app, hypercorn_config))
    except Exception as e:
        logging.exception("Failed to start server")
        sys.exit(1)

