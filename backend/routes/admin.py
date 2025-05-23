from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models import Store, Camera, AIModel, User, db, Cart, Product
from functools import wraps
import os
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Store management
@admin_bp.route('/stores', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def manage_stores():
    if request.method == 'POST':
        data = request.get_json()
        
        if not all(k in data for k in ['name', 'address', 'latitude', 'longitude']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        store = Store(
            name=data['name'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        db.session.add(store)
        db.session.commit()
        
        return jsonify({
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'latitude': store.latitude,
            'longitude': store.longitude
        }), 201
    
    # GET method
    stores = Store.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'address': s.address,
        'latitude': s.latitude,
        'longitude': s.longitude,
        'is_active': s.is_active,
        'camera_count': len(s.cameras)
    } for s in stores]), 200

# Camera management
@admin_bp.route('/cameras', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def manage_cameras():
    if request.method == 'POST':
        data = request.get_json()
        
        if not all(k in data for k in ['store_id', 'name', 'ip_address']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        store = Store.query.get(data['store_id'])
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        camera = Camera(
            store_id=data['store_id'],
            name=data['name'],
            ip_address=data['ip_address']
        )
        db.session.add(camera)
        db.session.commit()
        
        return jsonify({
            'id': camera.id,
            'store_id': camera.store_id,
            'name': camera.name,
            'ip_address': camera.ip_address,
            'status': camera.status
        }), 201
    
    # GET method
    store_id = request.args.get('store_id')
    query = Camera.query
    if store_id:
        query = query.filter_by(store_id=store_id)
    
    cameras = query.all()
    return jsonify([{
        'id': c.id,
        'store_id': c.store_id,
        'name': c.name,
        'ip_address': c.ip_address,
        'status': c.status,
        'last_seen': c.last_seen.isoformat() if c.last_seen else None
    } for c in cameras]), 200

# AI Model management
@admin_bp.route('/models', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def manage_models():
    if request.method == 'POST':
        if 'model' not in request.files:
            return jsonify({'error': 'No model file provided'}), 400
        
        model_file = request.files['model']
        name = request.form.get('name')
        version = request.form.get('version')
        classes = request.form.get('classes')  # JSON string of class labels
        
        if not all([name, version, classes]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            json.loads(classes)  # Validate JSON
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid classes JSON'}), 400
        
        # Save model file
        filename = f"{name}_v{version}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.h5"
        file_path = os.path.join('model', filename)
        os.makedirs('model', exist_ok=True)
        model_file.save(file_path)
        
        # Create model record
        model = AIModel(
            name=name,
            version=version,
            file_path=file_path,
            classes=classes,
            uploaded_by=get_jwt_identity()
        )
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'id': model.id,
            'name': model.name,
            'version': model.version,
            'is_active': model.is_active
        }), 201
    
    # GET method
    models = AIModel.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'version': m.version,
        'is_active': m.is_active,
        'created_at': m.created_at.isoformat()
    } for m in models]), 200

@admin_bp.route('/models/<int:model_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_model(model_id):
    """Activate a specific model and deactivate others"""
    model = AIModel.query.get(model_id)
    if not model:
        return jsonify({'error': 'Model not found'}), 404
    
    # Deactivate all models
    AIModel.query.update({AIModel.is_active: False})
    
    # Activate selected model
    model.is_active = True
    db.session.commit()
    
    return jsonify({
        'message': 'Model activated successfully',
        'model': {
            'id': model.id,
            'name': model.name,
            'version': model.version
        }
    }), 200

# System status
@admin_bp.route('/status', methods=['GET'])
@jwt_required()
@admin_required
def system_status():
    """Get system status overview"""
    total_stores = Store.query.count()
    active_cameras = Camera.query.filter_by(status='online').count()
    total_cameras = Camera.query.count()
    active_model = AIModel.query.filter_by(is_active=True).first()
    
    return jsonify({
        'stores': {
            'total': total_stores
        },
        'cameras': {
            'total': total_cameras,
            'active': active_cameras
        },
        'model': {
            'name': active_model.name if active_model else None,
            'version': active_model.version if active_model else None
        }
    }), 200

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard():
    """Get admin dashboard statistics"""
    total_users = User.query.count()
    total_products = Product.query.count()
    active_carts = Cart.query.filter_by(status='active').count()
    completed_carts = Cart.query.filter_by(status='completed').count()
    
    return jsonify({
        'statistics': {
            'total_users': total_users,
            'total_products': total_products,
            'active_carts': active_carts,
            'completed_carts': completed_carts
        }
    }), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@admin_bp.route('/carts/active', methods=['GET'])
@jwt_required()
@admin_required
def get_active_carts():
    """Get all active carts"""
    carts = Cart.query.filter_by(status='active').all()
    return jsonify({
        'carts': [cart.to_dict() for cart in carts]
    }), 200 