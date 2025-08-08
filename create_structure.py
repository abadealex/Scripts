import os

# Define the folder and file structure
structure = {
    "cograde_clone": {
        "app": {
            "__init__.py": "",
            "models.py": "",
            "forms.py": "",
            "utils.py": "",
            "routes": {
                "__init__.py": "",
                "student.py": "",
                "teacher.py": ""
            },
            "templates": {
                "dashboard.html": "",
                "index.html": "",
                "login.html": "",
                "upload_student.html": "",
                "upload_teacher.html": ""
            },
            "static": {}
        },
        "run.py": "",
        "requirements.txt": ""
    }
}

# Recursive function to create folders/files
def create_structure(base_path, tree):
    for name, content in tree.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write(content)

# Create the structure
create_structure(".", structure)

# Print the structure
def print_tree(start_path, indent=""):
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent_space = '│   ' * level
        print(f"{indent_space}├── {os.path.basename(root)}/")
        sub_indent = '│   ' * (level + 1)
        for f in files:
            print(f"{sub_indent}├── {f}")

print("\nDirectory structure:")
print_tree("cograde_clone")

