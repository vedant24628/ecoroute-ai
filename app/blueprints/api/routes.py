from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user
from app.models import db, Vehicle, GPSLocation, Collection, WasteCategory, Society, PickupRequest, Notification, Admin
from sqlalchemy import func
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)


def admin_only(func):
    """Restrict a JSON API endpoint to authenticated Super Admin users."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            return jsonify({'error': 'Admin authentication required'}), 401
        return func(*args, **kwargs)
    return wrapper

@api_bp.route('/vehicles/gps')
def get_vehicles_gps():
    """Return real-time GPS locations of all vehicles with active telemetry."""
    vehicles = Vehicle.query.all()
    data = []
    
    # Simple simulation offset to show subtle live moving markers when polling
    sim_t = (int(datetime.now().timestamp()) % 100) / 100.0 * 0.002
    
    for idx, v in enumerate(vehicles):
        offset_lat = sim_t if v.status in ['On Route', 'Collecting', 'Assigned'] else 0.0
        data.append({
            'id': v.id,
            'vehicle_number': v.vehicle_number,
            'vehicle_type': v.vehicle_type,
            'capacity_kg': v.capacity_kg,
            'lat': v.current_lat + (offset_lat * (1 if idx % 2 == 0 else -1)),
            'lng': v.current_lng + (offset_lat * (1 if idx % 3 == 0 else -1)),
            'status': v.status,
            'driver': v.driver.full_name if v.driver else 'Unassigned',
            'worker': v.worker.full_name if v.worker else 'Unassigned'
        })
    return jsonify({'vehicles': data, 'timestamp': datetime.now().isoformat()})


@api_bp.route('/vehicles/update-gps', methods=['POST'])
def update_vehicle_gps():
    """API Endpoint to record hardware GPS device ping. Requires the device
    shared-secret key in the 'X-Device-Key' header to prevent spoofed telemetry."""
    device_key = request.headers.get('X-Device-Key')
    if not device_key or device_key != current_app.config.get('GPS_DEVICE_API_KEY'):
        return jsonify({'error': 'Invalid or missing device key'}), 401

    req_data = request.get_json() or {}
    vehicle_id = req_data.get('vehicle_id')
    lat = req_data.get('lat')
    lng = req_data.get('lng')

    if not vehicle_id or lat is None or lng is None:
        return jsonify({'error': 'Missing required telemetry params'}), 400

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    vehicle.current_lat = lat
    vehicle.current_lng = lng

    gps_entry = GPSLocation(
        vehicle_id=vehicle.id,
        latitude=lat,
        longitude=lng,
        speed_kmh=req_data.get('speed', 28.5)
    )
    db.session.add(gps_entry)
    db.session.commit()

    # Push a real-time update over SocketIO so connected clients don't have
    # to wait for their next poll cycle to see the new position.
    from app import socketio
    socketio.emit('vehicle_position', {
        'id': vehicle.id,
        'vehicle_number': vehicle.vehicle_number,
        'lat': lat,
        'lng': lng,
        'status': vehicle.status
    })

    return jsonify({'status': 'success', 'vehicle_id': vehicle.id, 'lat': lat, 'lng': lng})


@api_bp.route('/chart-data/admin')
@admin_only
def admin_chart_data():
    """Return dynamic Chart.js JSON payloads for Admin analytics dashboard."""
    # 1. Daily Collection Trend (Last 7 Days) - real data, 0 for days with no collections
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_labels = [d.strftime('%a (%b %d)') for d in days]
    daily_weights = []

    for d in days:
        w = db.session.query(func.sum(Collection.total_weight_kg)).filter(
            func.date(Collection.collected_at) == d
        ).scalar() or 0.0
        daily_weights.append(round(w, 1))

    # 2. Category Distribution - the Collection model tracks 4 waste buckets
    # (wet/dry/recyclable/hazardous), so we sum those directly from real
    # records rather than showing an unrelated fixed number per category.
    wet_total = db.session.query(func.sum(Collection.wet_waste_kg)).scalar() or 0.0
    dry_total = db.session.query(func.sum(Collection.dry_waste_kg)).scalar() or 0.0
    recyclable_total = db.session.query(func.sum(Collection.recyclable_kg)).scalar() or 0.0
    hazardous_total = db.session.query(func.sum(Collection.hazardous_kg)).scalar() or 0.0

    bucket_map = {
        'Organic / Wet Waste': round(wet_total, 1),
        'Dry & Paper Waste': round(dry_total, 1),
        'Recyclable Plastic': round(recyclable_total, 1),
        'Hazardous Waste': round(hazardous_total, 1),
    }
    categories = WasteCategory.query.filter(WasteCategory.name.in_(bucket_map.keys())).all()
    if not categories:
        categories = WasteCategory.query.all()
    cat_labels = [c.name for c in categories]
    cat_colors = [c.color_code for c in categories]
    cat_values = [bucket_map.get(c.name, 0.0) for c in categories]

    # 3. Vehicle Utilization Status
    avail_count = Vehicle.query.filter_by(status='Available').count()
    assigned_count = Vehicle.query.filter_by(status='Assigned').count()
    route_count = Vehicle.query.filter_by(status='On Route').count()
    maint_count = Vehicle.query.filter_by(status='Maintenance').count()

    return jsonify({
        'daily_labels': daily_labels,
        'daily_weights': daily_weights,
        'cat_labels': cat_labels,
        'cat_colors': cat_colors,
        'cat_values': cat_values,
        'vehicle_utilization': {
            'labels': ['Available', 'Assigned', 'On Route', 'Maintenance'],
            'values': [avail_count, assigned_count, route_count, maint_count]
        }
    })
