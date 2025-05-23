from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Store, Item, ItemLocation, db, Product, Category
from math import radians, sin, cos, sqrt, atan2

store_bp = Blueprint('store', __name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

@store_bp.route('/nearby', methods=['GET'])
def find_nearby_stores():
    """Find stores near a given location"""
    try:
        lat = float(request.args.get('latitude'))
        lon = float(request.args.get('longitude'))
        radius = float(request.args.get('radius', 10))  # Default 10km radius
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid coordinates or radius'}), 400
    
    stores = Store.query.filter_by(is_active=True).all()
    
    nearby_stores = []
    for store in stores:
        distance = calculate_distance(lat, lon, store.latitude, store.longitude)
        if distance <= radius:
            nearby_stores.append({
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'latitude': store.latitude,
                'longitude': store.longitude,
                'distance': round(distance, 2),
                'camera_count': len(store.cameras)
            })
    
    # Sort by distance
    nearby_stores.sort(key=lambda x: x['distance'])
    
    return jsonify(nearby_stores), 200

@store_bp.route('/search', methods=['GET'])
def search_stores():
    """Search stores by name or address"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    stores = Store.query.filter(
        (Store.name.ilike(f'%{query}%') | Store.address.ilike(f'%{query}%')) &
        Store.is_active.is_(True)
    ).all()
    
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'address': s.address,
        'latitude': s.latitude,
        'longitude': s.longitude,
        'camera_count': len(s.cameras)
    } for s in stores]), 200

@store_bp.route('/<int:store_id>', methods=['GET'])
def get_store_details(store_id):
    """Get detailed information about a specific store"""
    store = Store.query.get(store_id)
    if not store:
        return jsonify({'error': 'Store not found'}), 404
    
    return jsonify({
        'id': store.id,
        'name': store.name,
        'address': store.address,
        'latitude': store.latitude,
        'longitude': store.longitude,
        'is_active': store.is_active,
        'cameras': [{
            'id': c.id,
            'name': c.name,
            'status': c.status,
            'last_seen': c.last_seen.isoformat() if c.last_seen else None
        } for c in store.cameras]
    }), 200

@store_bp.route('/items/search', methods=['GET'])
@jwt_required()
def search_items():
    query = request.args.get('q', '').strip()
    store_id = request.args.get('store_id')
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Base query for items
    items_query = Item.query
    
    # Apply search filter
    search_filter = Item.name.ilike(f'%{query}%')
    items_query = items_query.filter(search_filter)
    
    # If store_id is provided, only show items available in that store
    if store_id:
        items_query = items_query.join(ItemLocation).filter(ItemLocation.store_id == store_id)
    
    items = items_query.all()
    
    results = []
    for item in items:
        locations = []
        for loc in item.locations:
            store = Store.query.get(loc.store_id)
            locations.append({
                'store_id': loc.store_id,
                'store_name': store.name,
                'aisle_number': loc.aisle_number,
                'shelf_number': loc.shelf_number,
                'section': loc.section,
                'in_stock': loc.in_stock,
                'position': {
                    'x': loc.position_x,
                    'y': loc.position_y
                }
            })
        
        results.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'image_url': item.image_url,
            'locations': locations
        })
    
    return jsonify(results)

@store_bp.route('/items/<int:item_id>/location', methods=['GET'])
@jwt_required()
def get_item_location(item_id):
    store_id = request.args.get('store_id')
    if not store_id:
        return jsonify({'error': 'store_id is required'}), 400
    
    location = ItemLocation.query.filter_by(
        item_id=item_id,
        store_id=store_id
    ).first()
    
    if not location:
        return jsonify({'error': 'Item not found in this store'}), 404
    
    store = Store.query.get(store_id)
    
    return jsonify({
        'item': {
            'id': location.item.id,
            'name': location.item.name,
            'description': location.item.description,
            'image_url': location.item.image_url
        },
        'location': {
            'store_name': store.name,
            'aisle_number': location.aisle_number,
            'shelf_number': location.shelf_number,
            'section': location.section,
            'in_stock': location.in_stock,
            'position': {
                'x': location.position_x,
                'y': location.position_y
            }
        },
        'store_layout': {
            'image_url': store.layout_image,
            'layout_data': store.layout_data
        }
    })

@store_bp.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price),
            'category': p.category,
            'image_url': p.image_url
        } for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@store_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name
        } for c in categories]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 