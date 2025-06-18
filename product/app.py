from flask import Flask, request, jsonify
from models import db, Product
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/products', methods=['POST'])
def create_user():
    data = request.get_json()
    new_product = Product(name=data['name'], description=data['description'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201

@app.route('/products', methods=['GET'])
def get_users():
    products= Product.query.all()
    return jsonify([{'id': product.id, 'name': product.name, 'description': product.description, 'price': product.price} for product in products])

@app.route('/products/<int:id>', methods=['GET'])
def get_user(id):
    product = Product.query.get_or_404(id)
    return jsonify({'id': product.id, 'name': product.name, 'description': product.description, 'price': product.description})

@app.route('/products/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    product = Product.query.get_or_404(id)
    product.name = data['name']
    product.description = data['description']
    product.price = data['price']
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_user(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
