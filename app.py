
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from credential_loader import load_credentials_from_json, get_credential

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load credentials from JSON file
credentials = load_credentials_from_json()

class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key-change-in-production"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# -------------------------------
# Database Configuration (MySQL or PostgreSQL)
# -------------------------------

# Try MySQL first (from JSON credentials), then fallback to PostgreSQL
mysql_config = {
    'host': get_credential(credentials, 'MYSQL_HOST', 'localhost'),
    'port': get_credential(credentials, 'MYSQL_PORT', '3306'),
    'user': get_credential(credentials, 'MYSQL_USER', 'root'),
    'password': get_credential(credentials, 'MYSQL_PASSWORD', 'root123'),
    'database': get_credential(credentials, 'MYSQL_DATABASE', 'it_lobby')
}

# Check if we have a custom DATABASE_URL from JSON
database_url_from_json = get_credential(credentials, 'DATABASE_URL')

try:
    if database_url_from_json:
        # Use DATABASE_URL from JSON credentials
        database_url = database_url_from_json
        logging.info(f"Using DATABASE_URL from JSON credentials")
        db_type = "mysql" if "mysql" in database_url else "postgresql"
    elif mysql_config['host'] != 'localhost' or credentials:
        # Use MySQL configuration from JSON
        database_url = (
            f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}"
            f"@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
        )
        logging.info(f"Using MySQL database from JSON credentials: {mysql_config['host']}")
        db_type = "mysql"
    else:
        # Fallback to Replit's PostgreSQL database
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("No database configuration found")
        logging.info(f"Using PostgreSQL database: {database_url.split('@')[0]}@...")
        db_type = "postgresql"

    from sqlalchemy import create_engine, text
    test_engine = create_engine(database_url, connect_args={'connect_timeout': 5})
    with test_engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    logging.info(f"✅ {db_type.upper()} database connection successful")

except Exception as e:
    logging.error(f"❌ Database connection failed: {e}")
    # If MySQL from JSON fails, try PostgreSQL fallback
    from sqlalchemy import create_engine, text
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            logging.info("Trying PostgreSQL fallback...")
            test_engine = create_engine(database_url, connect_args={'connect_timeout': 5})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_recycle": 300,
                "pool_pre_ping": True,
                "pool_size": 10,
                "max_overflow": 20
            }
            db_type = "postgresql"
            logging.info("✅ PostgreSQL fallback connection successful")
        else:
            raise SystemExit("No working database configuration found")
    except Exception as fallback_error:
        logging.error(f"❌ PostgreSQL fallback also failed: {fallback_error}")
        raise SystemExit("Database connection failed. Please check database settings.")

# Store database type
app.config["DB_TYPE"] = db_type

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# SAP B1 Configuration (from JSON credentials)
app.config['SAP_B1_SERVER'] = get_credential(credentials, 'SAP_B1_SERVER', 'https://10.112.253.173:50000')
app.config['SAP_B1_USERNAME'] = get_credential(credentials, 'SAP_B1_USERNAME', 'manager')
app.config['SAP_B1_PASSWORD'] = get_credential(credentials, 'SAP_B1_PASSWORD', '1422')
app.config['SAP_B1_COMPANY_DB'] = get_credential(credentials, 'SAP_B1_COMPANY_DB', 'SBODemoUS')

# Log SAP B1 configuration (without password)
logging.info(f"SAP B1 Server: {app.config['SAP_B1_SERVER']}")
logging.info(f"SAP B1 Username: {app.config['SAP_B1_USERNAME']}")
logging.info(f"SAP B1 Company DB: {app.config['SAP_B1_COMPANY_DB']}")

# Import models
import models
import models_extensions
from modules.invoice_creation import models as invoice_models  # noqa: F401

with app.app_context():
    # Create tables
    db.create_all()
    logging.info("✅ Database tables created")

    # Drop unique constraint if exists (PostgreSQL version)
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_schema = 'public' 
                AND table_name = 'serial_number_transfer_serials' 
                AND constraint_name = 'unique_serial_per_item'
            """))
            if result.fetchone():
                conn.execute(text("ALTER TABLE serial_number_transfer_serials DROP CONSTRAINT unique_serial_per_item"))
                conn.commit()
                logging.info("Dropped unique_serial_per_item constraint")
    except Exception as e:
        logging.warning(f"⚠️ Could not drop unique constraint: {e}")

    # Create default data
    try:
        from models_extensions import Branch
        from werkzeug.security import generate_password_hash
        from models import User

        default_branch = Branch.query.filter_by(id='BR001').first()
        if not default_branch:
            default_branch = Branch(
                id='BR001',
                name='Main Branch',
                branch_code='BR001',
                branch_name='Main Branch',
                description='Main Office Branch',
                address='Main Office',
                phone='123-456-7890',
                email='main@company.com',
                manager_name='Branch Manager',
                active=True,
                is_default=True
            )
            db.session.add(default_branch)
            logging.info("✅ Default branch created")

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@company.com',
                password_hash=generate_password_hash('admin123'),
                first_name='System',
                last_name='Administrator',
                role='admin',
                branch_id='BR001',
                branch_name='Main Branch',
                default_branch_id='BR001',
                active=True,
                must_change_password=False
            )
            db.session.add(admin)
            logging.info("✅ Default admin user created")

        db.session.commit()
        logging.info("✅ Default data initialized")

    except Exception as e:
        logging.error(f"❌ Error initializing default data: {e}")
        db.session.rollback()

# Setup logging
try:
    from logging_config import setup_logging
    logger = setup_logging(app)
    logger.info("🚀 WMS Application starting with file-based logging")
except Exception as e:
    logging.warning(f"⚠️ Logging setup failed: {e}. Using basic logging.")

# Register blueprints
from modules.inventory_transfer.routes import transfer_bp
from modules.serial_item_transfer.routes import serial_item_bp
from modules.invoice_creation.routes import invoice_bp

app.register_blueprint(transfer_bp)
app.register_blueprint(serial_item_bp)
app.register_blueprint(invoice_bp)

# Import routes
import routes

