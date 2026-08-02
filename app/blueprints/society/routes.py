import random
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from app.models import db, Society, PickupRequest, Assignment, Collection, Notification, Vehicle
from app.blueprints.society.forms import SchedulePickupForm
from app.services.ai_engine import AIEngine
from app.services.pdf_generator import PDFGenerator
from sqlalchemy import func
from datetime import datetime, date

society_bp = Blueprint('society', __name__)

def society_required(func):
    """Decorator to restrict access to Society Secretary role."""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Society):
            flash('Please log in as a Society Secretary.', 'warning')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@society_bp.route('/dashboard')
@login_required
@society_required
def dashboard():
    society = current_user
    pickups = PickupRequest.query.filter_by(society_id=society.id).order_by(PickupRequest.created_at.desc()).all()
    collections = Collection.query.filter_by(society_id=society.id).all()
    
    total_waste = sum(c.total_weight_kg for c in collections) or 0.0
    wet_waste = sum(c.wet_waste_kg for c in collections) or 0.0
    dry_waste = sum(c.dry_waste_kg for c in collections) or 0.0
    plastic_waste = sum(c.recyclable_kg for c in collections) or 0.0
    hazardous_waste = sum(c.hazardous_kg for c in collections) or 0.0
    
    # Calculate carbon footprint
    carbon_impact = AIEngine.calculate_carbon_footprint(wet_waste, dry_waste, plastic_waste, hazardous_waste)
    
    # AI Forecast for next 7 days
    ai_forecast = AIEngine.predict_society_waste(
        total_residents=society.total_residents,
        num_flats=society.num_flats,
        historical_avg_kg=society.estimated_daily_waste
    )

    # Check active vehicle tracking
    active_assignment = None
    for p in pickups:
        if p.status in ['ASSIGNED', 'IN_PROGRESS'] and p.assignment:
            active_assignment = p.assignment
            break

    return render_template(
        'society/dashboard.html',
        society=society,
        pickups=pickups[:5],
        total_pickups=len(pickups),
        total_waste=round(total_waste, 1),
        carbon_impact=carbon_impact,
        ai_forecast=ai_forecast,
        active_assignment=active_assignment
    )

@society_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
@society_required
def schedule():
    form = SchedulePickupForm()
    if request.method == 'GET' and not form.scheduled_date.data:
        form.scheduled_date.data = date.today()

    if form.validate_on_submit():
        req_code = f"REQ-{random.randint(10000, 99999)}"
        new_req = PickupRequest(
            society_id=current_user.id,
            request_code=req_code,
            scheduled_date=form.scheduled_date.data,
            preferred_slot=form.preferred_slot.data,
            estimated_weight=form.estimated_weight.data,
            urgency_level=form.urgency_level.data,
            notes=form.notes.data,
            status='PENDING'
        )
        db.session.add(new_req)
        db.session.commit()
        flash(f'Pickup request {req_code} submitted successfully!', 'success')
        return redirect(url_for('society.dashboard'))

    return render_template('society/schedule.html', form=form)

@society_bp.route('/history')
@login_required
@society_required
def history():
    collections = Collection.query.filter_by(society_id=current_user.id).order_by(Collection.collected_at.desc()).all()
    return render_template('society/history.html', collections=collections)

@society_bp.route('/track')
@login_required
@society_required
def tracking():
    # Find active assignment for this society
    assignment = Assignment.query.join(PickupRequest).filter(
        PickupRequest.society_id == current_user.id,
        Assignment.status.in_(['DISPATCHED', 'EN_ROUTE', 'ARRIVED'])
    ).first()

    return render_template('society/tracking.html', assignment=assignment, society=current_user)

@society_bp.route('/carbon-report')
@login_required
@society_required
def carbon_report():
    collections = Collection.query.filter_by(society_id=current_user.id).all()
    wet_waste = sum(c.wet_waste_kg for c in collections) or 0.0
    dry_waste = sum(c.dry_waste_kg for c in collections) or 0.0
    plastic_waste = sum(c.recyclable_kg for c in collections) or 0.0
    hazardous_waste = sum(c.hazardous_kg for c in collections) or 0.0

    impact = AIEngine.calculate_carbon_footprint(wet_waste, dry_waste, plastic_waste, hazardous_waste)
    return render_template('society/carbon.html', impact=impact, society=current_user)

@society_bp.route('/history/download/<int:collection_id>')
@login_required
@society_required
def download_report(collection_id):
    """Society-scoped PDF download so secretaries aren't blocked by the admin-only route."""
    col = Collection.query.get_or_404(collection_id)
    if col.society_id != current_user.id:
        flash('You are not authorized to view this report.', 'danger')
        return redirect(url_for('society.history'))

    c_data = {
        'id': col.id,
        'society_name': col.society.society_name,
        'collected_at': col.collected_at.strftime('%Y-%m-%d %H:%M'),
        'worker_name': col.worker.full_name,
        'vehicle_number': col.vehicle.vehicle_number,
        'wet_waste_kg': col.wet_waste_kg,
        'dry_waste_kg': col.dry_waste_kg,
        'recyclable_kg': col.recyclable_kg,
        'hazardous_kg': col.hazardous_kg,
        'total_weight_kg': col.total_weight_kg,
        'co2_saved': col.total_weight_kg * 1.85
    }
    pdf_buffer = PDFGenerator.generate_collection_report(c_data)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"EcoRoute_Collection_Report_{col.id}.pdf",
        mimetype='application/pdf'
    )
