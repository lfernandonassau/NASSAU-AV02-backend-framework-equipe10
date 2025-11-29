from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models import Pedido

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

def serialize_pedido(pedido):
    return{
        'id': pedido.id,
        'user_id': pedido.user_id,
        'data_pedido': pedido.data_pedido.isoformat(),
        'status': pedido.status,
        'valor_status': pedido.valor_total,
        'deleted': pedido.deleted
    }
#1º Rota: Criar pedido
@pedidos_bp.route('/', methods=['POST'])
@login_required #Apenas usuários logados podem fazer pedidos.
def create_pedido():
    
    data = request.get_json()

    novo_pedido = Pedido(
        user_id = current_user.id,
        status = data.get('status', 'Pendente.'),
        valor_total = data.get('valor', 0.0)
    )

    try:
        db.session.add(novo_pedido)
        db.session.commit()
        return jsonify({
            'message': 'Pedido criado com êxito!',
            'pedido': serialize_pedido(novo_pedido)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify ({'message': f'Erro ao criar Pedido:{e}'}), 500
    
#2º Rota: Listar pedidos     
@pedidos_bp.route('/meus', methods=['GET'])
@login_required
def listar_meus_pedidos():
    try:
        pedidos = Pedido.query.filter_by(user_id=current_user.id).filter(Pedido.deleted_at.is_(None)).all()
        resultado = []
        for pedido in pedidos:
            resultado.append({
                'id': pedido.id,
                'data_pedido': pedido.data_pedido.isoformat(),
                'status': pedido.status,
                'valor_total': pedido.valor_total
            })
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao listar pedidos: {e}'}), 500

#3º Rota: Excluir pedido
@pedidos_bp.route('/<int:pedido_id>', methods=['DELETE'])
@login_required
def excluir_pedido(pedido_id):
    
    try:
        # Busca o pedido, não importa se está deletado ou não para poder restaurá-lo, mas vamos focar na exclusão
        pedido = Pedido.query.get(pedido_id)

        if not pedido:
            return jsonify({'message': 'Pedido não encontrado.'}), 404
            
        if pedido.user_id != current_user.id:
            return jsonify({'message': 'Acesso negado. Você não tem permissão para excluir este pedido.'}), 403 # 403 Forbidden

        if pedido.status not in ['Criado', 'Processando']:
             return jsonify({'message': f'Não é possível excluir o pedido no status atual: {pedido.status}'}), 400

        
        pedido.soft_delete() 
        db.session.commit()

        return jsonify({'message': 'Pedido excluído com sucesso (Soft Delete).'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao excluir pedido: {e}'}), 500