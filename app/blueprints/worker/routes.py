import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Worker, Assignment, Collection, WasteProcessing, Vehicle, PickupRequest
from app.blueprints.worker.forms import WasteCollectionForm
from datetime import datetime

worker_bp = Blueprint('worker', __name__)

def worker_required(func):
    """Decorator to restrict access to Worker role."""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Worker):
            flash('Please log in as a Collection Worker.', 'warning')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@worker_bp.route('/dashboard')
@login_required
@worker_required
def dashboard():
    worker = current_user
    assignments = Assignment.query.filter_by(worker_id=worker.id).order_by(Assignment.assigned_at.desc()).all()
    
    # Active assignment
    active_assignment = Assignment.query.filter_by(worker_id=worker.id, status='DISPATCHED').first() or \
                        Assignment.query.filter_by(worker_id=worker.id, status='EN_ROUTE').first()
                        
    completed_collections = Collection.query.filter_by(worker_id=worker.id).all()
    total_collected_kg = sum(c.total_weight_kg for c in completed_collections) or 0.0

    return render_template(
        'worker/dashboard.html',
        worker=worker,
        assignments=assignments,
        active_assignment=active_assignment,
        completed_count=len(completed_collections),
        total_collected_kg=round(total_collected_kg, 1)
    )

@worker_bp.route('/navigate/<int:assignment_id>')
@login_required
@worker_required
def navigate(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.worker_id != current_user.id:
        flash('Unauthorized task navigation.', 'danger')
        return redirect(url_for('worker.dashboard'))

    # Update status to EN_ROUTE
    if assignment.status == 'DISPATCHED':
        assignment.status = 'EN_ROUTE'
        db.session.commit()

    return render_template('worker/navigation.html', assignment=assignment)

@worker_bp.route('/collect/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@worker_required
def collect(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.worker_id != current_user.id:
        flash('Unauthorized task access.', 'danger')
        return redirect(url_for('worker.dashboard'))

    form = WasteCollectionForm()
    if form.validate_on_submit():
        wet = form.wet_waste_kg.data or 0.0
        dry = form.dry_waste_kg.data or 0.0
        plastic = form.recyclable_kg.data or 0.0
        haz = form.hazardous_kg.data or 0.0
        total = wet + dry + plastic + haz

        filename = 'default_proof.jpg'
        
        # New client-side compressed Base64 flow
        base64_data = request.form.get('image_proof_base64')
        if base64_data and base64_data.startswith('data:image'):
            filename = base64_data
        elif form.image_proof.data:
            # Fallback for old flow or local testing if JS is disabled
            file = form.image_proof.data
            original_name = secure_filename(file.filename or '')
            if original_name:
                ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
                filename = f"proof_{assignment.id}_{int(datetime.now().timestamp())}.{ext}"
                try:
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(upload_path)
                except OSError:
                    pass # Ignore read-only FS error on Vercel

        collection = Collection(
            assignment_id=assignment.id,
            society_id=assignment.pickup_request.society_id,
            worker_id=current_user.id,
            vehicle_id=assignment.vehicle_id,
            wet_waste_kg=wet,
            dry_waste_kg=dry,
            recyclable_kg=plastic,
            hazardous_kg=haz,
            total_weight_kg=total,
            image_proof=filename,
            remarks=form.remarks.data
        )

        # Update assignment and pickup status to COMPLETED
        assignment.status = 'COMPLETED'
        assignment.pickup_request.status = 'COMPLETED'
        
        # Vehicle status back to Available
        if assignment.vehicle:
            assignment.vehicle.status = 'Available'

        # Waste processing entry calculation
        wp = WasteProcessing(
            collection=collection,
            composted_kg=round(wet * 0.92, 2),
            recycled_plastic_kg=round(plastic * 0.85, 2),
            recycled_paper_kg=round(dry * 0.88, 2),
            recycled_metal_kg=round(haz * 0.40, 2),
            landfill_kg=round(total * 0.10, 2),
            co2_saved_kg=round(total * 1.85, 2)
        )

        db.session.add(collection)
        db.session.add(wp)
        db.session.commit()

        flash('Waste collection proof uploaded and trip completed successfully!', 'success')
        return redirect(url_for('worker.dashboard'))

    return render_template('worker/upload_collection.html', form=form, assignment=assignment)
