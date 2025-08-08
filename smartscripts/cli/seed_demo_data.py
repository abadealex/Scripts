# cli/seed_demo_data.py
import click
from smartscripts.app import create_app, db
from smartscripts.models import User, Submission, Organization

app = create_app()

@click.command()
def seed():
    with app.app_context():
        # Seed organizations
        org = Organization(name="Demo School")
        db.session.add(org)

        # Seed users
        admin = User(email="admin@demo.com", role="admin", organization=org)
        teacher = User(email="teacher@demo.com", role="teacher", organization=org)
        student = User(email="student@demo.com", role="student", organization=org)
        db.session.add_all([admin, teacher, student])

        # Seed submissions
        sub = Submission(student=student, content="This is a sample answer.")
        db.session.add(sub)

try:
        db.session.commit()
except SQLAlchemyError as e:
db.session.rollback()
current_app.logger.error(f'Database error: {e}')
flash('A database error occurred.', 'danger')
        click.echo("Demo data seeded.")

if __name__ == "__main__":
    seed()

