# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os

# Importações para produção
from models.user import db
from routes import auth, communities, events, posts, messages, notifications, follows, upload, user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gameversu-super-secret-key-2025')

# Configuração do banco de dados
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Corrige a URL do SQLAlchemy para o PostgreSQL em produção
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url:
    # Produção - PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Desenvolvimento - SQLite
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# Configuração CORS
CORS(app, origins=['https://gameversu.com', 'http://localhost:5173'], supports_credentials=True)

# Inicializar extensões
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Registrar blueprints com prefixo de API
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(communities.bp, url_prefix='/api/communities')
app.register_blueprint(events.bp, url_prefix='/api/events')
app.register_blueprint(posts.bp, url_prefix='/api/posts')
app.register_blueprint(messages.bp, url_prefix='/api/messages')
app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
app.register_blueprint(follows.bp, url_prefix='/api/follows')
app.register_blueprint(upload.bp, url_prefix='/api/upload')
app.register_blueprint(user.bp, url_prefix='/api/user')

with app.app_context():
    db.create_all()

@app.route('/api/health')
def health():
    return {'status': 'ok'}

# ... (resto dos seus eventos socketio) ...

@socketio.on('connect')
def on_connect():
    print(f'Cliente conectado: {request.sid}')
    emit('connected', {'data': 'Conectado!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port)