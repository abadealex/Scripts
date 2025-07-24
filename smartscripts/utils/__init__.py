# smartscripts/utils/__init__.py

from .file_io import (
    allowed_file,
    ensure_folder_exists,
    delete_file_if_exists,
    save_file,
    create_test_directories,
    is_released,
)

from .access_control import (
    check_teacher_access,
    check_student_access,
    check_role_access,
)

__all__ = [
    'allowed_file',
    'ensure_folder_exists',
    'delete_file_if_exists',
    'save_file',
    'create_test_directories',
    'is_released',
    'check_teacher_access',
    'check_student_access',
    'check_role_access',
]
