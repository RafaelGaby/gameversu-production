import { createContext, useContext, useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket deve ser usado dentro de um SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Conectar ao servidor WebSocket
    const newSocket = io('http://localhost:5000', {
      withCredentials: true,
      transports: ['websocket', 'polling']
    });

    newSocket.on('connect', () => {
      console.log('Conectado ao servidor WebSocket');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Desconectado do servidor WebSocket');
      setIsConnected(false);
    });

    newSocket.on('connected', (data) => {
      console.log('Confirmação de conexão:', data);
    });

    newSocket.on('new_message', (message) => {
      console.log('Nova mensagem recebida:', message);
      setMessages(prev => [message, ...prev]);
    });

    newSocket.on('new_notification', (notification) => {
      console.log('Nova notificação recebida:', notification);
      setNotifications(prev => [notification, ...prev]);
    });

    newSocket.on('user_typing', (data) => {
      console.log('Usuário digitando:', data);
      // Implementar indicador de digitação
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const joinChat = (type, id) => {
    if (socket) {
      socket.emit('join_chat', { type, id });
    }
  };

  const leaveChat = (type, id) => {
    if (socket) {
      socket.emit('leave_chat', { type, id });
    }
  };

  const sendMessage = (messageData) => {
    if (socket) {
      socket.emit('send_message', messageData);
    }
  };

  const sendTyping = (type, id, typing) => {
    if (socket) {
      socket.emit('typing', { type, id, typing });
    }
  };

  const value = {
    socket,
    isConnected,
    messages,
    notifications,
    joinChat,
    leaveChat,
    sendMessage,
    sendTyping,
    setMessages,
    setNotifications
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};

