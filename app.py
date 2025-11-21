from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin

#CONFIGURAÇÃO INICIAL DO FLASK E BANCO DE DADOS
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chavesecreta'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

#MODELOS (ENTIDADES) 

class Base(db.Model):
    __abstract__ = True 

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.commit()

class Usuario(Base, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(100), nullable=False)

    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.email}>'

class Loja(Base):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    contato = db.Column(db.String(20), nullable=False)
    
    # Relacionamento 1:N: Uma loja tem vários produtos.
    produtos = db.relationship('Produto', backref='loja', lazy=True)

    def __repr__(self):
        return f'<Loja {self.nome} CNPJ:{self.cnpj}>'
    
class Produto(Base):
    id = db.Column(db.Integer, primary_key=True)
    
    # ADICIONADO/CORRIGIDO: Chave Estrangeira para Loja (1:N)
    loja_id = db.Column(db.Integer, db.ForeignKey('loja.id'), nullable=False) 
    
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    
    # Relacionamento 1:1 com Estoque
    estoque = db.relationship('Estoque', backref='produto', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<Produto {self.nome}>'
    
class Estoque(Base):
    id = db.Column(db.Integer, primary_key=True)
    # CORRIGIDO: FK aponta para 'produto.id' (e não 'pedido.id')
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), unique=True, nullable=False)
    
    quantidade = db.Column(db.Integer, default=0, nullable=False)
    localizacao = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Estoque produto:{self.produto_id} QTD:{self.quantidade}>'
    
class Pedido(Base):
    id = db.Column(db.Integer, primary_key=True)
    # Relação N:1 com Usuário (Cliente)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False) 
    
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default='Criado', nullable=False)
    valor_total = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<Pedido {self.id}>'
    
#FUNÇÃO DE LOGIN 
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

#FUNÇÃO PARA CRIAR A LOJA FIXA
def criar_loja_unica():
    CNPJ_FIXO = '12345678000190'
    NOME_LOJA = 'E-Commerce Central'
    
    loja = Loja.query.filter_by(cnpj=CNPJ_FIXO).first()
    
    if not loja:
        print(f"Criando Loja Única Fixa: '{NOME_LOJA}'")
        nova_loja = Loja(
            cnpj=CNPJ_FIXO,
            nome=NOME_LOJA,
            contato='(99) 99999-9999' 
        )
        db.session.add(nova_loja)
        db.session.commit()
    else:
        print(f"Loja Única '{NOME_LOJA}' já existe.")


try:
    from produtos_controller import produtos_bp
    from auth import auth_bp
    from pedidos import pedidos_bp
    from estoque import estoque_bp


except ImportError as e:
    print(f"ATENÇÃO: Não foi possível importar um Blueprint. Verifique se todos os arquivos .py existem e se o erro foi resolvido. Erro: {e}")
    # Se der erro, vamos continuar para tentar criar as tabelas.

# REGISTRO DOS BLUEPRINTS (ROTAS) 
if 'produtos_bp' in locals():
    app.register_blueprint(produtos_bp)
if 'auth_bp' in locals():
    app.register_blueprint(auth_bp)
if 'pedidos_bp' in locals():
    app.register_blueprint(pedidos_bp)
if 'estoque_bp' in locals():
    app.register_blueprint(estoque_bp)

#INICIALIZAÇÃO DO SERVIDOR.
if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas db. caso não existam e cria a loja inicial.
        db.create_all() 
        criar_loja_unica() 
        
    app.run(debug=True)