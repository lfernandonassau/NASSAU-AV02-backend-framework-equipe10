from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from ..extensions import db
from ..models import Pedido

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
