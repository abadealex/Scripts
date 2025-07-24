from fastapi import FastAPI
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

print("main.py started")

def create_app():
    app = FastAPI()
    print("Created FastAPI app")

    # Define your routes
    @app.get("/")
    def root():
        logging.debug("Handling request to /")
        return {"message": "Hello from FastAPI"}

    return app
from smartscripts.api.v1.submissions import bp as submissions_bp
app.register_blueprint(submissions_bp, url_prefix='/api/v1')
