from datetime import datetime
from . import db

class AIModel(db.Model):
    __tablename__ = 'ai_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    model_path = db.Column(db.String(255), nullable=False)
    config_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=False)
    accuracy = db.Column(db.Float)
    last_trained = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    detections = db.relationship('Detection', backref='model', lazy=True)

    def __repr__(self):
        return f'<AIModel {self.name} v{self.version}>' 