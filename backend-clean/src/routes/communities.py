from flask import Blueprint, jsonify, request, session
from src.models.user import Community, User, db, community_members
from datetime import datetime

communities_bp = Blueprint('communities', __name__)

def require_auth():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@communities_bp.route('/communities', methods=['GET'])
def get_communities():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Community.query
        
        if search:
            query = query.filter(Community.name.contains(search))
        
        communities = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'communities': [community.to_dict() for community in communities.items],
            'total': communities.total,
            'pages': communities.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@communities_bp.route('/communities', methods=['POST'])
def create_community():
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        data = request.json
        
        if not data.get('name'):
            return jsonify({'error': 'Nome da comunidade é obrigatório'}), 400
        
        community = Community(
            name=data['name'],
            description=data.get('description', ''),
            banner_url=data.get('banner_url'),
            avatar_url=data.get('avatar_url'),
            is_private=data.get('is_private', False),
            owner_id=session['user_id']
        )
        
        db.session.add(community)
        db.session.flush()  # Para obter o ID da comunidade
        
        # Adicionar o criador como membro admin
        db.session.execute(
            community_members.insert().values(
                user_id=session['user_id'],
                community_id=community.id,
                role='admin'
            )
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comunidade criada com sucesso',
            'community': community.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@communities_bp.route('/communities/<int:community_id>', methods=['GET'])
def get_community(community_id):
    try:
        community = Community.query.get_or_404(community_id)
        
        # Verificar se é privada e se o usuário tem acesso
        if community.is_private:
            if 'user_id' not in session:
                return jsonify({'error': 'Comunidade privada - login necessário'}), 401
            
            user_id = session['user_id']
            is_member = db.session.query(community_members).filter_by(
                user_id=user_id, community_id=community_id
            ).first()
            
            if not is_member:
                return jsonify({'error': 'Acesso negado - você não é membro desta comunidade'}), 403
        
        return jsonify(community.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@communities_bp.route('/communities/<int:community_id>', methods=['PUT'])
def update_community(community_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        community = Community.query.get_or_404(community_id)
        
        # Verificar se é o dono ou admin
        user_id = session['user_id']
        if community.owner_id != user_id:
            member = db.session.query(community_members).filter_by(
                user_id=user_id, community_id=community_id
            ).first()
            if not member or member.role not in ['admin', 'moderator']:
                return jsonify({'error': 'Permissão negada'}), 403
        
        data = request.json
        
        if 'name' in data:
            community.name = data['name']
        if 'description' in data:
            community.description = data['description']
        if 'banner_url' in data:
            community.banner_url = data['banner_url']
        if 'avatar_url' in data:
            community.avatar_url = data['avatar_url']
        if 'is_private' in data and community.owner_id == user_id:
            community.is_private = data['is_private']
        
        community.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Comunidade atualizada com sucesso',
            'community': community.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@communities_bp.route('/communities/<int:community_id>/join', methods=['POST'])
def join_community(community_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        community = Community.query.get_or_404(community_id)
        user_id = session['user_id']
        
        # Verificar se já é membro
        existing_member = db.session.query(community_members).filter_by(
            user_id=user_id, community_id=community_id
        ).first()
        
        if existing_member:
            return jsonify({'error': 'Você já é membro desta comunidade'}), 400
        
        # Adicionar como membro
        db.session.execute(
            community_members.insert().values(
                user_id=user_id,
                community_id=community_id,
                role='member'
            )
        )
        
        db.session.commit()
        
        return jsonify({'message': 'Você entrou na comunidade com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@communities_bp.route('/communities/<int:community_id>/leave', methods=['POST'])
def leave_community(community_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        community = Community.query.get_or_404(community_id)
        user_id = session['user_id']
        
        # Não permitir que o dono saia
        if community.owner_id == user_id:
            return jsonify({'error': 'O dono da comunidade não pode sair'}), 400
        
        # Remover da comunidade
        db.session.execute(
            community_members.delete().where(
                (community_members.c.user_id == user_id) &
                (community_members.c.community_id == community_id)
            )
        )
        
        db.session.commit()
        
        return jsonify({'message': 'Você saiu da comunidade'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@communities_bp.route('/communities/<int:community_id>/members', methods=['GET'])
def get_community_members(community_id):
    try:
        community = Community.query.get_or_404(community_id)
        
        # Verificar acesso para comunidades privadas
        if community.is_private:
            if 'user_id' not in session:
                return jsonify({'error': 'Comunidade privada - login necessário'}), 401
            
            user_id = session['user_id']
            is_member = db.session.query(community_members).filter_by(
                user_id=user_id, community_id=community_id
            ).first()
            
            if not is_member:
                return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar membros
        members_query = db.session.query(User, community_members.c.role, community_members.c.joined_at).join(
            community_members, User.id == community_members.c.user_id
        ).filter(community_members.c.community_id == community_id)
        
        members = []
        for user, role, joined_at in members_query:
            member_data = user.to_dict()
            member_data['role'] = role
            member_data['joined_at'] = joined_at.isoformat()
            members.append(member_data)
        
        return jsonify({'members': members}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

