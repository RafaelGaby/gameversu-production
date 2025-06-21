from flask import Blueprint, jsonify, request, session
from src.models.user import Post, Comment, Like, User, Community, db
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

def require_auth():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        community_id = request.args.get('community_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        query = Post.query
        
        if community_id:
            query = query.filter(Post.community_id == community_id)
        
        if user_id:
            query = query.filter(Post.author_id == user_id)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(Post.created_at.desc())
        
        posts = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        posts_data = []
        for post in posts.items:
            post_dict = post.to_dict()
            
            # Adicionar informações de like do usuário atual
            if 'user_id' in session:
                user_like = Like.query.filter_by(
                    user_id=session['user_id'], 
                    post_id=post.id
                ).first()
                post_dict['user_liked'] = user_like is not None
            else:
                post_dict['user_liked'] = False
            
            posts_data.append(post_dict)
        
        return jsonify({
            'posts': posts_data,
            'total': posts.total,
            'pages': posts.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts', methods=['POST'])
def create_post():
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        data = request.json
        
        if not data.get('content'):
            return jsonify({'error': 'Conteúdo do post é obrigatório'}), 400
        
        # Verificar se a comunidade existe (se especificada)
        community_id = data.get('community_id')
        if community_id:
            community = Community.query.get(community_id)
            if not community:
                return jsonify({'error': 'Comunidade não encontrada'}), 404
        
        post = Post(
            content=data['content'],
            image_url=data.get('image_url'),
            author_id=session['user_id'],
            community_id=community_id
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post criado com sucesso',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        
        post_dict = post.to_dict()
        
        # Adicionar informações de like do usuário atual
        if 'user_id' in session:
            user_like = Like.query.filter_by(
                user_id=session['user_id'], 
                post_id=post.id
            ).first()
            post_dict['user_liked'] = user_like is not None
        else:
            post_dict['user_liked'] = False
        
        return jsonify(post_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        post = Post.query.get_or_404(post_id)
        
        # Verificar se é o autor
        if post.author_id != session['user_id']:
            return jsonify({'error': 'Permissão negada'}), 403
        
        data = request.json
        
        if 'content' in data:
            post.content = data['content']
        if 'image_url' in data:
            post.image_url = data['image_url']
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Post atualizado com sucesso',
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        post = Post.query.get_or_404(post_id)
        
        # Verificar se é o autor
        if post.author_id != session['user_id']:
            return jsonify({'error': 'Permissão negada'}), 403
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        post = Post.query.get_or_404(post_id)
        user_id = session['user_id']
        
        # Verificar se já curtiu
        existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
        
        if existing_like:
            # Remover like (descurtir)
            db.session.delete(existing_like)
            action = 'descurtido'
        else:
            # Adicionar like
            like = Like(user_id=user_id, post_id=post_id)
            db.session.add(like)
            action = 'curtido'
        
        db.session.commit()
        
        # Retornar contagem atualizada
        likes_count = Like.query.filter_by(post_id=post_id).count()
        
        return jsonify({
            'message': f'Post {action} com sucesso',
            'likes_count': likes_count,
            'user_liked': action == 'curtido'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        comments = Comment.query.filter_by(post_id=post_id).order_by(
            Comment.created_at.asc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments.items],
            'total': comments.total,
            'pages': comments.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        post = Post.query.get_or_404(post_id)
        data = request.json
        
        if not data.get('content'):
            return jsonify({'error': 'Conteúdo do comentário é obrigatório'}), 400
        
        comment = Comment(
            content=data['content'],
            author_id=session['user_id'],
            post_id=post_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comentário criado com sucesso',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        comment = Comment.query.get_or_404(comment_id)
        
        # Verificar se é o autor
        if comment.author_id != session['user_id']:
            return jsonify({'error': 'Permissão negada'}), 403
        
        data = request.json
        
        if 'content' in data:
            comment.content = data['content']
        
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Comentário atualizado com sucesso',
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        comment = Comment.query.get_or_404(comment_id)
        
        # Verificar se é o autor
        if comment.author_id != session['user_id']:
            return jsonify({'error': 'Permissão negada'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comentário deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

