from smartscripts.app import create_app, db
from smartscripts.models import User, MarkingGuide, StudentSubmission
from flask_migrate import Migrate
from flask.cli import FlaskGroup

app = create_app()
migrate = Migrate(app, db)

cli = FlaskGroup(create_app=create_app)

@cli.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'MarkingGuide': MarkingGuide,
        'StudentSubmission': StudentSubmission
    }

if __name__ == '__main__':
    cli()

