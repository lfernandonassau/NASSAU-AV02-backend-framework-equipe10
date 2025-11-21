from flask import Blueprint, request, jsonify
from app import db, Loja # Importar 'db' e a classe 'Loja'
from datetime import datetime

#Blueprint
loja_bp = Blueprint('loja', __name__, url_prefix='/lojas')

def serialize_loja(loja):
    return{
        'id': loja.id,
        'cnpj': loja.cnpj,
        'nome': loja.nome,
        'contato': loja.contato,
        'created_at': loja.created_at.isoformat(),
        'updated_at': loja.updated_at.isoformat()

    }

@loja_bp.route('/', methods=['POST'])
def criar_loja():
    data = request.get_json()
    #CPNJ e Nome são informações obrigatórias
    if not data or 'cnpj' not in data or 'nome' not in data:
        return jsonify({'message': 'CNPJ e Nome são informações obrigatórias!'})
    
    cnpj = data['cnpj']
    nome = nome['nome']
    contato = contato['contato']

    #Verifcação, se o CNPJ é único.
    if Loja.query.filter_by(cnpj=cnpj).firts():
        return jsonify({'message': f'Este CNPJ já esta cadastrado!{cnpj}'})
    
    nova_loja = Loja(
        cnpj=cnpj,
        nome=nome,
        contato=contato
    )

    try:
        db.session.add(nova_loja)
        db.session.commit()
        
        return jsonify({
            'message': 'Loja criada com sucesso!',
            'loja': serialize_loja(nova_loja)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar loja: {e}'}), 500
    