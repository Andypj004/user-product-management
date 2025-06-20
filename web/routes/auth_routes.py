from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import re

auth_bp = Blueprint('auth', __name__)

USUARIOS_SERVICE_URL = "http://web:5000/users"
AUTH_SERVICE_URL = "http://web4:5003/auth"

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        print(f"[LOGIN DEBUG] Intentando login para: {email}", flush=True)
        print(f"[LOGIN DEBUG] Password length: {len(password)}", flush=True)

        if not email or not password:
            flash("Email y contraseña son requeridos")
            print("[LOGIN DEBUG] Email o password faltantes", flush=True)
            return redirect(url_for('auth.login'))

        try:
            print(f"[LOGIN DEBUG] Consultando usuario en: {USUARIOS_SERVICE_URL}/{email}", flush=True)
            resp = requests.get(f"{USUARIOS_SERVICE_URL}/{email}", timeout=10)
            print(f"[LOGIN DEBUG] Respuesta del servicio de usuarios: {resp.status_code}", flush=True)
            
            if resp.status_code == 200:
                user = resp.json()
                print(f"[LOGIN DEBUG] Usuario encontrado: {user.get('email', 'N/A')}", flush=True)
                print(f"[LOGIN DEBUG] Rol del usuario: {user.get('rol', 'N/A')}", flush=True)
                
                # Verificar contraseña
                if user.get('password') == password:
                    print("[LOGIN DEBUG] Contraseña correcta, guardando en sesión", flush=True)
                    session['pending_user'] = user
                    print(f"[LOGIN DEBUG] Sesión guardada: {session.get('pending_user', {}).get('email', 'ERROR')}", flush=True)
                    return redirect(url_for('auth.verify_2fa'))
                else:
                    print("[LOGIN DEBUG] Contraseña incorrecta", flush=True)
                    flash("Contraseña incorrecta")
            elif resp.status_code == 404:
                print(f"[LOGIN DEBUG] Usuario no encontrado: {email}", flush=True)
                flash("Usuario no encontrado")
            else:
                print(f"[LOGIN DEBUG] Error del servicio: {resp.status_code} - {resp.text}", flush=True)
                flash(f"Error del servicio: {resp.status_code}")
                
        except requests.exceptions.Timeout:
            print("[LOGIN DEBUG] Timeout al conectar con servicio de usuarios", flush=True)
            flash("Timeout al conectar con el servidor")
        except requests.exceptions.ConnectionError:
            print("[LOGIN DEBUG] Error de conexión con servicio de usuarios", flush=True)
            flash("Error de conexión con el servidor")
        except Exception as e:
            print(f"[LOGIN DEBUG] Excepción: {str(e)}", flush=True)
            flash(f"Error interno: {str(e)}")

        return redirect(url_for('auth.login'))

    # GET request
    print("[LOGIN DEBUG] Mostrando formulario de login", flush=True)
    return render_template("login.html")

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    print("[2FA DEBUG] Accediendo a verify_2fa", flush=True)
    
    if 'pending_user' not in session:
        print("[2FA DEBUG] No hay pending_user en sesión, redirigiendo a login", flush=True)
        flash("Sesión expirada, inicia sesión nuevamente")
        return redirect(url_for('auth.login'))

    pending_user = session.get('pending_user')
    print(f"[2FA DEBUG] Usuario pendiente: {pending_user.get('email') if pending_user else 'None'}", flush=True)

    if request.method == 'POST':
        # Limpiar el token de espacios y caracteres no numéricos
        token = request.form.get('token', '').strip()
        token = re.sub(r'[^0-9]', '', token)  # Solo números
        
        print(f"[2FA DEBUG] Token recibido: {token}", flush=True)
        
        if not token or len(token) != 6:
            flash("El código debe contener exactamente 6 dígitos")
            print(f"[2FA DEBUG] Token inválido: longitud {len(token)}", flush=True)
            return render_template("verify_2fa.html")
        
        email = pending_user['email']
        
        try:
            print(f"[2FA DEBUG] Verificando token con servicio: {AUTH_SERVICE_URL}/verify_enhanced", flush=True)
            
            # Usar el endpoint mejorado
            resp = requests.post(
                f"{AUTH_SERVICE_URL}/verify_enhanced", 
                json={'token': token, 'email': email},
                timeout=10
            )
            
            print(f"[2FA DEBUG] Respuesta 2FA: {resp.status_code}", flush=True)
            print(f"[2FA DEBUG] Contenido respuesta: {resp.text}", flush=True)
            
            if resp.status_code == 200 and resp.json().get('verified'):
                print("[2FA DEBUG] Token verificado exitosamente", flush=True)
                user = session.pop('pending_user')
                session['user'] = user
                session.permanent = True  # Hacer la sesión persistente
                
                print(f"[2FA DEBUG] Usuario autenticado: {user.get('email')}", flush=True)
                print(f"[2FA DEBUG] Rol del usuario: {user.get('rol')}", flush=True)
                
                flash("Inicio de sesión exitoso", "success")
                
                if user.get('rol') == 'admin':
                    print("[2FA DEBUG] Redirigiendo a admin dashboard", flush=True)
                    return redirect(url_for('admin.admin_dashboard'))
                elif user.get('rol') == 'cliente':
                    print("[2FA DEBUG] Redirigiendo a listar productos", flush=True)
                    return redirect(url_for('client.listar_productos'))
                else:
                    print(f"[2FA DEBUG] Rol desconocido: {user.get('rol')}", flush=True)
                    flash("Rol de usuario no reconocido")
                    return redirect(url_for('auth.login'))
            else:
                error_msg = resp.json().get('error', 'Código 2FA incorrecto') if resp.status_code != 200 else 'Código 2FA incorrecto'
                print(f"[2FA DEBUG] Verificación fallida: {error_msg}", flush=True)
                flash(f"Error: {error_msg}")
                
        except requests.exceptions.Timeout:
            print("[2FA DEBUG] Timeout en verificación 2FA", flush=True)
            flash("Timeout al verificar el código. Intenta nuevamente.")
        except Exception as e:
            print(f"[2FA DEBUG] Excepción en 2FA: {str(e)}", flush=True)
            flash(f"Error al verificar: {str(e)}")

    print("[2FA DEBUG] Mostrando formulario 2FA", flush=True)
    return render_template("verify_2fa.html")

@auth_bp.route('/logout')
def logout():
    print("[LOGOUT DEBUG] Usuario cerrando sesión", flush=True)
    session.clear()
    flash("Sesión cerrada exitosamente")
    return redirect(url_for('auth.login'))

@auth_bp.route('/regenerate-qr')
def regenerate_qr():
    """Regenerar código QR para reconfigurar 2FA"""
    if 'pending_user' not in session:
        return redirect(url_for('auth.login'))
    
    email = session['pending_user']['email']
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/generate_qr/{email}")
        if resp.status_code == 200:
            qr_data = resp.json()
            return render_template("setup_2fa.html", qr_code=qr_data['qr_code_base64'])
        else:
            flash("Error al generar código QR")
    except Exception as e:
        flash(f"Error: {str(e)}")
    
    return redirect(url_for('auth.verify_2fa'))