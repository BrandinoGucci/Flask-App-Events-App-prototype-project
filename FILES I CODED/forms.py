from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email, NumberRange
from wtforms import ValidationError
from models import User
from database import db


class RegisterForm(FlaskForm):
    class Meta:
        csrf = False

    firstname = StringField('First Name', validators=[Length(1, 10)])

    lastname = StringField('Last Name', validators=[Length(1, 20)])

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password."),
        EqualTo('confirmPassword', message='Passwords must match')
    ])

    confirmPassword = PasswordField('Confirm Password', validators=[
        Length(min=6, max=10)
    ])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() != 0:
            raise ValidationError('Username already in use.')


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password.")])

    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() == 0:
            raise ValidationError('Incorrect username or password.')


class RSVPForm(FlaskForm):
    class Meta:
        csrf = False

    user_name = TextAreaField('Name',validators=[Length(min=1)])

    submit = SubmitField('Add RSVP')


class RateForm(FlaskForm):
    class Meta:
        csrf = False
    rating = IntegerField('Rating',validators=[NumberRange(min=1,max=10)])

    submit = SubmitField('Submit')