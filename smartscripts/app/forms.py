from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    FileField, SelectField, TextAreaField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length

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
        DataRequired(),
        Length(min=6),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    submit = SubmitField('Register')

# -----------------------
# Teacher Forms
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
        DataRequired(),
        Length(min=6),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Teacher Register')

# -----------------------
# Student Upload Form
# -----------------------

class StudentUploadForm(FlaskForm):
    guide_id = SelectField('Marking Guide', coerce=int, validators=[DataRequired()])
    file = FileField('Upload File', validators=[DataRequired()])
    submit = SubmitField('Submit')


# -----------------------
# Marking Guide Upload Form (UPDATED)
# -----------------------

class MarkingGuideUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    file = FileField('Upload Marking Guide', validators=[DataRequired()])
    answers_json = TextAreaField('Ideal Answers JSON', validators=[DataRequired()])
    submit = SubmitField('Upload Marking Guide')
