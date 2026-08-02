from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

class VehicleForm(FlaskForm):
    vehicle_number = StringField('Vehicle Registration Number', validators=[DataRequired()])
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('Electric Tipper Truck', 'Electric Tipper Truck (Zero Emission)'),
        ('Hydraulic Waste Compactor', 'Hydraulic Waste Compactor'),
        ('Mini Collection Van', 'Mini Collection Van'),
        ('Heavy Duty Bio-Truck', 'Heavy Duty Bio-Truck')
    ])
    capacity_kg = FloatField('Payload Capacity (kg)', validators=[DataRequired()], default=1500.0)
    driver_id = SelectField('Assigned Driver', coerce=int, validators=[Optional()])
    worker_id = SelectField('Assigned Worker', coerce=int, validators=[Optional()])
    gps_device_id = StringField('GPS Telemetry ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Available', 'Available'),
        ('Assigned', 'Assigned'),
        ('On Route', 'On Route'),
        ('Collecting', 'Collecting'),
        ('Maintenance', 'Maintenance'),
        ('Offline', 'Offline')
    ])
    submit = SubmitField('Save Vehicle')


class WorkerForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Optional()])
    address = TextAreaField('Address')
    status = SelectField('Status', choices=[
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('ON_LEAVE', 'On Leave'),
        ('OFFLINE', 'Offline')
    ])
    submit = SubmitField('Save Worker')


class DriverForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    license_number = StringField('Driving License Number', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email Address', validators=[Optional(), Email()])
    status = SelectField('Status', choices=[
        ('AVAILABLE', 'Available'),
        ('ON_DUTY', 'On Duty'),
        ('OFF_DUTY', 'Off Duty')
    ])
    submit = SubmitField('Save Driver')


class AssignmentForm(FlaskForm):
    pickup_request_id = SelectField('Pickup Request', coerce=int, validators=[DataRequired()])
    vehicle_id = SelectField('Select Vehicle', coerce=int, validators=[DataRequired()])
    worker_id = SelectField('Select Worker', coerce=int, validators=[DataRequired()])
    driver_id = SelectField('Select Driver', coerce=int, validators=[Optional()])
    estimated_eta_minutes = IntegerField('Estimated ETA (Minutes)', default=15)
    submit = SubmitField('Dispatch & Assign')
