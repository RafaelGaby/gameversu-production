# Gameversu - Rede Social Gamer Completa 🎮

## Visão Geral

O **Gameversu** é uma rede social completa desenvolvida especificamente para a comunidade gamer. A plataforma oferece um ambiente seguro e interativo onde gamers podem se conectar, formar comunidades, organizar eventos, trocar mensagens em tempo real e compartilhar suas experiências de jogo.

## 🚀 Funcionalidades Implementadas

### ✅ **Sistema de Autenticação Completo**
- Registro e login de usuários
- Perfis personalizáveis com avatar e bio
- Sistema de sessões seguro
- Upload de avatar com redimensionamento automático

### 📱 **Feed Social Avançado**
- Criação e compartilhamento de posts com imagens
- Sistema de curtidas e comentários
- Feed personalizado baseado em seguidores
- Upload de mídia otimizado

### 👥 **Sistema de Comunidades**
- Criação de comunidades públicas e privadas
- Gerenciamento de membros e moderação
- Posts específicos por comunidade
- Sistema de roles (admin, moderador, membro)
- Chat em tempo real por comunidade

### 📅 **Sistema de Eventos**
- Criação e gerenciamento de eventos
- Eventos online e presenciais
- Sistema de RSVP e participação
- Integração com comunidades
- Chat específico para eventos

### 💬 **Chat em Tempo Real (WebSockets)**
- Mensagens diretas entre usuários
- Chat de comunidades
- Chat de eventos
- Indicadores de digitação
- Status online/offline
- Histórico de conversas

### 🔔 **Sistema de Notificações**
- Notificações em tempo real
- Tipos: curtidas, comentários, follows, mensagens, eventos
- Contagem de não lidas
- Marcar como lida individual ou em massa

### 👤 **Sistema de Seguir Usuários**
- Seguir/deixar de seguir usuários
- Feed personalizado baseado em follows
- Contadores de seguidores e seguindo
- Páginas de seguidores e seguindo

### 🎨 **Design Gamer Premium**
- Tema escuro com cores neon (ciano/azul)
- **Wallpaper animado na página principal**
- Interface moderna e responsiva
- Efeitos visuais e animações suaves
- Layout inspirado em plataformas gaming
- Gradientes animados e efeitos de blur

### 📤 **Sistema de Upload de Mídia**
- Upload de imagens para posts e perfis
- Redimensionamento automático
- Otimização de qualidade
- Suporte a PNG, JPG, GIF, WebP
- Limite de 5MB por arquivo

## 🛠 **Tecnologias Utilizadas**

### Backend
- **Flask 3.1.1** - Framework web
- **Flask-SocketIO** - WebSockets para chat em tempo real
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-CORS** - Suporte a CORS
- **Pillow** - Processamento de imagens
- **Werkzeug** - Hash de senhas seguro
- **SQLite** - Banco de dados (desenvolvimento)

### Frontend
- **React 18** - Framework frontend
- **Vite 6.3.5** - Build tool e dev server
- **Tailwind CSS** - Framework de estilos
- **shadcn/ui** - Componentes UI modernos
- **Lucide React** - Ícones
- **Socket.IO Client** - WebSockets no frontend
- **React Router DOM** - Roteamento

## 📋 **APIs Disponíveis**

### Autenticação
- `POST /api/auth/register` - Registro de usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Dados do usuário atual

### Usuários e Follows
- `GET /api/users` - Listar usuários
- `POST /api/users/{id}/follow` - Seguir usuário
- `POST /api/users/{id}/unfollow` - Deixar de seguir
- `GET /api/users/{id}/followers` - Listar seguidores
- `GET /api/users/{id}/following` - Listar seguindo
- `GET /api/users/{id}/is-following` - Verificar se está seguindo

### Comunidades
- `GET /api/communities` - Listar comunidades
- `POST /api/communities` - Criar comunidade
- `POST /api/communities/{id}/join` - Entrar na comunidade
- `POST /api/communities/{id}/leave` - Sair da comunidade

### Eventos
- `GET /api/events` - Listar eventos
- `POST /api/events` - Criar evento
- `POST /api/events/{id}/join` - Participar do evento
- `POST /api/events/{id}/leave` - Sair do evento

### Posts e Comentários
- `GET /api/posts` - Listar posts
- `POST /api/posts` - Criar post
- `POST /api/posts/{id}/like` - Curtir/descurtir post
- `GET /api/posts/{id}/comments` - Listar comentários
- `POST /api/posts/{id}/comments` - Criar comentário

### Mensagens e Chat
- `GET /api/messages` - Obter mensagens
- `POST /api/messages` - Enviar mensagem
- `GET /api/conversations` - Listar conversas
- `PUT /api/messages/{id}/read` - Marcar como lida

### Notificações
- `GET /api/notifications` - Obter notificações
- `PUT /api/notifications/{id}/read` - Marcar como lida
- `PUT /api/notifications/read-all` - Marcar todas como lidas
- `GET /api/notifications/unread-count` - Contagem não lidas

