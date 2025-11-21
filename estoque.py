from flask import Blueprint, request, jsonify
from app import db, Estoque # Importamos 'db' e a classe 'Estoque'
from flask_login import login_required 
from datetime import datetime

# Criação do Blueprint. Todas as rotas começarão com /estoque.
estoque_bp = Blueprint('estoque', __name__, url_prefix='/estoque')

# Função auxiliar para serializar (converter para JSON)
def serialize_estoque(estoque):
    return {
        'id': estoque.id,
        'produto_id': estoque.produto_id,
        'quantidade': estoque.quantidade,
        'localizacao': estoque.localizacao,
        'created_at': estoque.created_at.isoformat(),
        'updated_at': estoque.updated_at.isoformat()
    }

#1º Rota: Criar ou inicializar Estoque.
@estoque_bp.route('/', methods=['POST'])
@login_required 
def criar_estoque():
    data = request.get_json()
    
    if not data or 'produto_id' not in data or 'quantidade' not in data:
        return jsonify({'message': 'Produto ID e Quantidade são obrigatórios.'}), 400

    produto_id = data['produto_id']
    quantidade = data['quantidade']
    localizacao = data.get('localizacao')

    # Verifica unicidade (1:1 com Produto)
    if Estoque.query.filter_by(produto_id=produto_id).first():
        return jsonify({'message': f'Estoque para o Produto ID {produto_id} já existe. Use PUT para atualizar.'}), 409

    novo_estoque = Estoque(
        produto_id=produto_id,
        quantidade=quantidade,
        localizacao=localizacao
    )

    try:
        db.session.add(novo_estoque)
        db.session.commit()
        
        return jsonify({
            'message': 'Estoque inicializado com sucesso!',
            'estoque': serialize_estoque(novo_estoque)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar estoque: {e}'}), 500

#2º Rota: Listar todo o estoque.
@estoque_bp.route('/', methods=['GET'])
@login_required
def listar_estoques():
    # Ignora itens deletados logicamente
    estoques = Estoque.query.filter_by(deleted_at=None).all() 
    lista_estoques = [serialize_estoque(e) for e in estoques]
        
    return jsonify(lista_estoques), 200


#3º Rota: Buscar no estoque.
@estoque_bp.route('/<int:produto_id>', methods=['GET'])
def buscar_estoque(produto_id):
    # Busca pelo produto_id (e verifica soft delete)
    estoque = Estoque.query.filter(
        Estoque.produto_id == produto_id,
        Estoque.deleted_at == None
    ).first()

    if not estoque:
        return jsonify({'message': f'Estoque para o Produto ID {produto_id} não encontrado.'}), 404

    return jsonify(serialize_estoque(estoque)), 200

#4º Rota: Atualizar estoque.
@estoque_bp.route('/<int:produto_id>', methods=['PUT'])
@login_required
def atualizar_estoque(produto_id):
    # Busca pelo produto_id (e verifica soft delete)
    estoque = Estoque.query.filter(
        Estoque.produto_id == produto_id,
        Estoque.deleted_at == None
    ).first()

    if not estoque:
        return jsonify({'message': f'Estoque para o Produto ID {produto_id} não encontrado.'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Nenhum dado fornecido para atualização.'}), 400
        
    try:
        if 'quantidade' in data:
            estoque.quantidade = data['quantidade']
        
        if 'localizacao' in data:
            estoque.localizacao = data['localizacao']
            
        db.session.commit()

        return jsonify({
            'message': f'Estoque do Produto ID {produto_id} atualizado com sucesso.',
            'estoque': serialize_estoque(estoque)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar estoque: {e}'}), 500

#5º Rota: Deletar estoque.
@estoque_bp.route('/<int:produto_id>', methods=['DELETE'])
@login_required
def deletar_estoque(produto_id):
    estoque = Estoque.query.filter(
        Estoque.produto_id == produto_id,
        Estoque.deleted_at == None
    ).first()

    if not estoque:
        return jsonify({'message': f'Estoque para o Produto ID {produto_id} não encontrado para exclusão.'}), 404
        
    try:
        # Usa o Soft Delete
        estoque.soft_delete() 
        
        return jsonify({'message': f'Estoque do Produto ID {produto_id} excluído logicamente.'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar estoque: {e}'}), 500