from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from app import mongo

class User():
    def __init__(self, username, email=None, unhashed_password=None,
                 discogs_user=None):
        self.username = username
        self.email = email
        self.discogs_user = discogs_user
        # self.unhashed_password = unhashed_password

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    discogs_user = StringField('Discogs username')
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
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired])
    submit = SubmitField('Login')



