from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Validar dados obrigatórios
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email e password são obrigatórios'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username já existe'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já está em uso'}), 400
        
        # Criar novo usuário
        user = User(
            username=data['username'],
            email=data['email'],
            display_name=data.get('display_name', data['username'])
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Fazer login automático
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        # Buscar usuário por username ou email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Atualizar status online
        user.is_online = True
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        # Criar sessão
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        if 'user_id' in session:
            # Atualizar status offline
            user = User.query.get(session['user_id'])
            if user:
                user.is_online = False
                user.last_seen = datetime.utcnow()
                db.session.commit()
            
            session.pop('user_id', None)
        
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify(user.to_dict(include_private=True)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['PUT'])
def update_current_user():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.json
        
        # Atualizar campos permitidos
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

