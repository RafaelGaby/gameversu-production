import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar'
import { Textarea } from '../ui/textarea'
import { useAuth } from '../hooks/useAuth'
import { 
  Heart, 
  MessageCircle, 
  Share, 
  MoreHorizontal,
  Image as ImageIcon,
  Send
} from 'lucide-react'

export default function Home() {
  const { user } = useAuth()
  const [posts, setPosts] = useState([])
  const [newPost, setNewPost] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/posts', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setPosts(data.posts)
      }
    } catch (error) {
      console.error('Erro ao buscar posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const createPost = async () => {
    if (!newPost.trim()) return

    try {
      const response = await fetch('http://localhost:5000/api/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          content: newPost
        })
      })

      if (response.ok) {
        setNewPost('')
        fetchPosts() // Recarregar posts
      }
    } catch (error) {
      console.error('Erro ao criar post:', error)
    }
  }

  const likePost = async (postId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/posts/${postId}/like`, {
        method: 'POST',
        credentials: 'include'
      })

      if (response.ok) {
        fetchPosts() // Recarregar posts para atualizar likes
      }
    } catch (error) {
      console.error('Erro ao curtir post:', error)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-primary text-xl neon-glow">Carregando feed...</div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Create Post */}
      <Card className="gamer-card">
        <CardHeader>
          <CardTitle className="text-lg">O que está acontecendo?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-4">
            <Avatar className="w-10 h-10 gamer-border">
              <AvatarImage src={user?.avatar_url} />
              <AvatarFallback className="bg-primary/20 text-primary">
                {user?.display_name?.[0]?.toUpperCase() || user?.username?.[0]?.toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <Textarea
                placeholder="Compartilhe suas aventuras gaming..."
                value={newPost}
                onChange={(e) => setNewPost(e.target.value)}
                className="min-h-[100px] gamer-border resize-none"
              />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm">
                <ImageIcon className="w-4 h-4 mr-2" />
                Imagem
              </Button>
            </div>
            <Button 
              onClick={createPost}
              disabled={!newPost.trim()}
              className="gamer-button"
            >
              <Send className="w-4 h-4 mr-2" />
              Postar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Posts Feed */}
      <div className="space-y-4">
        {posts.length === 0 ? (
          <Card className="gamer-card">
            <CardContent className="text-center py-12">
              <p className="text-muted-foreground">
                Nenhum post ainda. Seja o primeiro a compartilhar algo!
              </p>
            </CardContent>
          </Card>
        ) : (
          posts.map((post) => (
            <Card key={post.id} className="gamer-card">
              <CardContent className="p-6">
                {/* Post Header */}
                <div className="flex items-start space-x-3 mb-4">
                  <Avatar className="w-10 h-10 gamer-border">
                    <AvatarImage src={post.author?.avatar_url} />
                    <AvatarFallback className="bg-primary/20 text-primary">
                      {post.author?.display_name?.[0]?.toUpperCase() || post.author?.username?.[0]?.toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-semibold">
                        {post.author?.display_name || post.author?.username}
                      </h4>
                      <span className="text-muted-foreground text-sm">
                        @{post.author?.username}
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
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
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

                {/* Post Actions */}
                <div className="flex items-center space-x-6 text-muted-foreground">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => likePost(post.id)}
                    className={`hover:text-red-500 ${post.user_liked ? 'text-red-500' : ''}`}
                  >
                    <Heart className={`w-4 h-4 mr-2 ${post.user_liked ? 'fill-current' : ''}`} />
                    {post.likes_count}
                  </Button>
                  <Button variant="ghost" size="sm" className="hover:text-blue-500">
                    <MessageCircle className="w-4 h-4 mr-2" />
                    {post.comments_count}
                  </Button>
                  <Button variant="ghost" size="sm" className="hover:text-green-500">
                    <Share className="w-4 h-4 mr-2" />
                    Compartilhar
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

