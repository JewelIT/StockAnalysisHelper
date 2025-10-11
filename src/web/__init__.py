"""
Vestor - AI Financial Advisor Application
Flask application factory and initialization
"""
from flask import Flask
import os

def create_app(config=None):
    """Application factory pattern"""
    # Paths relative to project root (2 levels up from src/web/)
    import os.path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    app = Flask(__name__, 
                template_folder=os.path.join(project_root, 'templates'),
                static_folder=os.path.join(project_root, 'static'))
    
    # Configuration
    app.config['EXPORTS_FOLDER'] = 'exports'
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    if config:
        app.config.update(config)
    
    # Ensure exports folder exists
    os.makedirs(app.config['EXPORTS_FOLDER'], exist_ok=True)
    
    # Register blueprints - still in old location temporarily
    from app.routes import analysis, chat, main
    app.register_blueprint(main.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(chat.bp)
    
    return app
