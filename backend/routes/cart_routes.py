from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, Cart, CartItem, Product

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/api/cart/start', methods=['POST'])
@jwt_required()
def start_cart():
    """Start a new cart session"""
    data = request.get_json()
    cart_id = data.get('cart_id')
    
    if not cart_id:
        return jsonify({'error': 'Cart ID is required'}), 400
        
    # Check if cart exists and is available
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    if cart and cart.status != 'inactive':
        return jsonify({'error': 'Cart is already in use'}), 400
        
    if not cart:
        cart = Cart(cart_id=cart_id)
        
    # Assign cart to user
    cart.user_id = get_jwt_identity()
    cart.status = 'active'
    
    db.session.add(cart)
    db.session.commit()
    
    return jsonify(cart.to_dict()), 201

@cart_bp.route('/api/cart/<cart_id>', methods=['GET'])
@jwt_required()
def get_cart(cart_id):
    """Get cart details"""
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
        
    return jsonify(cart.to_dict()), 200

@cart_bp.route('/api/cart/<cart_id>/items', methods=['POST'])
@jwt_required()
def add_item(cart_id):
    """Add item to cart"""
    data = request.get_json()
    
    if not all(k in data for k in ('product_id', 'quantity')):
        return jsonify({'error': 'Missing required fields'}), 400
        
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
        
    if cart.status != 'active':
        return jsonify({'error': 'Cart is not active'}), 400
        
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    # Check if item already exists in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += data['quantity']
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=data['quantity'],
            price=product.price
        )
        db.session.add(cart_item)
    
    # Update cart total
    cart.total_amount = sum(item.price * item.quantity for item in cart.items)
    
    db.session.commit()
    
    return jsonify(cart.to_dict()), 200

@cart_bp.route('/api/cart/<cart_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_item(cart_id, item_id):
    """Remove item from cart"""
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
        
    if cart.status != 'active':
        return jsonify({'error': 'Cart is not active'}), 400
        
    cart_item = CartItem.query.get(item_id)
    if not cart_item or cart_item.cart_id != cart.id:
        return jsonify({'error': 'Item not found in cart'}), 404
        
    db.session.delete(cart_item)
    
    # Update cart total
    cart.total_amount = sum(item.price * item.quantity for item in cart.items)
    
    db.session.commit()
    
    return jsonify(cart.to_dict()), 200

@cart_bp.route('/api/cart/<cart_id>/complete', methods=['POST'])
@jwt_required()
def complete_cart(cart_id):
    """Complete cart checkout"""
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
        
    if cart.status != 'active':
        return jsonify({'error': 'Cart is not active'}), 400
        
    cart.status = 'completed'
    db.session.commit()
    
    return jsonify(cart.to_dict()), 200 