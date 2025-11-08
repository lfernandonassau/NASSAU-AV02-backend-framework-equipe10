from flask import Blueprint, request, jsonify
from produtos import db, Produto
from datetime import datetime

#Agora, vamos criar o módulo de rotas (Blueprint).
produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')


@produtos_bp.route('/', methods=['POST'])

def criar_produtos():
    data = request.get_json()

#Validar dados:
    if not data or 'nome' not in data or 'preco' not in data:
        return jsonify({'message': 'Dados incompletos. Nome e Preço são obrigatórios'}), 400
    
    nome = data['nome']
    preco = data['preco']
    descricao = data.get('descricao')

    #Criação de novo produto.
    novo_produto = Produto(
        nome=nome,
        preco=preco,
        descricao=descricao,
    )

    try: #Salvando no Banco de Dados.
        db.session.add(novo_produto)
        db.session.commit()

        return jsonify({
            'message': 'Produto criado com sucesso!',
            'id': novo_produto.id,
            'nome': novo_produto.nome
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar produto:{e}'}), 500

#Listagem de produtos.    
@produtos_bp.route('/', methods=['GET'])
def listar_produtos():
    produtos = Produto.query.filter(Produto.deleted_at == None).all()

    lista_produtos = []
    for produto in produtos:
        lista_produtos.append({
            'id': produto.id,
            'nome': produto.nome,
            'preco': produto.preco,
            'descricao': produto.descricao,
            'created_at': produto.created_at.isoformat(),
            'updated_at': produto.updated_at.isoformat(),


        })

 
    return jsonify(lista_produtos), 200

#Busca de Produtos por ID
@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def buscar_produto(produto_id):
    produto = Produto.query.filter(
        Produto.id == produto.id,
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

#Atualizar produtos.
@produtos_bp.route('/<int:produto.id', methods=['PUT'])
def autualizar_produto(produto_id):
    produto = Produto.query.filter(
        Produto.id == produto_id,
        Produto.deleted_at == None
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado para atualização!'}), 400
    
    data = request.get_json

    if not data:
        return jsonify({'message': 'Nenhuma informação foi dada para atualização!'})
    
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
        return jsonify({'message': f'Erro interno ao atualizar produto{e}'}), 500        



#Rota para Deleter um produto.
@produtos_bp.route('/<int:produto_id', methods=['DELETE'])
def deletar_produtos(produto_id):
    produto = Produto.query.filter(
        Produto.id == produto.id,
        deleted_at = None
    ).first()

    if not produto:
        return jsonify({'message': 'Produto não encontrado para excluído'}), 404
    
    try:
        produto.soft_delete()

        return jsonify({'message': f'Produto ID {produto.id} excluído.'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar o produto: {e}'}), 500    


          
        

    

