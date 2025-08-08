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
try:
        db.session.commit()
except SQLAlchemyError as e:
db.session.rollback()
current_app.logger.error(f'Database error: {e}')
flash('A database error occurred.', 'danger')
        click.echo(f"User {email} promoted to admin.")

if __name__ == "__main__":
    promote()

