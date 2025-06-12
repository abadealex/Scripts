import os

IGNORE_DIRS = {'__pycache__', 'venv', '.venv', 'Scripts'}

def print_structure(root_dir, prefix=""):
    entries = sorted(os.listdir(root_dir))
    entries = [e for e in entries if e not in IGNORE_DIRS]
    for i, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        print(prefix + connector + entry)
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_structure(path, new_prefix)

if __name__ == "__main__":
    print("Project Structure:")
    print_structure(".")
