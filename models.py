from extensions import db
from datetime import datetime
from flask_login import UserMixin


#Classe Base
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.commit()


#Classe usuário
class Usuario(Base, UserMixin):
    __tablename__ = 'usuario'

    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(100), nullable=False)

    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.email}>'


#Classe Loja
class Loja(Base):
    __tablename__ = 'loja'

    nome = db.Column(db.String(120), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    contato = db.Column(db.String(20), nullable=False)

    produtos = db.relationship('Produto', backref='loja', lazy=True)

    def __repr__(self):
        return f'<Loja {self.nome} CNPJ:{self.cnpj}>'


#Classe Produto
class Produto(Base):
    __tablename__ = 'produto'

    loja_id = db.Column(db.Integer, db.ForeignKey('loja.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    estoque = db.relationship('Estoque', backref='produto', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'


##Classe Estoque
class Estoque(Base):
    __tablename__ = 'estoque'

    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, default=0, nullable=False)
    localizacao = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Estoque produto:{self.produto_id} QTD:{self.quantidade}>'


#Classde Pedido
class Pedido(Base):
    __tablename__ = 'pedido'

    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default='Criado', nullable=False)
    valor_total = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Pedido {self.id}>'
