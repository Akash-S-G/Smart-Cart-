from datetime import datetime
from . import db

class Cart(db.Model):
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.String(50), unique=True, nullable=False)  # Physical cart identifier
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='inactive')  # inactive, active, completed
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('carts', lazy=True))
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    detections = db.relationship('Detection', backref='cart_ref', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        } 