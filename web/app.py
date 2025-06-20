from flask import Flask
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.client_routes import client_bp

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(client_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
