from flask import Blueprint, render_template, flash
from utils.decorators import login_required, roles_required
import requests

client_bp = Blueprint('client', __name__)
PRODUCTS_SERVICE_URL = 'http://web2:5001/products'

@client_bp.route('/productos')
@login_required
@roles_required('cliente')
def listar_productos():
    try:
        resp = requests.get(PRODUCTS_SERVICE_URL)
        productos = resp.json() if resp.status_code == 200 else []
        return render_template('productos.html', productos=productos)
    except:
        flash("Error al obtener productos")
        return render_template('productos.html', productos=[])
