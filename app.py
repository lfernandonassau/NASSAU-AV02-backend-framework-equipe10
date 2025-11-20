from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from produtos import produtos_bp
from auth import auth_bp
from flask_login import LoginManager, UserMixin

#Configurando o Flask.
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chavesecreta'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

class Base(db.Model):
    __abstract__ = True 

    created_at = db.Column(db.DateTime, default = datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default = datetime.utcnow, onupdate = datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.commit()

class Usuario(Base, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(100), nullable = False)

    pedidos = db.relationship('Pedido', backref='usuario', lazy = True)

    def __repr__(self):
        return f'<Usuario {self.email}>'

class Produto(Base, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)  
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)   

    def __repr__(self):
        return f'<Produto {self.nome}>'

class Pedido(Base):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False) 
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default='Criado', nullable=False)
    valor_total = db.Column(db.Float, default=0.0)
   
    def __repr__(self):
        return f'<Pedido {self.id}>'

class Loja(Base):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullbale=False)
    contato = db.Column(db.String(20), nullable=False)   
    #Relacionamento 1:N, onde uma loja tem vários produtos.
    produtos = db.relationship('Produto', backref='loja', lazy=True)

    def __repr__(self):
        return f'<Loja {self.nome} CNPJ:{self.cnpj}>'
    
class Estoque(Base):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, default=0, nullable=False)
    localizacao = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Estoque produto:{self.produto_id} QTD:{self.quantidade}>'
        

    
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


app.register_blueprint(produtos_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() #Cria as tabelas db. caso não existam.

    app.run(debug=True)    
