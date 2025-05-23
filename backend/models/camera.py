from datetime import datetime
from . import db

class Camera(db.Model):
    __tablename__ = 'cameras'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='offline')  # online, offline, error
    ip_address = db.Column(db.String(45))
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    store = db.relationship('Store', backref='cameras')
    detections = db.relationship('Detection', backref='camera', lazy=True)

    def __repr__(self):
        return f'<Camera {self.name}>' 