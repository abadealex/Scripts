from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            InputRequired(message="Email is required."),
            Email(message="Enter a valid email address.")
        ]
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Password is required."),
            Length(min=6, message="Password must be at least 6 characters.")
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ]
    )
    role = SelectField(
        "Register As",
        choices=[("teacher", "Teacher"), ("student", "Student")],
        validators=[InputRequired(message="Please select a role.")]
    )
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            InputRequired(message="Email is required."),
            Email(message="Enter a valid email address.")
        ]
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(message="Password is required.")]
    )
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")
