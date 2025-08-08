from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, FileField,
    SelectField, TextAreaField, DateField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

# -----------------------
# Authentication Forms
# -----------------------

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=25)],
        render_kw={"placeholder": "Enter your username"}
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message='Passwords must match')],
        render_kw={"placeholder": "Create a password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired()],
        render_kw={"placeholder": "Repeat your password"}
    )
    role = SelectField(
        'Role',
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Register')


# -----------------------
# Teacher Authentication
# -----------------------

class TeacherLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Teacher Login')


class TeacherRegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message='Passwords must match')]
    )
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    role = SelectField(
        'Registering As',
        choices=[('Teacher', 'Teacher'), ('Student', 'Student')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Register')


# -----------------------
# Test Creation (Step 1)
# -----------------------

class CreateTestForm(FlaskForm):
    test_title = StringField('Test Title', validators=[DataRequired()])

    subject = SelectField(
        'Subject',
        choices=[
            ('math', 'Math'),
            ('science', 'Science'),
            ('english', 'English'),
            ('history', 'History'),
            ('geography', 'Geography'),
            ('physics', 'Physics'),
            ('chemistry', 'Chemistry')
        ],
        validators=[DataRequired()]
    )

    grade_level = SelectField(
        'Grade Level',
        choices=[
            ('9', '9th Grade'),
            ('10', '10th Grade'),
            ('11', '11th Grade'),
            ('12', '12th Grade')
        ],
        validators=[Optional()]
    )

    exam_date = DateField('Exam Date (optional)', format='%Y-%m-%d', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Create Test')


# -----------------------
# Upload Additional Materials (Step 2)
# -----------------------

class TestMaterialsUploadForm(FlaskForm):
    def __init__(self, test=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if test and getattr(test, 'question_paper_path', None):
            self.question_paper.validators = [Optional(), FileAllowed(['pdf'], 'PDF files only!')]
        else:
            self.question_paper.validators = [FileRequired(), FileAllowed(['pdf'], 'PDF files only!')]

    # Metadata fields (for create step)
    test_title = StringField('Test Title', validators=[Optional(), Length(max=100)])
    subject = SelectField(
        'Subject',
        choices=[
            ('math', 'Math'),
            ('science', 'Science'),
            ('english', 'English'),
            ('history', 'History'),
            ('geography', 'Geography'),
            ('physics', 'Physics'),
            ('chemistry', 'Chemistry')
        ],
        validators=[Optional()]
    )
    grade_level = SelectField(
        'Grade Level',
        choices=[('9', '9th Grade'), ('10', '10th Grade'), ('11', '11th Grade'), ('12', '12th Grade')],
        validators=[Optional()]
    )
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])

    # Individual upload fields
    question_paper = FileField('Question Paper (PDF)')
    rubric = FileField('Rubric (PDF)', validators=[Optional(), FileAllowed(['pdf'], 'PDF files only!')])
    marking_guide = FileField('Marking Guide (PDF)', validators=[Optional(), FileAllowed(['pdf'], 'PDF files only!')])
    answered_script = FileField('Answered Script (PDF)', validators=[Optional(), FileAllowed(['pdf'], 'PDF files only!')])

    # Bulk upload fields - renamed for consistency
    class_list = FileField('Class List (CSV/TXT)', validators=[Optional(), FileAllowed(['csv', 'txt'], 'CSV or TXT files only!')])
    combined_scripts = FileField('Combined Scripts (PDF)', validators=[Optional(), FileAllowed(['pdf'], 'PDF files only!')])

    # Global upload button
    submit = SubmitField('Upload All')


# -----------------------
# AI Grading Form
# -----------------------

class AIGradingForm(FlaskForm):
    submit = SubmitField('Start AI Grading')
