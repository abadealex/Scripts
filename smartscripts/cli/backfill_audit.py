# cli/backfill_audit.py
import click
from smartscripts.app import create_app
from smartscripts.compliance.audit_logger import log_action

app = create_app()

@click.command()
def backfill():
    with app.app_context():
        # Example placeholder logic — adjust per your DB schema
        from smartscripts.models import User
        users = User.query.all()
        for user in users:
            log_action(user_id=user.id, action="backfill:user_imported")
            click.echo(f"Audit log created for user {user.email}")

if __name__ == "__main__":
    backfill()
