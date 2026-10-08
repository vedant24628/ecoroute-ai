from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50), default='SUPER_ADMIN')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"admin_{self.id}"


class Society(UserMixin, db.Model):
    __tablename__ = 'societies'
    
    id = db.Column(db.Integer, primary_key=True)
    society_name = db.Column(db.String(150), nullable=False)
    registration_number = db.Column(db.String(100), unique=True, nullable=False)
    secretary_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    landmark = db.Column(db.String(150))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float, nullable=False, default=18.5204)
    longitude = db.Column(db.Float, nullable=False, default=73.8567)
    num_buildings = db.Column(db.Integer, default=1)
    num_wings = db.Column(db.Integer, default=1)
    num_flats = db.Column(db.Integer, default=10)
    total_residents = db.Column(db.Integer, default=40)
    estimated_daily_waste = db.Column(db.Float, default=50.0)
    preferred_pickup_time = db.Column(db.String(50), default='08:00 AM - 10:00 AM')
    photo = db.Column(db.String(255), default='default_society.jpg')
    status = db.Column(db.String(20), default='APPROVED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pickup_requests = db.relationship('PickupRequest', backref='society', lazy=True, cascade="all, delete-orphan")
    collections = db.relationship('Collection', backref='society', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"society_{self.id}"


class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    status = db.Column(db.String(20), default='AVAILABLE') # AVAILABLE, ON_DUTY, OFF_DUTY
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship('Vehicle', backref='driver', lazy=True)
    assignments = db.relationship('Assignment', backref='driver', lazy=True)


class Worker(UserMixin, db.Model):
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.Text)
    status = db.Column(db.String(20), default='AVAILABLE') # AVAILABLE, ASSIGNED, ON_LEAVE, OFFLINE
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship('Vehicle', backref='worker', lazy=True)
    assignments = db.relationship('Assignment', backref='worker', lazy=True)
    collections = db.relationship('Collection', backref='worker', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"worker_{self.id}"


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    capacity_kg = db.Column(db.Float, nullable=False, default=1000.0)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=True)
    gps_device_id = db.Column(db.String(100), unique=True)
    current_lat = db.Column(db.Float, default=18.5204)
    current_lng = db.Column(db.Float, default=73.8567)
    status = db.Column(db.String(30), default='Available') # Available, Assigned, On Route, Collecting, Maintenance, Offline
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignments = db.relationship('Assignment', backref='vehicle', lazy=True)
    collections = db.relationship('Collection', backref='vehicle', lazy=True)
    gps_locations = db.relationship('GPSLocation', backref='vehicle', lazy=True, cascade="all, delete-orphan")


class WasteCategory(db.Model):
    __tablename__ = 'waste_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    color_code = db.Column(db.String(20), default='#43A047')
    recyclable_rate = db.Column(db.Float, default=0.0)
    co2_factor = db.Column(db.Float, default=1.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PickupRequest(db.Model):
    __tablename__ = 'pickup_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    society_id = db.Column(db.Integer, db.ForeignKey('societies.id'), nullable=False)
    request_code = db.Column(db.String(50), unique=True, nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    preferred_slot = db.Column(db.String(50), nullable=False)
    estimated_weight = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='PENDING') # PENDING, ASSIGNED, IN_PROGRESS, COMPLETED, CANCELLED
    urgency_level = db.Column(db.String(20), default='MEDIUM') # LOW, MEDIUM, HIGH, CRITICAL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignment = db.relationship('Assignment', backref='pickup_request', uselist=False, cascade="all, delete-orphan")


class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    pickup_request_id = db.Column(db.Integer, db.ForeignKey('pickup_requests.id'), unique=True, nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    optimized_sequence = db.Column(db.Integer, default=1)
    estimated_eta_minutes = db.Column(db.Integer, default=15)
    status = db.Column(db.String(20), default='DISPATCHED') # DISPATCHED, EN_ROUTE, ARRIVED, COMPLETED

    collection = db.relationship('Collection', backref='assignment', uselist=False, cascade="all, delete-orphan")


class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), unique=True, nullable=False)
    society_id = db.Column(db.Integer, db.ForeignKey('societies.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    total_weight_kg = db.Column(db.Float, nullable=False, default=0.0)
    wet_waste_kg = db.Column(db.Float, default=0.0)
    dry_waste_kg = db.Column(db.Float, default=0.0)
    recyclable_kg = db.Column(db.Float, default=0.0)
    hazardous_kg = db.Column(db.Float, default=0.0)
    image_proof = db.Column(db.Text)
    remarks = db.Column(db.Text)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)

    waste_processing = db.relationship('WasteProcessing', backref='collection', uselist=False, cascade="all, delete-orphan")


class WasteProcessing(db.Model):
    __tablename__ = 'waste_processing'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), unique=True, nullable=False)
    composted_kg = db.Column(db.Float, default=0.0)
    recycled_plastic_kg = db.Column(db.Float, default=0.0)
    recycled_paper_kg = db.Column(db.Float, default=0.0)
    recycled_metal_kg = db.Column(db.Float, default=0.0)
    landfill_kg = db.Column(db.Float, default=0.0)
    co2_saved_kg = db.Column(db.Float, default=0.0)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)


class GPSLocation(db.Model):
    __tablename__ = 'gps_locations'
    
    id = db.Column(db.Integer().with_variant(db.BigInteger(), 'mysql'), primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed_kmh = db.Column(db.Float, default=0.0)
    heading = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class RouteHistory(db.Model):
    __tablename__ = 'route_history'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_distance_km = db.Column(db.Float, default=0.0)
    route_geometry_json = db.Column(db.Text)


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20), nullable=False) # ADMIN, SOCIETY, WORKER
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    actor_type = db.Column(db.String(50), nullable=False)
    actor_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
