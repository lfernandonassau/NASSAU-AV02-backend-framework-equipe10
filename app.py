from flask import Flask, request, jsonify
from datetime import datetime
from extensions import db, login_manager


# CONFIGURAÇÃO INICIAL DO FLASK
app = Flask(__name__)


from models import Usuario, Loja, Produto, Estoque, Pedido

# Configurações do App
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chavesecreta'

# Inicialização de Extensões (em duas etapas para maior segurança contra RuntimeErrors)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Vincula as extensões ao app


# Rota de Teste Base
@app.route('/')
def home():
    return jsonify({"status": "API está no ar! Use os endpoints /auth, /produtos, etc."}), 200


@login_manager.user_loader
def load_user(user_id):
    """Função de callback do Flask-Login que carrega um usuário.
    É necessário o app_context para que a query funcione corretamente
    quando o debug mode está ligado."""
    with app.app_context():
        return Usuario.query.get(int(user_id))


def criar_loja_unica():
    CNPJ_FIXO = '12345678000190'
    NOME_LOJA = 'Matriz Atacado'
    CONTATO_PADRAO = '(82) 4002-8922'

    loja = Loja.query.filter_by(cnpj=CNPJ_FIXO).first()

    if not loja:
        print(f"Criando Loja Única Fixa: '{NOME_LOJA}'")
        nova_loja = Loja(
            cnpj=CNPJ_FIXO,
            nome=NOME_LOJA,
            contato=CONTATO_PADRAO
        )
        db.session.add(nova_loja)
        db.session.commit()
    else:
        print(f"Loja Única '{NOME_LOJA}' já existe.")


# ------------------------------------
# TESTE DO BANCO
# ------------------------------------
@app.route('/teste-db')
def teste_db():
    try:
        # A rota já está em um contexto de requisição, então a query funciona.
        total = Usuario.query.count() 
        return jsonify({"status": "ok", "usuarios_cadastrados": total}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


# ------------------------------------
# IMPORTAÇÃO DOS BLUEPRINTS
# ------------------------------------
try:
   from blueprints.auth_control import auth_bp
   from blueprints.produtos_controller import produtos_bp
   from blueprints.pedidos import pedidos_bp
   from blueprints.estoque import estoque_bp



except ImportError as e:
    print(f"ATENÇÃO: blueprint faltando ou com erro → {e}")


# ------------------------------------
# REGISTRO DOS BLUEPRINTS
# ------------------------------------
if 'auth_bp' in locals():      app.register_blueprint(auth_bp)
if 'produtos_bp' in locals():  app.register_blueprint(produtos_bp)
if 'pedidos_bp' in locals():   app.register_blueprint(pedidos_bp)
if 'estoque_bp' in locals():   app.register_blueprint(estoque_bp)


# ------------------------------------
# EXECUÇÃO DO SERVIDOR (Garante que db.create_all() está no contexto)
# ------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        criar_loja_unica()
    
    # Executa o app fora do app_context, mas dentro do __main__
    # O contexto é criado automaticamente nas requisições, mas não para o reloader.
    app.run(debug=True)