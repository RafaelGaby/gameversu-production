import { useState, useEffect, useRef } from 'react';
import { Send, Smile, Paperclip } from 'lucide-react';
import { useSocket } from '../hooks/useSocket';

const Chat = ({ chatType = 'direct', chatId, chatName }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  
  const { socket, isConnected, joinChat, leaveChat, sendMessage, sendTyping } = useSocket();

  useEffect(() => {
    if (chatId) {
      joinChat(chatType, chatId);
      loadMessages();
    }

    return () => {
      if (chatId) {
        leaveChat(chatType, chatId);
      }
    };
  }, [chatId, chatType]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (socket) {
      socket.on('new_message', handleNewMessage);
      socket.on('user_typing', handleUserTyping);
    }

    return () => {
      if (socket) {
        socket.off('new_message', handleNewMessage);
        socket.off('user_typing', handleUserTyping);
      }
    };
  }, [socket]);

  const loadMessages = async () => {
    try {
      const params = new URLSearchParams({
        type: chatType,
        chat_id: chatId
      });
      
      const response = await fetch(`/api/messages?${params}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.reverse());
      }
    } catch (error) {
      console.error('Erro ao carregar mensagens:', error);
    }
  };

  const handleNewMessage = (message) => {
    // Verificar se a mensagem pertence a este chat
    if (
      (chatType === 'direct' && 
       ((message.sender_id === chatId) || (message.receiver_id === chatId))) ||
      (chatType === 'community' && message.community_id === chatId) ||
      (chatType === 'event' && message.event_id === chatId)
    ) {
      setMessages(prev => [...prev, message]);
    }
  };

  const handleUserTyping = (data) => {
    if (data.typing) {
      setTypingUsers(prev => [...prev.filter(u => u.user_id !== data.user_id), data]);
    } else {
      setTypingUsers(prev => prev.filter(u => u.user_id !== data.user_id));
    }

    // Remover indicador após 3 segundos
    setTimeout(() => {
      setTypingUsers(prev => prev.filter(u => u.user_id !== data.user_id));
    }, 3000);
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !isConnected) return;

    const messageData = {
      content: newMessage,
      message_type: chatType
    };

    if (chatType === 'direct') {
      messageData.receiver_id = chatId;
    } else if (chatType === 'community') {
      messageData.community_id = chatId;
    } else if (chatType === 'event') {
      messageData.event_id = chatId;
    }

    sendMessage(messageData);
    setNewMessage('');
    
    // Parar indicador de digitação
    if (isTyping) {
      sendTyping(chatType, chatId, false);
      setIsTyping(false);
    }
  };

  const handleTyping = (e) => {
    setNewMessage(e.target.value);

    if (!isTyping && e.target.value.length > 0) {
      setIsTyping(true);
      sendTyping(chatType, chatId, true);
    }

    // Limpar timeout anterior
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Parar indicador após 2 segundos sem digitar
    typingTimeoutRef.current = setTimeout(() => {
      if (isTyping) {
        sendTyping(chatType, chatId, false);
        setIsTyping(false);
      }
    }, 2000);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 border border-cyan-500/20 rounded-lg">
      {/* Header do Chat */}
      <div className="p-4 border-b border-cyan-500/20 bg-gray-800/50">
        <h3 className="text-lg font-semibold text-white">
          {chatName || `Chat ${chatType}`}
        </h3>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          {isConnected ? 'Conectado' : 'Desconectado'}
        </div>
      </div>

      {/* Área de Mensagens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender?.username === 'current_user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
              message.sender?.username === 'current_user'
                ? 'bg-cyan-600 text-white'
                : 'bg-gray-700 text-gray-100'
            }`}>
              {chatType !== 'direct' && (
                <div className="text-xs text-cyan-300 mb-1">
                  {message.sender?.display_name || message.sender?.username}
                </div>
              )}
              <div className="text-sm">{message.content}</div>
              <div className="text-xs opacity-70 mt-1">
                {formatTime(message.created_at)}
              </div>
            </div>
          </div>
        ))}

        {/* Indicador de digitação */}
        {typingUsers.length > 0 && (
          <div className="flex justify-start">
            <div className="bg-gray-700 px-4 py-2 rounded-lg">
              <div className="text-xs text-cyan-300">
                {typingUsers.map(u => u.username).join(', ')} está digitando...
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input de Mensagem */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-cyan-500/20">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="p-2 text-gray-400 hover:text-cyan-400 transition-colors"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          
          <input
            type="text"
            value={newMessage}
            onChange={handleTyping}
            placeholder="Digite sua mensagem..."
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500"
            disabled={!isConnected}
          />
          
          <button
            type="button"
            className="p-2 text-gray-400 hover:text-cyan-400 transition-colors"
          >
            <Smile className="w-5 h-5" />
          </button>
          
          <button
            type="submit"
            disabled={!newMessage.trim() || !isConnected}
            className="p-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat;

