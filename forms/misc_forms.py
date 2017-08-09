from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateTimeField

import datetime


def _add_hover_to_label(title, label):
    return "<a href='#' data-toggle='tooltip' title='%s'>%s</a>" % (title, label)


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
    did_help = 'The number you will find at the end of an albums release page url'
    dmid_help = 'The number you will find at the end of an albums master page url'

    discogs_id = DecimalField(_add_hover_to_label(did_help, 'Discogs release ID (?)'),
                              validators=[Optional()])
    discogs_master_id = DecimalField(_add_hover_to_label(dmid_help, 'Discogs master ID (?)'),
                                                         validators=[Optional()])
    submit = SubmitField('Submit')

    # TODO: check whether album is in users collection, use custom validator

    def validate(self):
        if not self.discogs_id.data and not self.discogs_master_id.data:
            return False
        if self.discogs_id.data and self.discogs_master_id.data:
            return False
        return True


class ScrobbleForm(FlaskForm):
    just_record_help = 'This wont scrobble to your last.fm, but still record your activity'
    format = '%m/%d/%Y, %H:%M %p'
    play_date = DateTimeField('Started playing', default=datetime.datetime.now(),
                                   format=format, validators=[Optional()])
    submit = SubmitField('Scrobble', default=False)
    just_record_submit = SubmitField('Record', default=False)

    def validate(self):
        if self.submit.data | self.just_record_submit.data:
            return True
        else:
            False