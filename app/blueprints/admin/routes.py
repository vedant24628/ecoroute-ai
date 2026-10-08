from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app.models import (db, Admin, Society, Worker, Driver, Vehicle, WasteCategory,
                        PickupRequest, Assignment, Collection, WasteProcessing, SystemSettings)
from app.blueprints.admin.forms import VehicleForm, WorkerForm, DriverForm, AssignmentForm
from app.services.ai_engine import AIEngine
from app.services.pdf_generator import PDFGenerator
from app.services.mail_service import send_registration_approved_email
from sqlalchemy import func
from datetime import datetime, date

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    """Decorator to ensure route is restricted to Super Admin role."""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('Access denied. Super Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_societies = Society.query.count()
    total_workers = Worker.query.count()
    total_vehicles = Vehicle.query.count()
    pending_pickups = PickupRequest.query.filter_by(status='PENDING').count()
    completed_pickups = PickupRequest.query.filter_by(status='COMPLETED').count()
    
    total_waste_kg = db.session.query(func.sum(Collection.total_weight_kg)).scalar() or 0.0
    
    # Calculate recycling rate
    total_recycled = db.session.query(func.sum(Collection.recyclable_kg + Collection.wet_waste_kg)).scalar() or 0.0
    recycling_rate = round((total_recycled / total_waste_kg * 100), 1) if total_waste_kg > 0 else 88.5
    
    recent_pickups = PickupRequest.query.order_by(PickupRequest.created_at.desc()).limit(5).all()
    active_vehicles = Vehicle.query.filter(Vehicle.status.in_(['Assigned', 'On Route', 'Collecting'])).all()

    return render_template(
        'admin/dashboard.html',
        total_societies=total_societies,
        total_workers=total_workers,
        total_vehicles=total_vehicles,
        pending_pickups=pending_pickups,
        completed_pickups=completed_pickups,
        total_waste_kg=round(total_waste_kg, 1),
        recycling_rate=recycling_rate,
        recent_pickups=recent_pickups,
        active_vehicles=active_vehicles
    )

@admin_bp.route('/societies')
@login_required
@admin_required
def societies():
    all_societies = Society.query.order_by(Society.created_at.desc()).all()
    return render_template('admin/societies.html', societies=all_societies)

@admin_bp.route('/societies/approve/<int:society_id>')
@login_required
@admin_required
def approve_society(society_id):
    society = Society.query.get_or_404(society_id)
    society.status = 'APPROVED'
    db.session.commit()
    send_registration_approved_email(society)
    flash(f'Society {society.society_name} has been approved.', 'success')
    return redirect(url_for('admin.societies'))

@admin_bp.route('/vehicles', methods=['GET', 'POST'])
@login_required
@admin_required
def vehicles():
    form = VehicleForm()
    # Populate dropdown choices dynamically
    drivers = Driver.query.all()
    workers = Worker.query.all()
    
    form.driver_id.choices = [(0, '-- None --')] + [(d.id, f"{d.full_name} ({d.license_number})") for d in drivers]
    form.worker_id.choices = [(0, '-- None --')] + [(w.id, f"{w.full_name} ({w.employee_id})") for w in workers]

    if form.validate_on_submit():
        v = Vehicle(
            vehicle_number=form.vehicle_number.data.upper(),
            vehicle_type=form.vehicle_type.data,
            capacity_kg=form.capacity_kg.data,
            driver_id=form.driver_id.data if form.driver_id.data != 0 else None,
            worker_id=form.worker_id.data if form.worker_id.data != 0 else None,
            gps_device_id=form.gps_device_id.data,
            status=form.status.data
        )
        db.session.add(v)
        db.session.commit()
        flash('Vehicle registered successfully.', 'success')
        return redirect(url_for('admin.vehicles'))

    all_vehicles = Vehicle.query.order_by(Vehicle.id.desc()).all()
    return render_template('admin/vehicles.html', vehicles=all_vehicles, form=form)

@admin_bp.route('/workers', methods=['GET', 'POST'])
@login_required
@admin_required
def workers():
    form = WorkerForm()
    if form.validate_on_submit():
        w = Worker(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            employee_id=form.employee_id.data,
            address=form.address.data,
            status=form.status.data
        )
        w.set_password(form.password.data or 'Worker123!')
        db.session.add(w)
        db.session.commit()
        flash('Worker registered successfully.', 'success')
        return redirect(url_for('admin.workers'))

    all_workers = Worker.query.order_by(Worker.id.desc()).all()
    return render_template('admin/workers.html', workers=all_workers, form=form)

@admin_bp.route('/drivers', methods=['GET', 'POST'])
@login_required
@admin_required
def drivers():
    form = DriverForm()
    if form.validate_on_submit():
        d = Driver(
            full_name=form.full_name.data,
            license_number=form.license_number.data,
            phone=form.phone.data,
            email=form.email.data,
            status=form.status.data
        )
        db.session.add(d)
        db.session.commit()
        flash('Driver registered successfully.', 'success')
        return redirect(url_for('admin.drivers'))

    all_drivers = Driver.query.order_by(Driver.id.desc()).all()
    return render_template('admin/drivers.html', drivers=all_drivers, form=form)

@admin_bp.route('/assignments', methods=['GET', 'POST'])
@login_required
@admin_required
def assignments():
    form = AssignmentForm()
    
    pending_pickups = PickupRequest.query.filter_by(status='PENDING').all()
    available_vehicles = Vehicle.query.filter_by(status='Available').all()
    available_workers = Worker.query.filter_by(status='AVAILABLE').all()
    available_drivers = Driver.query.filter_by(status='AVAILABLE').all()

    form.pickup_request_id.choices = [(p.id, f"{p.request_code} - {p.society.society_name} ({p.urgency_level})") for p in pending_pickups]
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number} ({v.vehicle_type})") for v in available_vehicles]
    form.worker_id.choices = [(w.id, f"{w.full_name} ({w.employee_id})") for w in available_workers]
    form.driver_id.choices = [(0, '-- None --')] + [(d.id, f"{d.full_name}") for d in available_drivers]

    if form.validate_on_submit():
        p_req = PickupRequest.query.get_or_404(form.pickup_request_id.data)
        
        # Server-side race condition protection
        vehicle = Vehicle.query.get(form.vehicle_id.data)
        if not vehicle or vehicle.status != 'Available':
            flash('Selected vehicle is no longer available. Please select another vehicle.', 'danger')
            return redirect(url_for('admin.assignments'))
            
        worker = Worker.query.get(form.worker_id.data)
        if not worker or worker.status != 'AVAILABLE':
            flash('Selected worker is no longer available. Please select another worker.', 'danger')
            return redirect(url_for('admin.assignments'))
            
        driver_id = form.driver_id.data if form.driver_id.data != 0 else None
        if driver_id:
            driver = Driver.query.get(driver_id)
            if not driver or driver.status != 'AVAILABLE':
                flash('Selected driver is no longer available. Please select another driver.', 'danger')
                return redirect(url_for('admin.assignments'))
            driver.status = 'ON_DUTY'
        
        assignment = Assignment(
            pickup_request_id=p_req.id,
            vehicle_id=form.vehicle_id.data,
            worker_id=form.worker_id.data,
            driver_id=driver_id,
            estimated_eta_minutes=form.estimated_eta_minutes.data,
            status='DISPATCHED'
        )
        p_req.status = 'ASSIGNED'
        
        # Update statuses
        vehicle.status = 'Assigned'
        worker.status = 'ASSIGNED'

        db.session.add(assignment)
        db.session.commit()
        flash('Vehicle and worker successfully assigned to pickup request.', 'success')
        return redirect(url_for('admin.assignments'))

    all_assignments = Assignment.query.order_by(Assignment.id.desc()).all()
    return render_template('admin/assignments.html', assignments=all_assignments, form=form, pending_pickups=pending_pickups, available_vehicles=available_vehicles, available_workers=available_workers)

