from flask import Blueprint

main_bp = Blueprint('main', __name__)

from . import routes  # Ensure this import is here so routes are registered
