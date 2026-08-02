from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Optional

class SchedulePickupForm(FlaskForm):
    scheduled_date = DateField('Pickup Date', validators=[DataRequired()])
    preferred_slot = SelectField('Preferred Slot', choices=[
        ('07:00 AM - 09:00 AM', 'Morning (07:00 AM - 09:00 AM)'),
        ('09:00 AM - 11:00 AM', 'Mid Morning (09:00 AM - 11:00 AM)'),
        ('11:00 AM - 01:00 PM', 'Noon (11:00 AM - 01:00 PM)'),
        ('02:00 PM - 04:00 PM', 'Afternoon (02:00 PM - 04:00 PM)')
    ], validators=[DataRequired()])
    estimated_weight = FloatField('Estimated Total Waste (kg)', validators=[DataRequired()], default=50.0)
    urgency_level = SelectField('Priority / Urgency', choices=[
        ('LOW', 'Low Priority (Standard schedule)'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority (Overflow expected)'),
        ('CRITICAL', 'Critical (Urgent clear out required)')
    ], default='MEDIUM')
    notes = TextAreaField('Special Instructions / Notes', validators=[Optional()])
    submit = SubmitField('Confirm Pickup Request')
