from app import mongo

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    lastfm_user = StringField('Lastfm username')
    lastfm_password = PasswordField('Lastfm password')
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm_password',
                                                             message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')

    def validate_email(self, field):
        if mongo.db.users.find_one({'email': field.data}) is not None:
            raise ValidationError('Email already in use')

    def validate_username(self, field):
        if mongo.db.users.find_one({'user': field.data}) is not None:
            raise ValidationError('Username already in use')


class LoginForm(FlaskForm):
    user = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired])
    submit = SubmitField('Login')