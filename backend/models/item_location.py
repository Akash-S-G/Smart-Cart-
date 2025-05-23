from datetime import datetime
from . import db

class ItemLocation(db.Model):
    __tablename__ = 'item_locations'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    aisle_number = db.Column(db.Integer)
    shelf_number = db.Column(db.Integer)
    section = db.Column(db.String(50))
    position_x = db.Column(db.Float)
    position_y = db.Column(db.Float)
    in_stock = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<ItemLocation {self.item_id} at Store {self.store_id}>' 