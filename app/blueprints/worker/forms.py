from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class WasteCollectionForm(FlaskForm):
    wet_waste_kg = FloatField('Organic / Wet Waste (kg)', validators=[DataRequired()], default=25.0)
    dry_waste_kg = FloatField('Dry & Paper Waste (kg)', validators=[DataRequired()], default=15.0)
    recyclable_kg = FloatField('Recyclable Plastic (kg)', validators=[DataRequired()], default=10.0)
    hazardous_kg = FloatField('Hazardous / E-Waste (kg)', validators=[Optional()], default=2.0)
    image_proof = FileField('Upload Waste Verification Photo Proof', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')])
    remarks = TextAreaField('Worker Remarks / Notes', validators=[Optional()])
    submit = SubmitField('Submit Waste Proof & Complete Collection')
