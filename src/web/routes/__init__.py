"""
Routes package initialization
"""
# Import all route blueprints for easy registration
from src.web.routes import main, analysis, chat

__all__ = ['main', 'analysis', 'chat']
