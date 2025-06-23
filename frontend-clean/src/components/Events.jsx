import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar'
import { Badge } from '../ui/badge'
import { Calendar, MapPin, Users, Plus, Clock, Globe } from 'lucide-react'

export default function Events() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/events', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setEvents(data.events)
      }
    } catch (error) {
      console.error('Erro ao buscar eventos:', error)
    } finally {
      setLoading(false)
    }
  }

  const joinEvent = async (eventId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/events/${eventId}/join`, {
        method: 'POST',
        credentials: 'include'
      })

      if (response.ok) {
        fetchEvents() // Recarregar eventos
      }
    } catch (error) {
      console.error('Erro ao participar do evento:', error)
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

  const isEventPast = (dateString) => {
    return new Date(dateString) < new Date()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-primary text-xl neon-glow">Carregando eventos...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary neon-glow">Eventos</h1>
          <p className="text-muted-foreground mt-2">
            Descubra e participe de eventos gaming incríveis
          </p>
        </div>
        <Button className="gamer-button">
          <Plus className="w-4 h-4 mr-2" />
          Criar Evento
        </Button>
      </div>

      {/* Events List */}
      <div className="space-y-4">
        {events.length === 0 ? (
          <Card className="gamer-card">
            <CardContent className="text-center py-12">
              <Calendar className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                Nenhum evento encontrado. Seja o primeiro a criar um!
              </p>
            </CardContent>
          </Card>
        ) : (
          events.map((event) => (
            <Card key={event.id} className="gamer-card hover:gamer-border transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  {/* Event Banner/Avatar */}
                  <div className="flex-shrink-0">
                    <Avatar className="w-16 h-16 gamer-border">
                      <AvatarImage src={event.banner_url} />
                      <AvatarFallback className="bg-primary/20 text-primary text-lg">
                        {event.title[0]?.toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </div>

                  {/* Event Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-xl font-semibold text-foreground mb-1">
                          {event.title}
                        </h3>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <span>por {event.creator?.display_name || event.creator?.username}</span>
                          {event.community && (
                            <>
                              <span>·</span>
                              <span className="text-primary">{event.community.name}</span>
                            </>
                          )}
                        </div>
                      </div>
                      
                      {isEventPast(event.start_date) && (
                        <Badge variant="secondary">Finalizado</Badge>
                      )}
                    </div>

                    <p className="text-muted-foreground mb-4 line-clamp-2">
                      {event.description || 'Sem descrição disponível.'}
                    </p>

                    {/* Event Details */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="flex items-center space-x-2 text-sm">
                        <Calendar className="w-4 h-4 text-primary" />
                        <span>{formatDate(event.start_date)}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2 text-sm">
                        {event.is_online ? (
                          <>
                            <Globe className="w-4 h-4 text-primary" />
                            <span>Online</span>
                          </>
                        ) : (
                          <>
                            <MapPin className="w-4 h-4 text-primary" />
                            <span>{event.location || 'Local não informado'}</span>
                          </>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2 text-sm">
                        <Users className="w-4 h-4 text-primary" />
                        <span>
                          {event.participants_count} participantes
                          {event.max_participants && ` / ${event.max_participants}`}
                        </span>
                      </div>
                    </div>

                    {/* Event Actions */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {event.end_date && (
                          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            <span>até {formatDate(event.end_date)}</span>
                          </div>
                        )}
                      </div>
                      
                      {!isEventPast(event.start_date) && (
                        <Button 
                          onClick={() => joinEvent(event.id)}
                          className="gamer-button"
                          size="sm"
                          disabled={event.max_participants && event.participants_count >= event.max_participants}
                        >
                          {event.max_participants && event.participants_count >= event.max_participants 
                            ? 'Lotado' 
                            : 'Participar'
                          }
                        </Button>
                      )}
                    </div>
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

