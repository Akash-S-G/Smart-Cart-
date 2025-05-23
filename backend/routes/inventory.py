from flask import Blueprint, request, jsonify
from datetime import datetime

inventory = Blueprint('inventory', __name__)

# In-memory inventory (replace with database in production)
product_inventory = {}

@inventory.route('/add', methods=['POST'])
def add_product():
    """Add or update product in inventory"""
    data = request.json
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID required'}), 400
        
    product_info = {
        'name': data.get('name', f'Product {product_id}'),
        'price': data.get('price', 0.0),
        'quantity': data.get('quantity', 1),
        'category': data.get('category', 'uncategorized'),
        'last_updated': datetime.now().isoformat(),
        'detection_type': data.get('detection_type', 'manual'),
        'qr_code': data.get('qr_code'),
        'image_url': data.get('image_url')
    }
    
    if product_id in product_inventory:
        product_inventory[product_id]['quantity'] += product_info['quantity']
        product_inventory[product_id]['last_updated'] = product_info['last_updated']
    else:
        product_inventory[product_id] = product_info
    
    return jsonify({
        'message': 'Product added/updated successfully',
        'product': product_inventory[product_id]
    })

@inventory.route('/remove/<product_id>', methods=['POST'])
def remove_product(product_id):
    """Remove product from inventory"""
    if product_id not in product_inventory:
        return jsonify({'error': 'Product not found'}), 404
        
    quantity = request.json.get('quantity', 1)
    
    if product_inventory[product_id]['quantity'] <= quantity:
        del product_inventory[product_id]
        message = 'Product removed from inventory'
    else:
        product_inventory[product_id]['quantity'] -= quantity
        product_inventory[product_id]['last_updated'] = datetime.now().isoformat()
        message = 'Product quantity updated'
    
    return jsonify({'message': message})

@inventory.route('/list', methods=['GET'])
def list_products():
    """List all products in inventory"""
    category = request.args.get('category')
    if category:
        filtered_products = {
            k: v for k, v in product_inventory.items()
            if v['category'] == category
        }
        return jsonify(filtered_products)
    
    return jsonify(product_inventory)

@inventory.route('/update/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product information"""
    if product_id not in product_inventory:
        return jsonify({'error': 'Product not found'}), 404
        
    data = request.json
    product = product_inventory[product_id]
    
    for key, value in data.items():
        if key in product and key != 'product_id':
            product[key] = value
    
    product['last_updated'] = datetime.now().isoformat()
    
    return jsonify({
        'message': 'Product updated successfully',
        'product': product
    })

@inventory.route('/search', methods=['GET'])
def search_products():
    """Search products by name or category"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
        
    results = {
        k: v for k, v in product_inventory.items()
        if query in v['name'].lower() or query in v['category'].lower()
    }
    
    return jsonify(results)

@inventory.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product details"""
    if product_id not in product_inventory:
        return jsonify({'error': 'Product not found'}), 404
        
    return jsonify(product_inventory[product_id]) 