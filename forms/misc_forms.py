from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired


class DiscogsValidationForm(FlaskForm):
    code = StringField('Code given by discogs', validators=[DataRequired])
    submit = SubmitField('Register')


class AddRecordForm(FlaskForm):
    discogs_id = DecimalField('Discogs record id', validators=[DataRequired])
    submit = SubmitField('Submit')
