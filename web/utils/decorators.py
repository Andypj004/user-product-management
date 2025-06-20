from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            flash("Inicia sesión para continuar.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get('user')
            if not user or user.get('rol') not in roles:
                flash("Acceso denegado.")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator
