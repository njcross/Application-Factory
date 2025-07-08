from flask import Flask
from .extensions import ma
from .models import db  # Import the db instance from models.py
from .blueprints.mechanics import mechanics_bp  # Import the mechanics blueprint
from .blueprints.tickets import tickets_bp  # Import the tickets blueprint
from .blueprints.customers import customers_bp  # Import the customers blueprint
def create_app(config_name):
    app = Flask(__name__)
    
    # Load configuration from the specified config name
    app.config.from_object(f'config.{config_name}')
    
    # Initialize extensions, blueprints, etc.
    ma.init_app(app)
    db.init_app(app) #adding our db extension to our app
    
    # Register blueprints
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(customers_bp, url_prefix='/customers')

    return app