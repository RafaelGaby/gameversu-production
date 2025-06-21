import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';

const ImageUpload = ({ onUpload, currentImage, type = 'image', className = '' }) => {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(currentImage);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUpload = async (file) => {
    // Validar tipo de arquivo
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('Tipo de arquivo não permitido. Use JPG, PNG, GIF ou WebP.');
      return;
    }

    // Validar tamanho (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Arquivo muito grande. Máximo 5MB.');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const endpoint = type === 'avatar' ? '/api/upload/avatar' : '/api/upload/image';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setPreview(data.url || data.avatar_url);
        
        if (onUpload) {
          onUpload(data.url || data.avatar_url);
        }
      } else {
        const error = await response.json();
        alert(error.error || 'Erro no upload');
      }
    } catch (error) {
      console.error('Erro no upload:', error);
      alert('Erro no upload da imagem');
    } finally {
      setUploading(false);
    }
  };

  const removeImage = () => {
    setPreview(null);
    if (onUpload) {
      onUpload(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={`relative ${className}`}>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />

      {preview ? (
        <div className="relative group">
          <img
            src={preview}
            alt="Preview"
            className={`w-full h-full object-cover rounded-lg ${
              type === 'avatar' ? 'w-32 h-32 rounded-full' : ''
            }`}
          />
          
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
            <button
              onClick={removeImage}
              className="p-2 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        <div
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className={`border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-cyan-500 transition-colors ${
            uploading ? 'opacity-50 cursor-not-allowed' : ''
          } ${type === 'avatar' ? 'w-32 h-32 p-4' : ''}`}
        >
          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
              <span className="text-sm text-gray-400">Enviando...</span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              {type === 'avatar' ? (
                <Upload className="w-6 h-6 text-gray-400" />
              ) : (
                <ImageIcon className="w-12 h-12 text-gray-400" />
              )}
              <div className="text-gray-400">
                <p className="text-sm font-medium">
                  {type === 'avatar' ? 'Avatar' : 'Clique ou arraste uma imagem'}
                </p>
                {type !== 'avatar' && (
                  <p className="text-xs">PNG, JPG, GIF até 5MB</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageUpload;

