from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class VerifyEmailForm(FlaskForm):
    verification_code = StringField('Verification Code', 
        validators=[
            DataRequired(message='Please enter the verification code'),
            Length(min=6, max=6, message='Verification code must be 6 digits'),
            Regexp('^[0-9]{6}$', message='Verification code must contain only numbers')
        ])
    submit = SubmitField('Verify Email') 