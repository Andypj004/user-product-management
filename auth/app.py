from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'clave_secreta'

USUARIOS_SERVICE_URL = "http://web:5000/users"
PRODUCTS_SERVICE_URL = 'http://web2:5001/products'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            resp = requests.get(f"{USUARIOS_SERVICE_URL}/{email}")
            if resp.status_code == 200:
                user = resp.json()
                if user['password'] == password:
                    if user['rol'] == 'cliente':
                        return redirect(url_for('listar_productos'))
                    elif user['rol'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    else:
                        flash("Rol no reconocido.")
                else:
                    flash("Contraseña incorrecta")
            else:
                flash("Usuario no encontrado")
        except Exception as e:
            flash(f"Error al conectar con el servicio: {str(e)}")

        return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/admin')
def admin_dashboard():
    return render_template("admin.html")

@app.route('/admin/crear_usuario', methods=['POST'])
def crear_usuario():
    email = request.form['user_email']
    password = request.form['user_password']
    rol = request.form['user_rol']
    
    data = {'email': email, 'password': password, 'rol': rol}
    try:
        response = requests.post(f"{USUARIOS_SERVICE_URL}", json=data)
        if response.status_code == 201:
            flash("Usuario creado con éxito.")
        else:
            flash("Error al crear el usuario.")
    except Exception as e:
        flash(f"Error al conectar con el servicio de usuarios: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/actualizar_usuario', methods=['POST'])
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
        flash(f"Error al conectar con el servicio de usuarios: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/crear_producto', methods=['POST'])
def crear_producto():
    name = request.form['product_name']
    price = request.form['product_price']
    
    data = {'name': name, 'price': price}
    try:
        response = requests.post(f"{PRODUCTS_SERVICE_URL}", json=data)
        if response.status_code == 201:
            flash("Producto creado con éxito.")
        else:
            flash("Error al crear el producto.")
    except Exception as e:
        flash(f"Error al conectar con el servicio de productos: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/actualizar_producto', methods=['POST'])
def actualizar_producto():
    product_id = request.form['update_product_id']
    new_name = request.form['update_product_name']
    new_price = request.form['update_product_price']
    
    data = {}
    if new_name:
        data['name'] = new_name
    if new_price:
        data['price'] = new_price

    try:
        response = requests.put(f"{PRODUCTS_SERVICE_URL}/{product_id}", json=data)
        if response.status_code == 200:
            flash("Producto actualizado con éxito.")
        else:
            flash("Error al actualizar el producto.")
    except Exception as e:
        flash(f"Error al conectar con el servicio de productos: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    email = request.form['delete_user_email']
    
    try:
        response = requests.delete(f"{USUARIOS_SERVICE_URL}/{email}")
        if response.status_code == 200:
            flash("Usuario eliminado con éxito.")
        else:
            flash("Error al eliminar el usuario.")
    except Exception as e:
        flash(f"Error al conectar con el servicio de usuarios: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/eliminar_producto', methods=['POST'])
def eliminar_producto():
    product_id = request.form['delete_product_id']
    
    try:
        response = requests.delete(f"{PRODUCTS_SERVICE_URL}/{product_id}")
        if response.status_code == 200:
            flash("Producto eliminado con éxito.")
        else:
            flash("Error al eliminar el producto.")
    except Exception as e:
        flash(f"Error al conectar con el servicio de productos: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/productos')
def listar_productos():
    try:
        response = requests.get(PRODUCTS_SERVICE_URL)
        if response.status_code == 200:
            productos = response.json()
            return render_template('productos.html', productos=productos)
        else:
            flash("Error al obtener productos del servicio.")
            return render_template('productos.html', productos=[])
    except Exception as e:
        flash(f"Error al conectar con el servicio de productos: {str(e)}")
        return render_template('productos.html', productos=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
