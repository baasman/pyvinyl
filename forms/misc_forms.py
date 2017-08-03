from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateTimeField

from app import mongo, app

import datetime


class DiscogsValidationForm(FlaskForm):
    code = StringField('Code given by discogs', validators=[DataRequired])
    submit = SubmitField('Register')


# def discogs_id_validator(form, field):
#     username = app.app_context()
#     if mongo.db.users.find_one({'user': username})


class AddRecordForm(FlaskForm):
    discogs_id = DecimalField('Discogs release ID', validators=[Optional()])
    discogs_master_id = DecimalField('Discogs master ID', validators=[Optional()])
    submit = SubmitField('Submit')

    #TODO: check whether album is in users collection, use custom validator

    def validate(self):
        print(self.discogs_master_id.data)
        if not self.discogs_id.data and not self.discogs_master_id.data:
            print(1)
            return False
        if self.discogs_id.data and self.discogs_master_id.data:
            print(2)
            return False
        print(3)
        return True


class ScrobbleForm(FlaskForm):
    format = '%m/%d/%Y, %H:%M %p'
    play_date = DateTimeField('Started playing', default=datetime.datetime.now(),
                                   format=format, validators=[Optional])
    submit = SubmitField('Scrobble')