from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, user_follows
from src.routes.notifications import create_notification

follows_bp = Blueprint('follows', __name__)

@follows_bp.route('/api/users/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    """Seguir um usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    current_user_id = session['user_id']
    
    if current_user_id == user_id:
        return jsonify({'error': 'Você não pode seguir a si mesmo'}), 400
    
    user_to_follow = User.query.get_or_404(user_id)
    current_user = User.query.get(current_user_id)
    
    # Verificar se já está seguindo
    if user_to_follow in current_user.following:
        return jsonify({'error': 'Você já está seguindo este usuário'}), 400
    
    # Adicionar follow
    current_user.following.append(user_to_follow)
    db.session.commit()
    
    # Criar notificação
    create_notification(
        user_id=user_id,
        title='Novo seguidor',
        content=f'{current_user.display_name or current_user.username} começou a seguir você',
        notification_type='follow',
        related_id=current_user_id
    )
    
    return jsonify({'message': 'Usuário seguido com sucesso'})

@follows_bp.route('/api/users/<int:user_id>/unfollow', methods=['POST'])
def unfollow_user(user_id):
    """Deixar de seguir um usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    current_user_id = session['user_id']
    
    if current_user_id == user_id:
        return jsonify({'error': 'Você não pode deixar de seguir a si mesmo'}), 400
    
    user_to_unfollow = User.query.get_or_404(user_id)
    current_user = User.query.get(current_user_id)
    
    # Verificar se está seguindo
    if user_to_unfollow not in current_user.following:
        return jsonify({'error': 'Você não está seguindo este usuário'}), 400
    
    # Remover follow
    current_user.following.remove(user_to_unfollow)
    db.session.commit()
    
    return jsonify({'message': 'Usuário deixou de ser seguido'})

@follows_bp.route('/api/users/<int:user_id>/followers', methods=['GET'])
def get_followers(user_id):
    """Obter seguidores de um usuário"""
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    followers = User.query.join(user_follows, User.id == user_follows.c.follower_id).filter(
        user_follows.c.followed_id == user_id
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'followers': [follower.to_dict() for follower in followers.items],
        'total': followers.total,
        'pages': followers.pages,
        'current_page': page,
        'has_next': followers.has_next,
        'has_prev': followers.has_prev
    })

@follows_bp.route('/api/users/<int:user_id>/following', methods=['GET'])
def get_following(user_id):
    """Obter usuários que um usuário está seguindo"""
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    following = User.query.join(user_follows, User.id == user_follows.c.followed_id).filter(
        user_follows.c.follower_id == user_id
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'following': [followed.to_dict() for followed in following.items],
        'total': following.total,
        'pages': following.pages,
        'current_page': page,
        'has_next': following.has_next,
        'has_prev': following.has_prev
    })

@follows_bp.route('/api/users/<int:user_id>/is-following', methods=['GET'])
def is_following(user_id):
    """Verificar se o usuário atual está seguindo outro usuário"""
    if 'user_id' not in session:
        return jsonify({'is_following': False})
    
    current_user_id = session['user_id']
    
    if current_user_id == user_id:
        return jsonify({'is_following': False})
    
    current_user = User.query.get(current_user_id)
    user_to_check = User.query.get_or_404(user_id)
    
    is_following = user_to_check in current_user.following
    
    return jsonify({'is_following': is_following})

