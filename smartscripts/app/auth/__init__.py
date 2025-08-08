from flask import Blueprint
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint('auth', __name__, template_folder='templates')

from . import routes


