from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Tabela de associação para membros de comunidades
community_members = db.Table('community_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('community_id', db.Integer, db.ForeignKey('community.id'), primary_key=True),
    db.Column('role', db.String(20), default='member'),  # member, moderator, admin
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

# Tabela de associação para participantes de eventos
event_participants = db.Table('event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

# Tabela de associação para follows
user_follows = db.Table('user_follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy=True, cascade='all, delete-orphan')
    owned_communities = db.relationship('Community', backref='owner', lazy=True)
    created_events = db.relationship('Event', backref='creator', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    
    # Relacionamentos many-to-many
    communities = db.relationship('Community', secondary=community_members, backref='members')
    events = db.relationship('Event', secondary=event_participants, backref='participants')
    
    # Sistema de follows
    following = db.relationship('User', 
                               secondary=user_follows,
                               primaryjoin=id == user_follows.c.follower_id,
                               secondaryjoin=id == user_follows.c.followed_id,
                               backref='followers')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'followers_count': len(self.followers),
            'following_count': len(self.following)
        }

class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    banner_url = db.Column(db.String(255))
    avatar_url = db.Column(db.String(255))
    is_private = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    posts = db.relationship('Post', backref='community', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('Event', backref='community', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='community', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'banner_url': self.banner_url,
            'avatar_url': self.avatar_url,
            'is_private': self.is_private,
            'owner_id': self.owner_id,
            'owner': self.owner.to_dict() if self.owner else None,
            'members_count': len(self.members),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    banner_url = db.Column(db.String(255))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    is_online = db.Column(db.Boolean, default=True)
    max_participants = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    messages = db.relationship('Message', backref='event', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'banner_url': self.banner_url,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'is_online': self.is_online,
            'max_participants': self.max_participants,
            'creator_id': self.creator_id,
            'creator': self.creator.to_dict() if self.creator else None,
            'community_id': self.community_id,
            'community': self.community.to_dict() if self.community else None,
            'participants_count': len(self.participants),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'image_url': self.image_url,
            'author_id': self.author_id,
            'author': self.author.to_dict() if self.author else None,
            'community_id': self.community_id,
            'community': self.community.to_dict() if self.community else None,
            'likes_count': len(self.likes),
            'comments_count': len(self.comments),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author_id': self.author_id,
            'author': self.author.to_dict() if self.author else None,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Para mensagens diretas
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))  # Para chat de comunidade
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))  # Para chat de evento
    message_type = db.Column(db.String(20), default='direct')  # direct, community, event
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'sender_id': self.sender_id,
            'sender': self.sender.to_dict() if self.sender else None,
            'receiver_id': self.receiver_id,
            'receiver': self.receiver.to_dict() if self.receiver else None,
            'community_id': self.community_id,
            'event_id': self.event_id,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    notification_type = db.Column(db.String(50))  # like, comment, follow, message, event, etc.
    related_id = db.Column(db.Integer)  # ID do objeto relacionado (post, user, event, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'notification_type': self.notification_type,
            'related_id': self.related_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

