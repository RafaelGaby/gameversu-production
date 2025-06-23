import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/buttoncard'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/buttonavatar'
import { Badge } from '@/components/ui/buttonbadge'
import { Users, Plus, Lock, Globe } from 'lucide-react'

export default function Communities() {
  const [communities, setCommunities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCommunities()
  }, [])

  const fetchCommunities = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/communities', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setCommunities(data.communities)
      }
    } catch (error) {
      console.error('Erro ao buscar comunidades:', error)
    } finally {
      setLoading(false)
    }
  }

  const joinCommunity = async (communityId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/communities/${communityId}/join`, {
        method: 'POST',
        credentials: 'include'
      })

      if (response.ok) {
        fetchCommunities() // Recarregar comunidades
      }
    } catch (error) {
      console.error('Erro ao entrar na comunidade:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-primary text-xl neon-glow">Carregando comunidades...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary neon-glow">Comunidades</h1>
          <p className="text-muted-foreground mt-2">
            Encontre e participe de comunidades gaming
          </p>
        </div>
        <Button className="gamer-button">
          <Plus className="w-4 h-4 mr-2" />
          Criar Comunidade
        </Button>
      </div>

      {/* Communities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {communities.length === 0 ? (
          <div className="col-span-full">
            <Card className="gamer-card">
              <CardContent className="text-center py-12">
                <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Nenhuma comunidade encontrada. Seja o primeiro a criar uma!
                </p>
              </CardContent>
            </Card>
          </div>
        ) : (
          communities.map((community) => (
            <Card key={community.id} className="gamer-card hover:gamer-border transition-all duration-300">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <Avatar className="w-12 h-12 gamer-border">
                      <AvatarImage src={community.avatar_url} />
                      <AvatarFallback className="bg-primary/20 text-primary">
                        {community.name[0]?.toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-lg">{community.name}</CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        {community.is_private ? (
                          <Lock className="w-3 h-3 text-muted-foreground" />
                        ) : (
                          <Globe className="w-3 h-3 text-muted-foreground" />
                        )}
                        <span className="text-xs text-muted-foreground">
                          {community.is_private ? 'Privada' : 'Pública'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {community.description || 'Sem descrição disponível.'}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span>{community.members_count} membros</span>
                    </div>
                  </div>
                  
                  <Badge variant="secondary" className="text-xs">
                    {community.owner?.display_name || community.owner?.username}
                  </Badge>
                </div>

                <Button 
                  onClick={() => joinCommunity(community.id)}
                  className="w-full gamer-button"
                  size="sm"
                >
                  Entrar na Comunidade
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

