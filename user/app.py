from flask import Flask, request, jsonify
from models import db, User
from config import Config
import pyotp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    secret_key = pyotp.random_base32() 
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        rol=data['rol'],
        secret_key=secret_key
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'message': 'User created successfully',
        'secret_key': secret_key  
    }), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username, 'email': user.email, 'password': user.password, 'rol': user.rol} for user in users])

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email, 'password': user.password, 'rol': user.rol})

@app.route('/users/<string:email>', methods=['GET'])
def get_user_email(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'rol': user.rol
        })
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
@app.route('/users/<string:email>/secret', methods=['GET'])
def get_secret_key(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'secret_key': user.secret_key}), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404

    
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)
    user.username = data['username']
    user.email = data['email']
    user.password = data['password']
    user.rol = data['rol']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@app.route('/users/<string:email>', methods=['DELETE'])
def delete_user_email(email):
    user = User.query.filter_by(email=email).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
