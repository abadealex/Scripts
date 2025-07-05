from smartscripts.app import create_app

app = create_app('development')  # or 'default' if you want

with app.app_context():
    print("Registered Flask routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> endpoint: {rule.endpoint}")
