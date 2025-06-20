from flask import Flask, request, jsonify, send_file
import requests
import os
import pyotp
import qrcode
import io
import base64
import time
from datetime import datetime

app = Flask(__name__)

USERS_SERVICE_URL = "http://web:5000"

def get_user_secret(email):
    resp = requests.get(f"{USERS_SERVICE_URL}/users/{email}/secret")
    if resp.status_code == 200:
        return resp.json().get("secret_key")
    return None

@app.route('/auth/generate_otp/<string:email>', methods=['GET'])
def generate_otp(email):
    secret = get_user_secret(email)
    totp = pyotp.TOTP(secret)
    otp_uri = totp.provisioning_uri(name=email, issuer_name="UserProductApp")
    return jsonify({'otp_uri': otp_uri})

@app.route('/auth/generate_qr/<string:email>', methods=['GET'])
def generate_qr(email):
    secret = get_user_secret(email)
    if not secret:
        return jsonify({'error': 'No se pudo obtener la clave secreta'}), 404

    totp = pyotp.TOTP(secret)
    otp_uri = totp.provisioning_uri(name=email, issuer_name="UserProductApp")

    img = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Codificar imagen en base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return jsonify({'qr_code_base64': img_base64})

@app.route('/auth/debug/<string:email>', methods=['GET'])
def debug_totp(email):
    """Endpoint para debug - eliminar en producción"""
    secret = get_user_secret(email)
    if not secret:
        return jsonify({'error': 'No se encontró clave secreta'}), 404
    
    totp = pyotp.TOTP(secret)
    current_time = int(time.time())
    
    # Generar códigos para diferentes ventanas de tiempo
    debug_info = {
        'secret': secret,
        'current_timestamp': current_time,
        'current_datetime': datetime.fromtimestamp(current_time).isoformat(),
        'current_code': totp.now(),
        'codes_window': {}
    }
    
    # Verificar códigos en una ventana de ±3 minutos
    for offset in range(-3, 4):
        timestamp = current_time + (offset * 30)  # 30 segundos por ventana
        code = totp.at(timestamp)
        debug_info['codes_window'][f'offset_{offset}'] = {
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp).isoformat(),
            'code': code
        }
    
    return jsonify(debug_info)

@app.route('/auth/verify', methods=['POST'])
def verify_token():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')

    print(f"Verificando código para: {email}", flush=True)
    print(f"Código recibido: {token}", flush=True)

    secret = get_user_secret(email)
    print(f"Secreto usado: {secret}", flush=True)

    if not secret:
        return jsonify({'verified': False, 'error': 'No se encontró clave secreta'}), 404

    # Verificar que el token sea numérico y tenga 6 dígitos
    if not token or not token.isdigit() or len(token) != 6:
        print(f"Token inválido: {token}", flush=True)
        return jsonify({'verified': False, 'error': 'Token debe ser 6 dígitos'}), 400

    totp = pyotp.TOTP(secret)
    current_time = int(time.time())
    current_code = totp.now()
    
    print(f"Timestamp actual: {current_time}", flush=True)
    print(f"Fecha/hora actual: {datetime.fromtimestamp(current_time)}", flush=True)
    print(f"Código actual esperado: {current_code}", flush=True)

    # Intentar verificar con ventana más amplia para debug
    for window in [1, 2, 3]:
        if totp.verify(token, valid_window=window):
            print(f"Código verificado exitosamente con ventana: {window}", flush=True)
            return jsonify({'verified': True}), 200
        else:
            print(f"Falló verificación con ventana: {window}", flush=True)

    # Si llega aquí, mostrar códigos de debug
    print("=== DEBUG: Códigos en ventana de tiempo ===", flush=True)
    for offset in range(-2, 3):
        timestamp = current_time + (offset * 30)
        code = totp.at(timestamp)
        print(f"Offset {offset}: {code} (timestamp: {timestamp})", flush=True)
    
    return jsonify({'verified': False}), 401

@app.route('/auth/verify_enhanced', methods=['POST'])
def verify_token_enhanced():
    """Versión mejorada de verificación con mejor manejo de errores"""
    data = request.get_json()
    token = data.get('token', '').strip()
    email = data.get('email', '').strip()

    if not email or not token:
        return jsonify({
            'verified': False, 
            'error': 'Email y token son requeridos'
        }), 400

    # Validar formato del token
    if not token.isdigit() or len(token) != 6:
        return jsonify({
            'verified': False, 
            'error': 'El token debe contener exactamente 6 dígitos'
        }), 400

    secret = get_user_secret(email)
    if not secret:
        return jsonify({
            'verified': False, 
            'error': 'No se encontró clave secreta para el usuario'
        }), 404

    try:
        totp = pyotp.TOTP(secret)
        
        # Verificar con ventana de tolerancia
        # valid_window=2 permite ±60 segundos de diferencia
        if totp.verify(token, valid_window=2):
            return jsonify({'verified': True}), 200
        else:
            return jsonify({
                'verified': False, 
                'error': 'Código 2FA incorrecto o expirado'
            }), 401
            
    except Exception as e:
        print(f"Error en verificación TOTP: {str(e)}", flush=True)
        return jsonify({
            'verified': False, 
            'error': 'Error interno en verificación'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)