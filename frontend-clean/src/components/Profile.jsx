import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar'
import { Badge } from '../ui/badge'
import { useAuth } from '../hooks/useAuth'
import { 
  User, 
  Calendar, 
  Users, 
  Heart, 
  MessageCircle,
  Settings,
  Edit
} from 'lucide-react'

export default function Profile() {
  const { user } = useAuth()
  const [userPosts, setUserPosts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      fetchUserPosts()
    }
  }, [user])

  const fetchUserPosts = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/posts?user_id=${user.id}`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setUserPosts(data.posts)
      }
    } catch (error) {
      console.error('Erro ao buscar posts do usuário:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-primary text-xl neon-glow">Carregando perfil...</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <Card className="gamer-card">
        <CardContent className="p-6">
          <div className="flex items-start space-x-6">
            {/* Avatar */}
            <Avatar className="w-24 h-24 gamer-border">
              <AvatarImage src={user?.avatar_url} />
              <AvatarFallback className="bg-primary/20 text-primary text-2xl">
                {user?.display_name?.[0]?.toUpperCase() || user?.username?.[0]?.toUpperCase()}
              </AvatarFallback>
            </Avatar>

            {/* User Info */}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-2xl font-bold text-foreground">
                    {user?.display_name || user?.username}
                  </h1>
                  <p className="text-muted-foreground">@{user?.username}</p>
                </div>
                <Button className="gamer-button">
                  <Edit className="w-4 h-4 mr-2" />
                  Editar Perfil
                </Button>
              </div>

              {/* Bio */}
              {user?.bio && (
                <p className="text-foreground mb-4">{user.bio}</p>
              )}

              {/* Stats */}
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-4 h-4 text-primary" />
                  <span className="text-muted-foreground">
                    Entrou em {formatDate(user?.created_at)}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="w-4 h-4 text-primary" />
                  <span className="text-foreground font-medium">{user?.followers_count || 0}</span>
                  <span className="text-muted-foreground">seguidores</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-foreground font-medium">{user?.following_count || 0}</span>
                  <span className="text-muted-foreground">seguindo</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile Navigation */}
      <Card className="gamer-card">
        <CardContent className="p-4">
          <div className="flex space-x-6">
            <Button variant="ghost" className="text-primary border-b-2 border-primary">
              Posts ({userPosts.length})
            </Button>
            <Button variant="ghost" className="text-muted-foreground">
              Comunidades
            </Button>
            <Button variant="ghost" className="text-muted-foreground">
              Eventos
            </Button>
            <Button variant="ghost" className="text-muted-foreground">
              Curtidas
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* User Posts */}
      <div className="space-y-4">
        {userPosts.length === 0 ? (
          <Card className="gamer-card">
            <CardContent className="text-center py-12">
              <MessageCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                Você ainda não fez nenhum post. Compartilhe suas aventuras gaming!
              </p>
            </CardContent>
          </Card>
        ) : (
          userPosts.map((post) => (
            <Card key={post.id} className="gamer-card">
              <CardContent className="p-6">
                {/* Post Header */}
                <div className="flex items-start space-x-3 mb-4">
                  <Avatar className="w-10 h-10 gamer-border">
                    <AvatarImage src={user?.avatar_url} />
                    <AvatarFallback className="bg-primary/20 text-primary">
                      {user?.display_name?.[0]?.toUpperCase() || user?.username?.[0]?.toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-semibold">
                        {user?.display_name || user?.username}
                      </h4>
                      <span className="text-muted-foreground text-sm">
                        @{user?.username}
                      </span>
                      <span className="text-muted-foreground text-sm">
                        · {formatDate(post.created_at)}
                      </span>
                    </div>
                    {post.community && (
                      <p className="text-sm text-primary">
                        em {post.community.name}
                      </p>
                    )}
                  </div>
                </div>

                {/* Post Content */}
                <div className="mb-4">
                  <p className="text-foreground whitespace-pre-wrap">
                    {post.content}
                  </p>
                  {post.image_url && (
                    <img 
                      src={post.image_url} 
                      alt="Post image" 
                      className="mt-3 rounded-lg max-w-full h-auto gamer-border"
                    />
                  )}
                </div>

                {/* Post Stats */}
                <div className="flex items-center space-x-6 text-muted-foreground text-sm">
                  <div className="flex items-center space-x-1">
                    <Heart className="w-4 h-4" />
                    <span>{post.likes_count} curtidas</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MessageCircle className="w-4 h-4" />
                    <span>{post.comments_count} comentários</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

