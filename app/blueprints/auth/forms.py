from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('User Role', choices=[
        ('admin', 'Super Admin'),
        ('society', 'Society Secretary'),
        ('worker', 'Worker / Collection Agent')
    ], validators=[DataRequired()])
    submit = SubmitField('Login to Portal')


class RegisterSocietyForm(FlaskForm):
    society_name = StringField('Society Name', validators=[DataRequired(), Length(max=150)])
    registration_number = StringField('Registration Number (Reg No)', validators=[DataRequired(), Length(max=100)])
    secretary_name = StringField('Secretary Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Account Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    address = TextAreaField('Street Address', validators=[DataRequired()])
    landmark = StringField('Landmark', validators=[Optional()])
    city = StringField('City', validators=[DataRequired()], default='Pune')
    state = StringField('State', validators=[DataRequired()], default='Maharashtra')
    pin_code = StringField('PIN Code', validators=[DataRequired(), Length(max=10)])
    
    latitude = FloatField('Latitude', validators=[DataRequired()], default=18.5204)
    longitude = FloatField('Longitude', validators=[DataRequired()], default=73.8567)
    
    num_buildings = IntegerField('Number of Buildings', default=2)
    num_wings = IntegerField('Number of Wings', default=4)
    num_flats = IntegerField('Number of Flats', default=80)
    total_residents = IntegerField('Total Residents', default=320)
    estimated_daily_waste = FloatField('Estimated Daily Waste (kg)', default=120.0)
    preferred_pickup_time = SelectField('Preferred Pickup Time', choices=[
        ('07:00 AM - 09:00 AM', 'Early Morning (07:00 AM - 09:00 AM)'),
        ('09:00 AM - 11:00 AM', 'Mid Morning (09:00 AM - 11:00 AM)'),
        ('11:00 AM - 01:00 PM', 'Noon (11:00 AM - 01:00 PM)'),
        ('02:00 PM - 04:00 PM', 'Afternoon (02:00 PM - 04:00 PM)')
    ])
    submit = SubmitField('Register Society')
