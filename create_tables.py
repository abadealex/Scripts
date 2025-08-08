# create_tables.py
from smartscripts.extensions import db
from smartscripts.models import *   # Import all models so they register with db metadata
from smartscripts.app import create_app  # Assuming you have a Flask app factory

app = create_app()  # Create Flask app context

with app.app_context():
    db.create_all()
    print("All tables created successfully!")

