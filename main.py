from flask import Flask, request, jsonify
from sqlalchemy import Column, Float, Integer, Text, String, DateTime, ForeignKey
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

    created_at = Column(DateTime, default = datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.commit()

class Usuario(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(100), nullable = False)

    pedidos = db.relationship('Pedido', backref='usuario', lazy = True)

    def __repr__(self):
        return f'<Usuario {self.email}>'

class Produto(Base, UserMixin):
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)  
    preco = Column(Float, nullable=False)
    descricao = Column(Text, nullable=True)   

    def __repr__(self):
        return f'<Produto {self.nome}>'

class Pedido(Base):
    id = Column(Integer, primary_key=True)
    data_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), default='Criado', nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f'<Pedido {self.id}>'
    
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


app.register_blueprint(produtos_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() #Cria as tabelas db. caso não existam.

    app.run(debug=True)    
