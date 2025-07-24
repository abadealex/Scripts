# cli/create_admin.py
import click
from smartscripts.app import create_app, db
from smartscripts.models import User

app = create_app()

@click.command()
@click.argument("email")
def promote(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            click.echo("User not found.")
            return

        user.role = 'admin'
        db.session.commit()
        click.echo(f"User {email} promoted to admin.")

if __name__ == "__main__":
    promote()
