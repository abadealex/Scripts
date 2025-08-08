def log_override_change(student_id, question_number, old_score, new_score):
    print(f"[AUDIT] Override: Student {student_id}, Q{question_number}, {old_score} ? {new_score}")

def log_manual_edit(student_id, field_name, old_value, new_value):
    print(f"[AUDIT] Manual Edit: Student {student_id}, Field: {field_name}, {old_value} ? {new_value}")

def version_control_save(entity, before_state, after_state):
    print(f"[AUDIT] Version Control for {entity}:\nBefore: {before_state}\nAfter: {after_state}")

