from flask import Blueprint, request, jsonify

# Blueprint de produtos
produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')


# --- Criar Produto ---
@produtos_bp.route('/', methods=['POST'])
def criar_produtos():
    from app import db, Produto  # Import dentro da função para evitar ciclo

    data = request.get_json()
    if not data or 'nome' not in data or 'preco' not in data:
        return jsonify({'message': 'Dados incompletos. Nome e Preço são obrigatórios'}), 400

    novo_produto = Produto(
        nome=data['nome'],
        preco=data['preco'],
        descricao=data.get('descricao')
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


# --- Listar Produtos ---
@produtos_bp.route('/', methods=['GET'])
def listar_produtos():
    from app import Produto

    produtos = Produto.query.filter(Produto.deleted_at == None).all()
    lista = []
    for produto in produtos:
        lista.append({
            'id': produto.id,
            'nome': produto.nome,
            'preco': produto.preco,
            'descricao': produto.descricao,
            'created_at': produto.created_at.isoformat(),
            'updated_at': produto.updated_at.isoformat()
        })
    return jsonify(lista), 200


# --- Buscar Produto por ID ---
@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def buscar_produto(produto_id):
    from app import Produto

    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at == None
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    produto_data = {
        'id': produto.id,
        'nome': produto.nome,
        'preco': produto.preco,
        'descricao': produto.descricao,
        'created_at': produto.created_at.isoformat(),
        'updated_at': produto.updated_at.isoformat()
    }
    return jsonify(produto_data), 200


# --- Atualizar Produto ---
@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    from app import db, Produto

    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at == None
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado para atualização!'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Nenhuma informação foi dada para atualização!'}), 400

    try:
        if 'nome' in data:
            produto.nome = data['nome']
        if 'preco' in data:
            produto.preco = float(data['preco'])
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


# --- Deletar Produto (Soft Delete) ---
@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
def deletar_produtos(produto_id):
    from app import db, Produto

    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at == None
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado para exclusão'}), 404

    try:
        produto.soft_delete()
        db.session.commit()
        return jsonify({'message': f'Produto ID {produto.id} excluído.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar o produto: {e}'}), 500
