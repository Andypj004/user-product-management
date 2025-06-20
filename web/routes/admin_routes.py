from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, roles_required
import requests

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

USUARIOS_SERVICE_URL = "http://web:5000/users"
PRODUCTS_SERVICE_URL = 'http://web2:5001/products'
AUTH_SERVICE_URL = 'http://web4:5003/auth'


@admin_bp.route('/')
@login_required
@roles_required('admin')
def admin_dashboard():
    return render_template("admin.html")


@admin_bp.route('/qr/<email>')
@login_required
@roles_required('admin')
def mostrar_qr(email):
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/generate_qr/{email}")
        if resp.status_code == 200:
            qr_data = resp.json()
            return render_template("setup_2fa.html", qr_base64=qr_data["qr_code_base64"], email=email)
        else:
            flash("No se pudo generar el código QR.")
    except Exception as e:
        flash(f"Error: {str(e)}")
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/crear_usuario', methods=['POST'])
@login_required
@roles_required('admin')
def crear_usuario():
    username = request.form['user_username']
    email = request.form['user_email']
    password = request.form['user_password']
    rol = request.form['user_rol']

    data = {
        'username': username,
        'email': email,
        'password': password,
        'rol': rol
    }

    try:
        response = requests.post(USUARIOS_SERVICE_URL, json=data)
        if response.status_code == 201:
            flash("Usuario creado con éxito.")
            return redirect(url_for('admin.mostrar_qr', email=email))
        else:
            flash("Error al crear el usuario.")
    except Exception as e:
        flash(f"Error al conectar con el servicio: {str(e)}")

    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/actualizar_usuario', methods=['POST'])
@login_required
@roles_required('admin')
def actualizar_usuario():
    email = request.form['update_user_email']
    new_password = request.form['update_user_password']
    new_rol = request.form['update_user_rol']

    data = {}
    if new_password:
        data['password'] = new_password
    if new_rol:
        data['rol'] = new_rol

    try:
        response = requests.put(f"{USUARIOS_SERVICE_URL}/{email}", json=data)
        if response.status_code == 200:
            flash("Usuario actualizado con éxito.")
        else:
            flash("Error al actualizar el usuario.")
    except Exception as e:
        flash(f"Error al conectar con el servicio: {str(e)}")

    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/eliminar_usuario', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_usuario():
    email = request.form['delete_user_email']

    try:
        response = requests.delete(f"{USUARIOS_SERVICE_URL}/{email}")
        if response.status_code == 200:
            flash("Usuario eliminado con éxito.")
        else:
            flash("Error al eliminar el usuario.")
    except Exception as e:
        flash(f"Error al conectar con el servicio: {str(e)}")

    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/crear_producto', methods=['POST'])
@login_required
@roles_required('admin')
def crear_producto():
    name = request.form['product_name']
    description = request.form['product_description']
    price = request.form['product_price']

    data = {'name': name, 'price': price, 'description': description}

    try:
        response = requests.post(PRODUCTS_SERVICE_URL, json=data)
        if response.status_code == 201:
            flash("Producto creado con éxito.")
        else:
            flash("Error al crear el producto.")
    except Exception as e:
        flash(f"Error al conectar con el servicio: {str(e)}")

    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/actualizar_producto', methods=['POST'])
@login_required
@roles_required('admin')
def actualizar_producto():
    product_id = request.form['update_product_id']
    new_name = request.form['update_product_name']
    new_description = request.form['update_product_description']
    new_price = request.form['update_product_price']

    data = {}
    if new_name:
        data['name'] = new_name
    if new_price:
        data['price'] = new_price
    if new_description:
        data['description'] = new_description

    try:
        response = requests.put(f"{PRODUCTS_SERVICE_URL}/{product_id}", json=data)
        if response.status_code == 200:
            flash("Producto actualizado con éxito.")
        else:
            flash("Error al actualizar el producto.")
    except Exception as e:
        flash(f"Error al conectar con el servicio: {str(e)}")

    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/eliminar_producto', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_producto():
    product_id = request.form['delete_product_id']

    try:
        response = requests.delete(f"{PRODUCTS_SERVICE_URL}/{product_id}")
        if response.status_code == 200:
            flash("Producto eliminado con éxito.")
        else:
            flash("Error al eliminar el producto.")
    except Exception as e:
        flash(f"Error al conectar con el servicio: {str(e)}")

    return redirect(url_for('admin.admin_dashboard'))
