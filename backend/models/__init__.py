"""
Models package initialization.
This file makes the models directory a Python package.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import all models
from backend.models.user import User
from backend.models.product import Product
from backend.models.cart import Cart
from backend.models.cart_item import CartItem
from backend.models.detection import Detection
from backend.models.store import Store
from backend.models.camera import Camera
from backend.models.ai_model import AIModel
from backend.models.item import Item
from backend.models.item_location import ItemLocation
from backend.models.category import Category

# Make models available at package level
__all__ = [
    'db',
    'User',
    'Product',
    'Cart',
    'CartItem',
    'Detection',
    'Store',
    'Camera',
    'AIModel',
    'Item',
    'ItemLocation',
    'Category'
] 