import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { SocketProvider } from './hooks/useSocket';
import Layout from './components/Layout';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Home from './components/Home';
import Communities from './components/Communities';
import Events from './components/Events';
import Profile from './components/Profile';
import Chat from './components/Chat';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <SocketProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<Layout />}>
                <Route index element={<Navigate to="/home" replace />} />
                <Route path="home" element={<Home />} />
                <Route path="communities" element={<Communities />} />
                <Route path="events" element={<Events />} />
                <Route path="profile" element={<Profile />} />
                <Route path="chat" element={<Chat />} />
                <Route path="chat/:type/:id" element={<Chat />} />
              </Route>
            </Routes>
          </div>
        </Router>
      </SocketProvider>
    </AuthProvider>
  );
}

export default App;

