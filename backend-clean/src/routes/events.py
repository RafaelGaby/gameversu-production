from flask import Blueprint, jsonify, request, session
from src.models.user import Event, User, Community, db, event_participants
from datetime import datetime

events_bp = Blueprint('events', __name__)

def require_auth():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@events_bp.route('/events', methods=['GET'])
def get_events():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        community_id = request.args.get('community_id', type=int)
        
        query = Event.query
        
        if search:
            query = query.filter(Event.title.contains(search))
        
        if community_id:
            query = query.filter(Event.community_id == community_id)
        
        # Ordenar por data de início
        query = query.order_by(Event.start_date.asc())
        
        events = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'events': [event.to_dict() for event in events.items],
            'total': events.total,
            'pages': events.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events', methods=['POST'])
def create_event():
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        data = request.json
        
        if not data.get('title') or not data.get('start_date'):
            return jsonify({'error': 'Título e data de início são obrigatórios'}), 400
        
        # Validar data
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            end_date = None
            if data.get('end_date'):
                end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
        
        # Verificar se a comunidade existe (se especificada)
        community_id = data.get('community_id')
        if community_id:
            community = Community.query.get(community_id)
            if not community:
                return jsonify({'error': 'Comunidade não encontrada'}), 404
        
        event = Event(
            title=data['title'],
            description=data.get('description', ''),
            banner_url=data.get('banner_url'),
            start_date=start_date,
            end_date=end_date,
            location=data.get('location'),
            is_online=data.get('is_online', False),
            max_participants=data.get('max_participants'),
            creator_id=session['user_id'],
            community_id=community_id
        )
        
        db.session.add(event)
        db.session.flush()  # Para obter o ID do evento
        
        # Adicionar o criador como participante
        db.session.execute(
            event_participants.insert().values(
                user_id=session['user_id'],
                event_id=event.id,
                status='going'
            )
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Evento criado com sucesso',
            'event': event.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        return jsonify(event.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        event = Event.query.get_or_404(event_id)
        
        # Verificar se é o criador
        if event.creator_id != session['user_id']:
            return jsonify({'error': 'Permissão negada'}), 403
        
        data = request.json
        
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'banner_url' in data:
            event.banner_url = data['banner_url']
        if 'start_date' in data:
            try:
                event.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de data de início inválido'}), 400
        if 'end_date' in data:
            if data['end_date']:
                try:
                    event.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Formato de data de fim inválido'}), 400
            else:
                event.end_date = None
        if 'location' in data:
            event.location = data['location']
        if 'is_online' in data:
            event.is_online = data['is_online']
        if 'max_participants' in data:
            event.max_participants = data['max_participants']
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Evento atualizado com sucesso',
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<int:event_id>/join', methods=['POST'])
def join_event(event_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        event = Event.query.get_or_404(event_id)
        user_id = session['user_id']
        
        # Verificar se já é participante
        existing_participant = db.session.query(event_participants).filter_by(
            user_id=user_id, event_id=event_id
        ).first()
        
        if existing_participant:
            return jsonify({'error': 'Você já está participando deste evento'}), 400
        
        # Verificar limite de participantes
        if event.max_participants:
            current_participants = len(event.participants)
            if current_participants >= event.max_participants:
                return jsonify({'error': 'Evento lotado'}), 400
        
        # Adicionar como participante
        db.session.execute(
            event_participants.insert().values(
                user_id=user_id,
                event_id=event_id,
                status='going'
            )
        )
        
        db.session.commit()
        
        return jsonify({'message': 'Você se inscreveu no evento com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<int:event_id>/leave', methods=['POST'])
def leave_event(event_id):
    try:
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        event = Event.query.get_or_404(event_id)
        user_id = session['user_id']
        
        # Não permitir que o criador saia
        if event.creator_id == user_id:
            return jsonify({'error': 'O criador do evento não pode sair'}), 400
        
        # Remover do evento
        db.session.execute(
            event_participants.delete().where(
                (event_participants.c.user_id == user_id) &
                (event_participants.c.event_id == event_id)
            )
        )
        
        db.session.commit()
        
        return jsonify({'message': 'Você saiu do evento'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<int:event_id>/participants', methods=['GET'])
def get_event_participants(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        
        # Buscar participantes
        participants_query = db.session.query(User, event_participants.c.status, event_participants.c.joined_at).join(
            event_participants, User.id == event_participants.c.user_id
        ).filter(event_participants.c.event_id == event_id)
        
        participants = []
        for user, status, joined_at in participants_query:
            participant_data = user.to_dict()
            participant_data['status'] = status
            participant_data['joined_at'] = joined_at.isoformat()
            participants.append(participant_data)
        
        return jsonify({'participants': participants}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

