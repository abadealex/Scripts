# smartscripts/app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')


# Teacher specific forms

class TeacherLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Teacher Login')


class TeacherRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Teacher Register')


# Student specific form for file upload

class StudentUploadForm(FlaskForm):
    file = FileField('Upload File', validators=[DataRequired()])
    submit = SubmitField('Submit')


# New form for marking guide upload

class MarkingGuideUploadForm(FlaskForm):
    file = FileField('Upload Marking Guide', validators=[DataRequired()])
    submit = SubmitField('Upload Marking Guide')
