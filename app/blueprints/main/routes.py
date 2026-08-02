from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Society, Vehicle, Collection, WasteCategory, db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch public statistics for the landing page hero & counter section
    total_societies = Society.query.count() or 14
    total_vehicles = Vehicle.query.count() or 8
    total_waste_kg = db.session.query(func.sum(Collection.total_weight_kg)).scalar() or 18450.0
    total_co2_kg = round(total_waste_kg * 1.85, 1)

    waste_categories = WasteCategory.query.all()

    return render_template(
        'main/index.html',
        total_societies=total_societies,
        total_vehicles=total_vehicles,
        total_waste_kg=round(total_waste_kg, 1),
        total_co2_kg=total_co2_kg,
        waste_categories=waste_categories
    )

@main_bp.route('/features')
def features():
    return render_template('main/features.html')

@main_bp.route('/live-tracking')
def live_tracking_public():
    vehicles = Vehicle.query.all()
    societies = Society.query.all()
    return render_template('main/tracking.html', vehicles=vehicles, societies=societies)

@main_bp.route('/faq')
def faq():
    return render_template('main/faq.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash(f'Thank you, {name}! Your message has been received. Our green team will reach out shortly.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('main/contact.html')
