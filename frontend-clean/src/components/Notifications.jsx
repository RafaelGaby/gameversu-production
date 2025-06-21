import { useState, useEffect } from 'react';
import { Bell, Check, X } from 'lucide-react';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
  }, []);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/notifications', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications);
      }
    } catch (error) {
      console.error('Erro ao carregar notificações:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await fetch('/api/notifications/unread-count', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Erro ao carregar contagem:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        credentials: 'include'
      });
      
      if (response.ok) {
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? { ...notif, is_read: true }
              : notif
          )
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Erro ao marcar como lida:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const response = await fetch('/api/notifications/read-all', {
        method: 'PUT',
        credentials: 'include'
      });
      
      if (response.ok) {
        setNotifications(prev => 
          prev.map(notif => ({ ...notif, is_read: true }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Erro ao marcar todas como lidas:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'like':
        return '❤️';
      case 'comment':
        return '💬';
      case 'follow':
        return '👤';
      case 'message':
        return '📩';
      case 'event':
        return '📅';
      default:
        return '🔔';
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Agora';
    if (minutes < 60) return `${minutes}m`;
    if (hours < 24) return `${hours}h`;
    return `${days}d`;
  };

  return (
    <div className="relative">
      {/* Botão de Notificações */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-400 hover:text-cyan-400 transition-colors"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown de Notificações */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-gray-800 border border-cyan-500/20 rounded-lg shadow-xl z-50">
          {/* Header */}
          <div className="p-4 border-b border-cyan-500/20 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Notificações</h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-cyan-400 hover:text-cyan-300"
                >
                  Marcar todas como lidas
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Lista de Notificações */}
          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-400">
                Carregando...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                Nenhuma notificação
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-700 hover:bg-gray-700/50 transition-colors ${
                    !notification.is_read ? 'bg-cyan-900/20' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">
                      {getNotificationIcon(notification.notification_type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-white">
                            {notification.title}
                          </h4>
                          {notification.content && (
                            <p className="text-sm text-gray-400 mt-1">
                              {notification.content}
                            </p>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-2 ml-2">
                          <span className="text-xs text-gray-500">
                            {formatTime(notification.created_at)}
                          </span>
                          
                          {!notification.is_read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="text-cyan-400 hover:text-cyan-300"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                      
                      {!notification.is_read && (
                        <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2" />
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-cyan-500/20">
            <button
              onClick={() => {
                setIsOpen(false);
                // Navegar para página de notificações
              }}
              className="w-full text-center text-sm text-cyan-400 hover:text-cyan-300"
            >
              Ver todas as notificações
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Notifications;

