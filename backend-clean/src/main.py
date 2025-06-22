# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os

# Importações corrigidas para execução como módulo
from .models.user import db
from .routes import auth, communities, events, posts, messages, notifications, follows, upload, user

app = Flask(__name__)
# O ideal é que as instâncias de pastas e db fiquem fora do app factory, mas vamos manter assim por enquanto
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gameversu-super-secret-key-2025')

# Configuração do banco de dados
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Em um contexto de módulo, é mais seguro usar caminhos absolutos baseados na instância do app
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "app.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads' # Esta pasta também deve ser gerenciada com cuidado
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# Configuração CORS
CORS(app, origins=['https://gameversu.com', 'http://localhost:5173'], supports_credentials=True)

# Inicializar extensões
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# BLOCO CORRIGIDO
app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
app.register_blueprint(communities.communities_bp, url_prefix='/api/communities')
app.register_blueprint(events.events_bp, url_prefix='/api/events')
app.register_blueprint(posts.posts_bp, url_prefix='/api/posts')
app.register_blueprint(messages.messages_bp, url_prefix='/api/messages')
app.register_blueprint(notifications.notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(follows.follows_bp, url_prefix='/api/follows')
app.register_blueprint(upload.upload_bp, url_prefix='/api/upload')
app.register_blueprint(user.user_bp, url_prefix='/api/user')


with app.app_context():
    db.create_all()

@app.route('/api/health')
def health():
    return {'status': 'ok'}

@socketio.on('connect')
def on_connect():
    print(f'Cliente conectado: {request.sid}')
    emit('connected', {'data': 'Conectado!'})

# ... (resto dos seus eventos socketio, se houver mais) ...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port)