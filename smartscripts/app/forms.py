from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import (
    HiddenField, StringField, PasswordField, SubmitField, BooleanField,
    FileField, SelectField, MultipleFileField, TextAreaField, DateField, FieldList
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
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6), EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
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
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6), EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Teacher Register')


# -----------------------
# Test Creation & Upload
# -----------------------

class TestMaterialsUploadForm(FlaskForm):
    test_title = StringField('Test Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])

    subject = SelectField('Subject', choices=[
        ('math', 'Math'),
        ('science', 'Science'),
        ('english', 'English'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry')
    ], validators=[DataRequired()])

    grade_level = SelectField('Grade Level', choices=[
        ('9', '9th Grade'),
        ('10', '10th Grade'),
        ('11', '11th Grade'),
        ('12', '12th Grade')
    ], validators=[Optional()])

    exam_date = DateField('Exam Date (optional)', format='%Y-%m-%d', validators=[Optional()])

    marking_guide = FileField('Marking Guide (PDF)', validators=[
        FileRequired(), FileAllowed(['pdf'], 'PDF files only!')
    ])

    rubric = FileField('Rubric (PDF)', validators=[
        Optional(), FileAllowed(['pdf'], 'PDF files only!')
    ])

    answered_script = FileField('Answered Script (PDF)', validators=[
        Optional(), FileAllowed(['pdf'], 'PDF files only!')
    ])

    student_scripts = MultipleFileField('Student Scripts', validators=[
        FileRequired(), FileAllowed(
            ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'],
            'Allowed types: pdf, doc, docx, png, jpg, jpeg'
        )
    ])

    # Hidden fields for student IDs to match uploads
    student_ids = FieldList(HiddenField('Student ID'), min_entries=0)

    submit = SubmitField('Upload All')


# -----------------------
# AI Grading Trigger Form
# -----------------------

class StartGradingForm(FlaskForm):
    confirm = BooleanField("I'm ready to start AI grading and lock this test", validators=[DataRequired()])
    submit = SubmitField('Start AI Grading')


# -----------------------
# Test Creation (Step 1 Only)
# -----------------------

class CreateTestForm(FlaskForm):
    test_title = StringField('Test Title', validators=[DataRequired()])
    subject = SelectField('Subject', choices=[
        ('math', 'Math'),
        ('science', 'Science'),
        ('english', 'English'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry')
    ], validators=[DataRequired()])
    grade_level = SelectField('Grade Level', choices=[
        ('9', '9th Grade'),
        ('10', '10th Grade'),
        ('11', '11th Grade'),
        ('12', '12th Grade')
    ], validators=[Optional()])
    exam_date = DateField('Exam Date (optional)', format='%Y-%m-%d', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Create Test')


class AIGradingForm(FlaskForm):
    submit = SubmitField('Start AI Grading')
