from datetime import datetime
from . import db

class Detection(db.Model):
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=False)
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    confidence = db.Column(db.Float, nullable=False)  # Detection confidence score
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)  # Whether this detection has been added to cart
    
    # Relationships
    product = db.relationship('Product')
    ai_model = db.relationship('AIModel')
    
    def to_dict(self):
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'processed': self.processed
        } 