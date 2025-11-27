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
    """Cria um novo produto, associando-o a uma loja existente."""
    data = request.get_json()
    
    # 1. Validação de Dados OBRIGATÓRIOS
    # Agora requer 'loja_id'
    if not data or 'nome' not in data or 'preco' not in data or 'loja_id' not in data:
        return jsonify({'message': 'Dados incompletos. Nome, Preço e ID da Loja são obrigatórios.'}), 400

    loja_id = data.get('loja_id')
    
    # 2. Validação da Loja
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
    """Lista todos os produtos que não foram deletados (soft delete)."""
    
    # 💡 MELHORIA: Usar .is_(None) é mais legível e idiomático com SQLAlchemy
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

@produtos_bp.route('/loja/<int:loja_id>', methods=['GET'])
@login_required
def listar_produtos_por_loja(loja_id): 
    """Lista todos os produtos de uma loja específica."""

    if current_user.id != loja_id:
        return jsonify({'message': 'Acesso negado. Você só pode visualizar produtos da sua própria loja.'}), 403
    
    loja = Loja.query.get(loja_id)
    if not loja:
        return jsonify({'message': f'Loja com ID {loja_id} não encontrada.'}), 404
        
    # Filtra produtos APENAS da loja especificada e que não foram eliminados
    produtos = Produto.query.filter(
        Produto.loja_id == loja_id, 
        Produto.deleted_at.is_(None)
    ).all()
    
    produtos_list = [
        {
            'id': p.id,
            'nome': p.nome,
            'preco': p.preco,
            'descricao': p.descricao,
            'loja_id': p.loja_id,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat()
        }
        for p in produtos
    ]
    return jsonify(produtos_list), 200


# Função Buscar Produto
@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def buscar_produto(produto_id):
    """Busca um produto específico pelo ID, ignorando deletados."""
    
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
@login_required # Recomendado: Apenas usuários autenticados podem atualizar produtos
def atualizar_produto(produto_id):
    """Atualiza as informações de um produto existente."""
    
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
            # Garante que o preço seja um float válido
            try:
                produto.preco = float(data['preco'])
            except ValueError:
                return jsonify({'message': 'O preço deve ser um valor numérico válido.'}), 400
                
        if 'descricao' in data:
            produto.descricao = data['descricao']

        # Obs: Não permitimos alterar o loja_id, pois geralmente é uma chave imutável.

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
@login_required # Recomendado: Apenas usuários autenticados podem deletar produtos
def deletar_produtos(produto_id):
    """Marca um produto como deletado (soft delete)."""
    
    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at.is_(None)
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado para exclusão'}), 404

    try:
        # Usa o método soft_delete definido na classe Base do modelo
        produto.soft_delete() 
        # Não é necessário um db.session.commit() após soft_delete se o método 
        # já o faz, mas o Base modelo que definimos acima não faz o commit internamente.
        db.session.commit()
        
        return jsonify({'message': f'Produto ID {produto.id} excluído (Soft Delete).'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar o produto: {e}'}), 500