from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateTimeField
import datetime


class DiscogsValidationForm(FlaskForm):
    code = StringField('Code given by discogs', validators=[DataRequired])
    submit = SubmitField('Register')


class AddRecordForm(FlaskForm):
    discogs_id = DecimalField('Discogs record id', validators=[DataRequired])
    submit = SubmitField('Submit')


class ScrobbleForm(FlaskForm):
    format = '%m/%d/%Y, %H:%M %p'
    play_date = DateTimeField('Started playing', default=datetime.datetime.now(),
                                   format=format, validators=[Optional])
    submit = SubmitField('Scrobble')