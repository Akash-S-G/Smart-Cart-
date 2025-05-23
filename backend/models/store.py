from datetime import datetime
from . import db

class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    layout_image = db.Column(db.String(255))
    layout_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    cameras = db.relationship('Camera', backref='store', lazy=True)
    item_locations = db.relationship('ItemLocation', backref='store', lazy=True)

    def __repr__(self):
        return f'<Store {self.name}>' 