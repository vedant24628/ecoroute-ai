import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    if os.environ.get('VERCEL'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
        GPS_DEVICE_API_KEY = os.environ.get('GPS_DEVICE_API_KEY')
    else:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-do-not-use-in-prod')
        GPS_DEVICE_API_KEY = os.environ.get('GPS_DEVICE_API_KEY', 'dev-gps-key-do-not-use-in-prod')
    # TiDB / MySQL Configuration
    TIDB_HOST = os.environ.get('TIDB_HOST')
    TIDB_PORT = os.environ.get('TIDB_PORT', '4000')
    TIDB_USER = os.environ.get('TIDB_USER')
    TIDB_PASSWORD = os.environ.get('TIDB_PASSWORD')
    TIDB_DATABASE = os.environ.get('TIDB_DATABASE', 'ecoroute')
    
    if TIDB_HOST and TIDB_USER and TIDB_PASSWORD:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}"
        
        # Production-safe connection pooling for Serverless/TiDB
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {
                'ssl': {'ssl_cert_reqs': 'CERT_REQUIRED'}
            }
        }
        
        ca_path = os.environ.get('TIDB_CA_PATH')
        if ca_path:
            SQLALCHEMY_ENGINE_OPTIONS['connect_args']['ssl']['ca'] = ca_path
            
    elif not os.environ.get('VERCEL'):
        # Local development fallback to SQLite ONLY IF not on Vercel
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'ecoroute.db')
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        # Fail loudly in production if TiDB credentials are missing
        raise RuntimeError("CRITICAL: TiDB credentials are missing in production. SQLite fallback is disabled.")
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Shared secret for hardware GPS device telemetry pings
    # so it can't use Flask-Login sessions). Devices must send this in the
    # 'X-Device-Key' header when POSTing to /api/vehicles/update-gps.

    # Upload folder
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # Flask-Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME', 'noreply@ecoroute.ai')
