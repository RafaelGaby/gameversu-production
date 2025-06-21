import os
import sys
# DON'T CHANGE THIS LINE
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, session, request
from flask_cors import CORS
from flask_socketio import SocketIO
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.communities import communities_bp
from src.routes.events import events_bp
from src.routes.posts import posts_bp
from src.routes.messages import messages_bp, init_socketio_events
from src.routes.notifications import notifications_bp
from src.routes.follows import follows_bp
from src.routes.upload import upload_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gameversu-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'https://edurucmk.manus.space'])

# Configurar SocketIO
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5173', 'https://edurucmk.manus.space'])

# Inicializar banco de dados
db.init_app(app)

# Registrar blueprints
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(communities_bp)
app.register_blueprint(events_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(follows_bp)
app.register_blueprint(upload_bp)

# Inicializar eventos do SocketIO
init_socketio_events(socketio)

@app.route('/api/health')
def health_check():
    return {'message': 'Gameversu API está funcionando!', 'status': 'ok'}

@app.before_request
def before_request():
    # Permitir OPTIONS requests para CORS
    if request.method == 'OPTIONS':
        return '', 200

# vvvvvvv  CÓDIGO DE DEBUG ADICIONADO AQUI  vvvvvvv
# Rota de DEBUG temporária para listar todas as rotas
@app.route('/debug/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule.rule))
        output.append(line)
    
    response_body = "<pre>" + "\n".join(sorted(output)) + "</pre>"
    return response_body
# ^^^^^^^  FIM DO CÓDIGO DE DEBUG  ^^^^^^^

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)