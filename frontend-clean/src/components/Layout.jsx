import { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, Users, Calendar, User, MessageCircle, Search, Settings, LogOut, Gamepad2 } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import Notifications from './Notifications';

const Layout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  if (!user) {
    navigate('/login');
    return null;
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    // Implementar busca
    console.log('Buscar:', searchQuery);
  };

  const navItems = [
    { path: '/home', icon: Home, label: 'Feed' },
    { path: '/communities', icon: Users, label: 'Comunidades' },
    { path: '/events', icon: Calendar, label: 'Eventos' },
    { path: '/chat', icon: MessageCircle, label: 'Chat' },
    { path: '/profile', icon: User, label: 'Perfil' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Wallpaper Animado de Fundo */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/20 via-blue-900/30 to-purple-900/20"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      <div className="relative z-10 flex h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-gray-900/80 backdrop-blur-sm border-r border-cyan-500/20 flex flex-col">
          {/* Logo */}
          <div className="p-6 border-b border-cyan-500/20">
            <Link to="/home" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
                <Gamepad2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Gameversu</h1>
                <p className="text-xs text-cyan-400">Rede Social Gamer</p>
              </div>
            </Link>
          </div>

          {/* Navegação */}
          <nav className="flex-1 p-4">
            <ul className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <li key={item.path}>
                    <Link
                      to={item.path}
                      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                        isActive
                          ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/25'
                          : 'text-gray-300 hover:bg-gray-800/50 hover:text-cyan-400'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Perfil do Usuário */}
          <div className="p-4 border-t border-cyan-500/20">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-800/50">
              <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">
                  {user.display_name?.[0] || user.username?.[0] || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">
                  {user.display_name || user.username}
                </p>
                <p className="text-gray-400 text-sm truncate">@{user.username}</p>
              </div>
              <button
                onClick={handleLogout}
                className="text-gray-400 hover:text-red-400 transition-colors"
                title="Sair"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Conteúdo Principal */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="bg-gray-900/80 backdrop-blur-sm border-b border-cyan-500/20 p-4">
            <div className="flex items-center justify-between">
              {/* Busca */}
              <form onSubmit={handleSearch} className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Buscar usuários, comunidades, eventos..."
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                  />
                </div>
              </form>

              {/* Ações do Header */}
              <div className="flex items-center gap-4">
                <Notifications />
                
                <button className="p-2 text-gray-400 hover:text-cyan-400 transition-colors">
                  <Settings className="w-6 h-6" />
                </button>
              </div>
            </div>
          </header>

          {/* Área de Conteúdo */}
          <main className="flex-1 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;

