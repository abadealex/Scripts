import os
import sys
import logging
from logging.config import fileConfig
from contextlib import contextmanager

from alembic import context
from alembic.config import Config
from flask import current_app
from dotenv import load_dotenv

# === ✅ Load environment variables from .env and print DATABASE_URL ===
load_dotenv()
print("DATABASE_URL used in Alembic env.py:", os.getenv("DATABASE_URL"))

# === Path Setup ===
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# === Load alembic.ini dynamically ===
alembic_ini_path = os.path.join(project_root, 'alembic.ini')
config = Config(alembic_ini_path)

# === Logging ===
fileConfig(alembic_ini_path)
logger = logging.getLogger('alembic.env')

# === Import Flask App Factory ===
from smartscripts.app import create_app

@contextmanager
def flask_app_context():
    """Context manager to push and pop Flask app context properly."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    try:
                yield
    finally:
        ctx.pop()

# === Access DB Engine ===
def get_engine():
    with flask_app_context():
        try:
                    return current_app.extensions['migrate'].db.get_engine()
        except (TypeError, AttributeError):
            return current_app.extensions['migrate'].db.engine

def get_engine_url():
    # ✅ Read from .env or fallback to alembic.ini config
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        # Escape % for alembic config formatting
        return env_url.replace('%', '%%')
    with flask_app_context():
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')

# ✅ Inject SQLAlchemy URL into Alembic config
config.set_main_option('sqlalchemy.url', get_engine_url())

# === Metadata ===
def get_target_db():
    with flask_app_context():
        return current_app.extensions['migrate'].db

def get_metadata():
    target_db = get_target_db()
    return getattr(target_db, 'metadata', None)

# === Offline Migration ===
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

# === Online Migration ===
def run_migrations_online():

    def process_revision_directives(context_, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No schema changes detected.')

    with flask_app_context():
        target_db = get_target_db()

        conf_args = current_app.extensions['migrate'].configure_args
        if conf_args.get("process_revision_directives") is None:
            conf_args["process_revision_directives"] = process_revision_directives

        connectable = get_engine()

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=get_metadata(),
                **conf_args
            )
            with context.begin_transaction():
                context.run_migrations()

# === Entry Point ===
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

