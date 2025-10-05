"""
Routes package initialization
"""
# Import all route blueprints for easy registration
from app.routes import main, analysis, chat

__all__ = ['main', 'analysis', 'chat']
