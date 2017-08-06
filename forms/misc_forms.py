from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateTimeField

from app import mongo, app

import datetime


class DiscogsValidationForm(FlaskForm):
    code = StringField('Code given by discogs', validators=[DataRequired])
    submit = SubmitField('Register')

class AddTagForm(FlaskForm):
    tag = StringField('Tag for album')
    submit = SubmitField('Add')

    def validate(self):
        if self.tag.data != '':
            return True
        return False


class AddRecordForm(FlaskForm):
    discogs_id = DecimalField('Discogs release ID', validators=[Optional()])
    discogs_master_id = DecimalField('Discogs master ID', validators=[Optional()])
    submit = SubmitField('Submit')

    #TODO: check whether album is in users collection, use custom validator

    def validate(self):
        if not self.discogs_id.data and not self.discogs_master_id.data:
            return False
        if self.discogs_id.data and self.discogs_master_id.data:
            return False
        return True


class ScrobbleForm(FlaskForm):
    format = '%m/%d/%Y, %H:%M %p'
    play_date = DateTimeField('Started playing', default=datetime.datetime.now(),
                                   format=format, validators=[Optional()])
    submit = SubmitField('Scrobble', default=False, validators=[DataRequired])

    def validate(self):
        if self.submit.data:
            return True
        else:
            False