@admin_bp.route('/ai-optimize-routes')
@login_required
@admin_required
def ai_optimize_routes():
    """AI Endpoint to optimize current pending pickup routes across all vehicles."""
    pending_pickups = PickupRequest.query.filter_by(status='PENDING').all()
    depot_coords = (18.5204, 73.8567) # City Central Depot
    
    pickup_data = []
    for p in pending_pickups:
        pickup_data.append({
            'id': p.id,
            'name': p.society.society_name,
            'lat': p.society.latitude,
            'lng': p.society.longitude,
            'est_weight': p.estimated_weight or p.society.estimated_daily_waste,
            'urgency': p.urgency_level
        })

    optimization_result = AIEngine.optimize_route(depot_coords, pickup_data)
    return jsonify(optimization_result)

@admin_bp.route('/live-fleet')
@login_required
@admin_required
def live_fleet():
    vehicles = Vehicle.query.all()
    societies = Society.query.all()
    return render_template('admin/live_tracking.html', vehicles=vehicles, societies=societies)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    wet_total = db.session.query(func.sum(Collection.wet_waste_kg)).scalar() or 0.0
    dry_total = db.session.query(func.sum(Collection.dry_waste_kg)).scalar() or 0.0
    recyclable_total = db.session.query(func.sum(Collection.recyclable_kg)).scalar() or 0.0
    hazardous_total = db.session.query(func.sum(Collection.hazardous_kg)).scalar() or 0.0

    impact = AIEngine.calculate_carbon_footprint(wet_total, dry_total, recyclable_total, hazardous_total)
    return render_template('admin/analytics.html', impact=impact)

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    collections = Collection.query.order_by(Collection.collected_at.desc()).all()
    return render_template('admin/reports.html', collections=collections)

@admin_bp.route('/reports/download/<int:collection_id>')
@login_required
@admin_required
def download_report(collection_id):
    col = Collection.query.get_or_404(collection_id)
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
