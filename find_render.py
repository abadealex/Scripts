import os

for root, dirs, files in os.walk('smartscripts/app'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                for num, line in enumerate(f, 1):
                    if 'render_template(' in line:
                        print(f"{path}:{num}: {line.strip()}")

