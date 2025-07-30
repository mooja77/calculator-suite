from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
redis_client = None

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///calculator.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['GA_TRACKING_ID'] = os.environ.get('GA_TRACKING_ID', '')
    app.config['ADSENSE_CLIENT'] = os.environ.get('ADSENSE_CLIENT', '')
    
    # Security configuration
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow for development
    
    # Rate limiting configuration
    app.config['RATELIMIT_STORAGE_URL'] = app.config['REDIS_URL']
    app.config['RATELIMIT_DEFAULT'] = "100/minute"
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Initialize Redis
    global redis_client
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        redis_client.ping()
    except:
        redis_client = None
        print("Warning: Redis not available, caching disabled")
    
    # Import models to ensure they're registered
    from app import models
    
    # Import calculators to register them
    from app.calculators import percentage, paycheck, sip, rentvsbuy, studentloan, retirement401k
    
    # Import services to initialize them
    from app.services import currency, localization
    from app.services.i18n import i18n_service
    
    # Initialize i18n service
    with app.app_context():
        i18n_service.initialize_translations()
    
    # Initialize localization middleware
    from app.middleware.localization import localization_middleware
    from app.middleware.i18n_middleware import i18n_middleware
    localization_middleware.init_app(app)
    i18n_middleware.init_app(app)
    
    # Register template helpers
    from app.template_helpers.i18n_helpers import register_i18n_helpers
    register_i18n_helpers(app)
    
    # Register blueprints
    from app.routes import main
    from app.routes.i18n_routes import i18n_routes
    app.register_blueprint(main)
    app.register_blueprint(i18n_routes)
    
    # Register API blueprints
    from app.api.global_routes import global_api
    from app.api.health import health_api
    from app.api.i18n_routes import i18n_bp
    app.register_blueprint(global_api)
    app.register_blueprint(health_api)
    app.register_blueprint(i18n_bp)
    
    # Add security headers
    from app.security import security_headers
    
    @app.after_request
    def add_security_headers(response):
        return security_headers(response)
    
    return app