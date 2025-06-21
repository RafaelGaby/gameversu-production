from flask import Blueprint, request, jsonify, session
from src.models.user import db, Notification, User

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Obter notificações do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)
    
    query = Notification.query.filter_by(user_id=user_id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'notifications': [notification.to_dict() for notification in notifications.items],
        'total': notifications.total,
        'pages': notifications.pages,
        'current_page': page,
        'has_next': notifications.has_next,
        'has_prev': notifications.has_prev
    })

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Marcar notificação como lida"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != user_id:
        return jsonify({'error': 'Não autorizado'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Notificação marcada como lida'})

@notifications_bp.route('/api/notifications/read-all', methods=['PUT'])
def mark_all_notifications_read():
    """Marcar todas as notificações como lidas"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'message': 'Todas as notificações marcadas como lidas'})

@notifications_bp.route('/api/notifications/unread-count', methods=['GET'])
def get_unread_count():
    """Obter contagem de notificações não lidas"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    return jsonify({'unread_count': count})

def create_notification(user_id, title, content, notification_type, related_id=None):
    """Função helper para criar notificações"""
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        notification_type=notification_type,
        related_id=related_id
    )
    
    db.session.add(notification)
    db.session.commit()
    
    return notification