### Upload de Mídia
- `POST /api/upload/image` - Upload de imagem
- `POST /api/upload/avatar` - Upload de avatar
- `GET /uploads/{filename}` - Servir arquivos

## 🎯 **Eventos WebSocket**

### Cliente para Servidor
- `connect` - Conectar ao chat
- `join_chat` - Entrar em sala de chat
- `leave_chat` - Sair de sala de chat
- `send_message` - Enviar mensagem
- `typing` - Indicar digitação

### Servidor para Cliente
- `connected` - Confirmação de conexão
- `new_message` - Nova mensagem recebida
- `new_notification` - Nova notificação
- `user_typing` - Usuário digitando

## 📁 **Estrutura do Projeto**

```
gameversu/
├── gameversu-backend/
│   ├── src/
│   │   ├── models/
│   │   │   └── user.py              # Modelos do banco (User, Community, Event, Post, etc.)
│   │   ├── routes/
│   │   │   ├── auth.py              # Autenticação
│   │   │   ├── communities.py       # Comunidades
│   │   │   ├── events.py            # Eventos
│   │   │   ├── posts.py             # Posts e comentários
│   │   │   ├── messages.py          # Chat e mensagens
│   │   │   ├── notifications.py     # Notificações
│   │   │   ├── follows.py           # Sistema de follows
│   │   │   ├── upload.py            # Upload de mídia
│   │   │   └── user.py              # Usuários
│   │   ├── uploads/                 # Arquivos uploadados
│   │   ├── main.py                  # Aplicação principal
│   │   └── app.db                   # Banco SQLite
│   ├── requirements.txt
│   └── venv/
├── gameversu-frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   └── Register.jsx
│   │   │   ├── ui/                  # Componentes shadcn/ui
│   │   │   ├── Chat.jsx             # Chat em tempo real
│   │   │   ├── Communities.jsx
│   │   │   ├── Events.jsx
│   │   │   ├── Home.jsx             # Feed principal
│   │   │   ├── ImageUpload.jsx      # Upload de imagens
│   │   │   ├── Layout.jsx           # Layout com wallpaper animado
│   │   │   ├── Notifications.jsx    # Sistema de notificações
│   │   │   └── Profile.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.jsx          # Hook de autenticação
│   │   │   └── useSocket.jsx        # Hook para WebSockets
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── dist/                        # Build de produção
│   ├── package.json
│   └── index.html
├── README.md                        # Esta documentação
├── design_document.md               # Documento de design
└── desenvolvimento_continuacao.md   # Log de desenvolvimento
```

## 🚀 **Instalação e Execução**

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- pnpm

### Backend
```bash
cd gameversu-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/main.py
```

### Frontend
```bash
cd gameversu-frontend
pnpm install
pnpm run dev
```

### Acessos
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🔒 **Segurança**

- Hash de senhas com Werkzeug
- Validação de dados no backend
- CORS configurado adequadamente
- Sessões seguras do Flask
- Sanitização de inputs
- Proteção contra SQL Injection
- Upload seguro com validação de tipos
- Redimensionamento automático de imagens

## ⚡ **Performance**

- Paginação em listas de dados
- Lazy loading de componentes
- Otimização automática de imagens
- Cache de dados do usuário
- Queries otimizadas no banco
- WebSockets para comunicação em tempo real
- Build otimizado com Vite

## 🎮 **Recursos Visuais Únicos**

### Wallpaper Animado
- Gradientes animados no fundo
- Efeitos de blur e transparência
- Animações suaves com CSS
- Elementos flutuantes com pulse

### Tema Gamer
- Cores neon ciano/azul
- Bordas brilhantes
- Cards com backdrop blur
- Hover effects e transições
- Ícones de gaming

## 🌐 **Deploy**

O projeto está configurado para deploy em:
- **Frontend**: Plataformas estáticas (Vercel, Netlify, etc.)
- **Backend**: Servidores Python (Heroku, Railway, etc.)
- **Banco**: SQLite (desenvolvimento) / PostgreSQL (produção)

## 📈 **Próximas Melhorias**

- [ ] Versão mobile com React Native
- [ ] Sistema de moderação avançado
- [ ] Analytics e dashboard
- [ ] Integração com APIs de jogos
- [ ] Sistema de conquistas
- [ ] Streaming de vídeo
- [ ] Marketplace de itens

## 🤝 **Contribuição**

O projeto está estruturado de forma modular:
- **Backend**: Adicionar novas rotas em `src/routes/`
- **Frontend**: Criar novos componentes em `src/components/`
- **Banco**: Expandir modelos em `src/models/user.py`

## 📄 **Licença**

Projeto desenvolvido para fins educacionais e demonstração de habilidades em desenvolvimento full-stack.

---

**Gameversu** - A rede social que os gamers merecem! 🎮✨

