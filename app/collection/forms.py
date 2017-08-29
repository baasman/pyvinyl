from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Optional

import datetime
from dateutil import tz

def _add_hover_to_label(title, label):
    return "<a href='#' data-toggle='tooltip' title='%s'>%s</a>" % (title, label)


class DiscogsValidationForm(FlaskForm):
    code = StringField('Code given by discogs', validators=[DataRequired])
    submit = SubmitField('Register')

    def validate(self):
        return True


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
    cl_help = 'Example: https://www.discogs.com/user/<yourusername>/collection'


    collection_link = StringField(_add_hover_to_label(cl_help, 'Link to collection (?)'),
                                  validators=[Optional()])
    discogs_id = DecimalField(_add_hover_to_label(did_help, 'Discogs release ID (?)'),
                              validators=[Optional()])

    submit = SubmitField('Submit')

    # TODO: check whether album is in users collection, use custom validator
    def validate_discogs_id(self, Field):
        return True

    def validate(self):
        if not self.discogs_id.data and not self.collection_link.data:
            return False
        if self.discogs_id.data and self.collection_link.data:
            return False
        return True


class ScrobbleForm(FlaskForm):
    just_record_help = 'This wont scrobble to your last.fm, but still record your activity'
    format = '%m/%d/%Y, %H:%M %p'

    def_time = datetime.datetime.utcnow()
    UTC = tz.gettz('UTC')
    def_time = def_time.replace(tzinfo=UTC)

    # TODO: Ask user for timezone
    tz_present = 'US/Eastern'
    if tz_present:
        def_time = def_time.astimezone(tz.gettz(tz_present))

    play_date = DateTimeField('Started playing', default=def_time,
                                   format=format, validators=[Optional()])
    submit = SubmitField('Scrobble', default=False)
    just_record_submit = SubmitField('Record', default=False)

    def validate(self):
        if self.submit.data | self.just_record_submit.data:
            return True
        else:
            False

class DeleteForm(FlaskForm):

    delete = SubmitField('X')

    def validate(self):
        if self.delete.data:
            return True
        return False