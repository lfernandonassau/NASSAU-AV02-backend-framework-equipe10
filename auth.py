from flask import Flask
from main import db, Usuario
from Crypto.Hash import SHA256
from flask_login import login_user, logout_user, login_required, current_user

auth.bp = Blueprint('auth', __name__, url_prefix= '/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = register.get_json()
    