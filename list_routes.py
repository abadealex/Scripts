from your_app import app  # change this to your actual app import

with app.app_context():
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, URL: {rule}, Methods: {rule.methods}")

