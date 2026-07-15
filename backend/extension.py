# backend/extensions.py
from flask_caching import Cache

cache = Cache()

def init_extension(app):
    """Initialize all extensions with app"""
    cache.init_app(app)