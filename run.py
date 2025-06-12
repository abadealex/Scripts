from cograder_clone import create_app
from cograder_clone.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all database tables are created
    app.run(host='0.0.0.0', port=5000)

