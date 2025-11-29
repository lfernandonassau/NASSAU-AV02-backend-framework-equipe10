# blueprints/produtos_controller.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user 


# IMPORTAÇÕES CORRETAS 
from extensions import db
from models import Produto, Loja # Importando Loja para validação

# Blueprint de produtos
produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')


# Função Criar Produto
@produtos_bp.route('/', methods=['POST'])
@login_required # Recomendado: Apenas usuários autenticados podem criar produtos
def criar_produtos():
    
    data = request.get_json()
    
    
    if not data or 'nome' not in data or 'preco' not in data or 'loja_id' not in data:
        return jsonify({'message': 'Dados incompletos. Nome, Preço e ID da Loja são obrigatórios.'}), 400

    loja_id = data.get('loja_id')
    
    
    loja = Loja.query.filter_by(id=loja_id).first()
    if not loja:
        return jsonify({'message': f'Loja com ID {loja_id} não encontrada.'}), 404
    
    # Validação de preço
    try:
        preco_float = float(data['preco'])
    except ValueError:
        return jsonify({'message': 'O preço deve ser um valor numérico válido.'}), 400
        
    # 3. Criação do Produto (Com a correção do loja_id)
    novo_produto = Produto(
        nome=data['nome'],
        preco=preco_float,
        descricao=data.get('descricao'),
        loja_id=loja_id # 💡 CORREÇÃO CRÍTICA AQUI!
    )

    try:
        db.session.add(novo_produto)
        db.session.commit()
        return jsonify({
            'message': 'Produto criado com sucesso!',
            'id': novo_produto.id,
            'nome': novo_produto.nome
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar produto: {e}'}), 500


# Função Listar Produtos
@produtos_bp.route('/', methods=['GET'])
def listar_todos_produtos():
    
    produtos = Produto.query.filter(Produto.deleted_at.is_(None)).all()
    
    lista = []
    for produto in produtos:
        lista.append({
            'id': produto.id,
            'nome': produto.nome,
            'preco': produto.preco,
            'descricao': produto.descricao,
            'loja_id': produto.loja_id, # Adicionando loja_id para contexto
            'created_at': produto.created_at.isoformat(),
            'updated_at': produto.updated_at.isoformat()
        })
    return jsonify(lista), 200


# Função Buscar Produto
@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def buscar_produto(produto_id):
    
    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at.is_(None) # 💡 MELHORIA: Usar .is_(None)
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    produto_data = {
        'id': produto.id,
        'nome': produto.nome,
        'preco': produto.preco,
        'descricao': produto.descricao,
        'loja_id': produto.loja_id, # Adicionando loja_id para contexto
        'created_at': produto.created_at.isoformat(),
        'updated_at': produto.updated_at.isoformat()
    }
    return jsonify(produto_data), 200


# Função Atualizar Produto
@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@login_required 
def atualizar_produto(produto_id):
    
    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at.is_(None)
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado para atualização!'}), 400

    if current_user.id != produto.loja.id:
        return jsonify({'message:' 'Acesso Negado! Apenas é possível atualzar produtos da sua loja!'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Nenhuma informação foi dada para atualização!'}), 400

    try:
        if 'nome' in data:
            produto.nome = data['nome']
        
        if 'preco' in data:
            try:
                produto.preco = float(data['preco'])
            except ValueError:
                return jsonify({'message': 'O preço deve ser um valor numérico válido.'}), 400
                
        if 'descricao' in data:
            produto.descricao = data['descricao']


        db.session.commit()

        return jsonify({
            'message': f'Produto ID {produto_id} foi atualizado com sucesso!',
            'updated_at': produto.updated_at.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro interno ao atualizar produto: {e}'}), 500


# Função Deletar Produto (Soft Delete) 
@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
@login_required 
def deletar_produtos(produto_id):
    
    
    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at.is_(None)
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado para exclusão'}), 404

    try:
        produto.soft_delete() 
        
        db.session.commit()
        
        return jsonify({'message': f'Produto ID {produto.id} excluído (Soft Delete).'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar o produto: {e}'}), 500