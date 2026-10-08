import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from config import Config
from app.models import db, Admin, Society, Worker

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")

@login_manager.user_loader
def load_user(user_id):
    if not user_id or '_' not in user_id:
        return None
    try:
        role, id_str = user_id.split('_', 1)
        uid = int(id_str)
        if role == 'admin':
            return Admin.query.get(uid)
        elif role == 'society':
            return Society.query.get(uid)
        elif role == 'worker':
            return Worker.query.get(uid)
    except Exception:
        return None
    return None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass  # Read-only file system on Vercel/serverless environments

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    # Context Processor for system variables & active user role
    @app.context_processor
    def inject_global_vars():
        return {
            'app_name': 'EcoRoute AI',
            'motto': 'Smarter Routes. Cleaner Communities.'
        }

    # Register Blueprints
    from app.blueprints.main.routes import main_bp
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.society.routes import society_bp
    from app.blueprints.worker.routes import worker_bp
    from app.blueprints.api.routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(society_bp, url_prefix='/society')
    app.register_blueprint(worker_bp, url_prefix='/worker')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create tables only for SQLite development/fallback
    with app.app_context():
        if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
            try:
                db.create_all()
            except Exception:
                pass
        else:
            # Safely upgrade TiDB production schema to store compressed Base64 images
            try:
                from sqlalchemy import text
                db.session.execute(text('ALTER TABLE collections MODIFY image_proof MEDIUMTEXT'))
                db.session.commit()
            except Exception:
                db.session.rollback()

    return app
