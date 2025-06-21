import os
import uuid
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from PIL import Image
import io

upload_bp = Blueprint('upload', __name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Criar pasta de uploads se não existir"""
    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path

def resize_image(image_data, max_width=1200, max_height=1200, quality=85):
    """Redimensionar e otimizar imagem"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Converter para RGB se necessário
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Redimensionar mantendo proporção
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Salvar em buffer
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output.getvalue()
    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
        return None

@upload_bp.route('/api/upload/image', methods=['POST'])
def upload_image():
    """Upload de imagem"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    try:
        # Ler dados do arquivo
        file_data = file.read()
        
        if len(file_data) > MAX_FILE_SIZE:
            return jsonify({'error': 'Arquivo muito grande (máximo 5MB)'}), 400
        
        # Processar imagem
        processed_data = resize_image(file_data)
        if not processed_data:
            return jsonify({'error': 'Erro ao processar imagem'}), 400
        
        # Gerar nome único
        file_extension = 'jpg'  # Sempre salvar como JPG após processamento
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Criar pasta de uploads
        upload_path = create_upload_folder()
        file_path = os.path.join(upload_path, filename)
        
        # Salvar arquivo
        with open(file_path, 'wb') as f:
            f.write(processed_data)
        
        # URL para acessar o arquivo
        file_url = f"/uploads/{filename}"
        
        return jsonify({
            'message': 'Upload realizado com sucesso',
            'filename': filename,
            'url': file_url,
            'size': len(processed_data)
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

@upload_bp.route('/api/upload/avatar', methods=['POST'])
def upload_avatar():
    """Upload de avatar do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    try:
        from src.models.user import db, User
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Ler e processar imagem (avatar menor)
        file_data = file.read()
        
        if len(file_data) > MAX_FILE_SIZE:
            return jsonify({'error': 'Arquivo muito grande (máximo 5MB)'}), 400
        
        # Redimensionar para avatar (200x200)
        processed_data = resize_image(file_data, max_width=200, max_height=200, quality=90)
        if not processed_data:
            return jsonify({'error': 'Erro ao processar imagem'}), 400
        
        # Gerar nome único
        filename = f"avatar_{user_id}_{uuid.uuid4().hex}.jpg"
        
        # Criar pasta de uploads
        upload_path = create_upload_folder()
        file_path = os.path.join(upload_path, filename)
        
        # Remover avatar anterior se existir
        if user.avatar_url:
            old_filename = user.avatar_url.split('/')[-1]
            old_path = os.path.join(upload_path, old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        # Salvar novo avatar
        with open(file_path, 'wb') as f:
            f.write(processed_data)
        
        # Atualizar usuário
        user.avatar_url = f"/uploads/{filename}"
        db.session.commit()
        
        return jsonify({
            'message': 'Avatar atualizado com sucesso',
            'avatar_url': user.avatar_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

@upload_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir arquivos uploadados"""
    try:
        upload_path = create_upload_folder()
        file_path = os.path.join(upload_path, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        from flask import send_file
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({'error': f'Erro ao servir arquivo: {str(e)}'}), 500

