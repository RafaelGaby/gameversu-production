from flask import Blueprint, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from src.models.user import db, Message, User, Community, Event
from datetime import datetime

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """Obter mensagens do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    message_type = request.args.get('type', 'direct')
    chat_id = request.args.get('chat_id')
    
    query = Message.query.filter_by(message_type=message_type)
    
    if message_type == 'direct':
        if chat_id:
            # Mensagens entre dois usuários específicos
            query = query.filter(
                ((Message.sender_id == user_id) & (Message.receiver_id == chat_id)) |
                ((Message.sender_id == chat_id) & (Message.receiver_id == user_id))
            )
        else:
            # Todas as mensagens diretas do usuário
            query = query.filter(
                (Message.sender_id == user_id) | (Message.receiver_id == user_id)
            )
    elif message_type == 'community' and chat_id:
        query = query.filter_by(community_id=chat_id)
    elif message_type == 'event' and chat_id:
        query = query.filter_by(event_id=chat_id)
    
    messages = query.order_by(Message.created_at.desc()).limit(50).all()
    return jsonify([message.to_dict() for message in messages])

@messages_bp.route('/api/messages', methods=['POST'])
def send_message():
    """Enviar mensagem"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    message = Message(
        content=data['content'],
        sender_id=user_id,
        receiver_id=data.get('receiver_id'),
        community_id=data.get('community_id'),
        event_id=data.get('event_id'),
        message_type=data.get('message_type', 'direct')
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify(message.to_dict()), 201

@messages_bp.route('/api/messages/<int:message_id>/read', methods=['PUT'])
def mark_message_read(message_id):
    """Marcar mensagem como lida"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    message = Message.query.get_or_404(message_id)
    
    # Verificar se o usuário pode marcar esta mensagem como lida
    if message.receiver_id != user_id:
        return jsonify({'error': 'Não autorizado'}), 403
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Mensagem marcada como lida'})

@messages_bp.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Obter lista de conversas do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    
    # Buscar últimas mensagens de cada conversa
    conversations = []
    
    # Conversas diretas
    direct_messages = db.session.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id),
        Message.message_type == 'direct'
    ).order_by(Message.created_at.desc()).all()
    
    seen_users = set()
    for msg in direct_messages:
        other_user_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
        if other_user_id not in seen_users:
            seen_users.add(other_user_id)
            other_user = User.query.get(other_user_id)
            conversations.append({
                'type': 'direct',
                'id': other_user_id,
                'name': other_user.display_name or other_user.username,
                'avatar': other_user.avatar_url,
                'last_message': msg.to_dict(),
                'unread_count': Message.query.filter_by(
                    sender_id=other_user_id,
                    receiver_id=user_id,
                    is_read=False
                ).count()
            })
    
    return jsonify(conversations)

# WebSocket events para chat em tempo real
def init_socketio_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        if 'user_id' in session:
            user_id = session['user_id']
            join_room(f'user_{user_id}')
            
            # Atualizar status online
            user = User.query.get(user_id)
            if user:
                user.is_online = True
                user.last_seen = datetime.utcnow()
                db.session.commit()
            
            emit('connected', {'message': 'Conectado ao chat'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if 'user_id' in session:
            user_id = session['user_id']
            leave_room(f'user_{user_id}')
            
            # Atualizar status offline
            user = User.query.get(user_id)
            if user:
                user.is_online = False
                user.last_seen = datetime.utcnow()
                db.session.commit()
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        if 'user_id' not in session:
            return
        
        chat_type = data.get('type')
        chat_id = data.get('id')
        
        if chat_type == 'community':
            join_room(f'community_{chat_id}')
        elif chat_type == 'event':
            join_room(f'event_{chat_id}')
        elif chat_type == 'direct':
            join_room(f'direct_{chat_id}')
    
    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        chat_type = data.get('type')
        chat_id = data.get('id')
        
        if chat_type == 'community':
            leave_room(f'community_{chat_id}')
        elif chat_type == 'event':
            leave_room(f'event_{chat_id}')
        elif chat_type == 'direct':
            leave_room(f'direct_{chat_id}')
    
    @socketio.on('send_message')
    def handle_send_message(data):
        if 'user_id' not in session:
            return
        
        user_id = session['user_id']
        
        # Criar mensagem no banco
        message = Message(
            content=data['content'],
            sender_id=user_id,
            receiver_id=data.get('receiver_id'),
            community_id=data.get('community_id'),
            event_id=data.get('event_id'),
            message_type=data.get('message_type', 'direct')
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Emitir mensagem para a sala apropriada
        message_data = message.to_dict()
        
        if message.message_type == 'direct':
            # Enviar para ambos os usuários
            socketio.emit('new_message', message_data, room=f'user_{user_id}')
            if message.receiver_id:
                socketio.emit('new_message', message_data, room=f'user_{message.receiver_id}')
        elif message.message_type == 'community':
            socketio.emit('new_message', message_data, room=f'community_{message.community_id}')
        elif message.message_type == 'event':
            socketio.emit('new_message', message_data, room=f'event_{message.event_id}')
    
    @socketio.on('typing')
    def handle_typing(data):
        if 'user_id' not in session:
            return
        
        user_id = session['user_id']
        chat_type = data.get('type')
        chat_id = data.get('id')
        is_typing = data.get('typing', False)
        
        user = User.query.get(user_id)
        typing_data = {
            'user_id': user_id,
            'username': user.username,
            'typing': is_typing
        }
        
        if chat_type == 'community':
            emit('user_typing', typing_data, room=f'community_{chat_id}', include_self=False)
        elif chat_type == 'event':
            emit('user_typing', typing_data, room=f'event_{chat_id}', include_self=False)
        elif chat_type == 'direct':
            emit('user_typing', typing_data, room=f'user_{chat_id}', include_self=False)

