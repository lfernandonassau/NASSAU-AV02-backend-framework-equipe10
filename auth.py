from flask import Flask
from main import db, Usuario
from Crypto.Hash import SHA256 #Para segurança.
from flask_login import login_user, logout_user, login_required, current_user

auth.bp = Blueprint('auth', __name__, url_prefix= '/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = register.get_json()
    
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'message': 'Dados incompletos. Email e senha são obrigatórios!'}), 400
    
    if len(senha) < 8:
        return jsonify({'message': 'A senha deve ter no mínimo 8 caracteres.'}), 400
    
    if usuario.query.filter_by(email=email).first():
        return jsonify({'message:' 'Este email já esta cadastrado!'}), 409
    
    h = SHA256.new(data=senha.encode('utf-8'))
    senha_hash = h.hexdigeste()

    novo_usuario = Usuario(
        email = email
        senha_hash = senha_hash
    )

    try:
        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({
            'message': 'Registro foi um sucesso. :)'
            'user_id': novo_usuario.id
        }), 201
    
    except Exception as e:
        db.sessio.rollback()
        return jsonify({'message:' f'Erro ao cadastrar usuário!{e}'}), 500 
    
@auth_bp.route(/'login', methods=['POST'])#Rota Login.
def login()
    data = request.get_json()

    if not data or not data.get('email') or not data.get():
        return jsonify({'message:' 'Login e senha são obrigatórios.'}), 400
    
    email = data.get('email')
    senha = data.get('senha')

    #Buscando o usúario.
    usuario = Usuario.query.filter_by(email=email).firts()

    if not usuario:
        return jsonify({'message:' 'Dados não credenciados!'}), 401
    
    h = SHA256.new(data=senha.encode('utf-8'))
    senha_hash_fornecida = h.hexdigest()
    
    if usuario.senha_hash == senha_hash_fornecida:
        login_user(usuario)
        
        return jsonify({
            'message': 'Login executado com sucesso!'
            'user_id': usuario.id
            'email': usuario.email
        }), 200
    
    else:
        return jsonify({'message': 'Dados inválidos'}), 401

#Rota de Logout.    
@auth_bp.route('/logout', methods=['POST'])
@login_required #Para dar Logout é preciso estar logado.

def logout():
    logout_user()
    return jsonify({'message': 'Sessão encerrada!'}), 200





    
        
