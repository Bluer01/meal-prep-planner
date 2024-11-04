from flask import Flask
from config import Config
from .database import init_app, engine
from .middleware import init_middleware
from .security import limiter

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Load config
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.update(test_config)
    
    # Initialize extensions
    init_app(app)
    limiter.init_app(app)
    init_middleware(app)
    
    # Register blueprints
    from .routes import bp
    app.register_blueprint(bp)
    
    # Create tables
    with app.app_context():
        from .models import Base
        Base.metadata.create_all(bind=engine)
    
    return app