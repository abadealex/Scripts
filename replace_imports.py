import os

old_name = 'cograder_clone'
new_name = 'smartscripts'

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    new_content = content.replace(f'from {old_name}', f'from {new_name}') \
                         .replace(f'import {old_name}', f'import {new_name}')
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"✅ Updated: {filepath}")

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                replace_in_file(os.path.join(root, file))

if __name__ == '__main__':
    process_directory(os.getcwd())


