"""Renderer de Pong sobre el motor SDL compartido."""
from .sdl_viewport import SDLViewport, pygame


class PongViewport(SDLViewport):
    title="Pong"
    def draw(self,game):
        r=self.renderer
        r.draw_color=(29,53,79,255)
        r.clear()
        r.draw_color=(80,102,125,255)
        for y in range(10,440,24):r.fill_rect(pygame.FRect(399,y,2,12))
        self.label("TÚ",270,26,15,"#a4d4df",True)
        self.label("CPU",530,26,15,"#dac5a1",True)
        self.label(str(game.player_score),270,65,40,"#dce6ef",True)
        self.label(str(game.cpu_score),530,65,40,"#dce6ef",True)
        half=game.PADDLE_HEIGHT/2
        r.draw_color=(156,216,233,255)
        r.fill_rect(pygame.FRect(28,game.player-half,12,game.PADDLE_HEIGHT))
        r.draw_color=(230,196,140,255)
        r.fill_rect(pygame.FRect(760,game.cpu-half,12,game.PADDLE_HEIGHT))
        radius=game.RADIUS
        self.ball_texture.draw(dstrect=pygame.FRect(game.x-radius,game.y-radius,radius*2,radius*2))
        if game.paused:
            r.draw_color=(36,67,94,255)
            r.fill_rect(pygame.FRect(115,165,570,120))
            r.draw_color=(120,152,180,255)
            r.draw_rect(pygame.FRect(115,165,570,120))
            message=game.winner or ("PONG · ¿Listo para jugar?" if game.player_score+game.cpu_score==0 else "Partida en pausa")
            self.label(message,400,207,28,"#f3f6fa",True)
            self.label("Pulsa Espacio o Jugar",400,252,16,"#b8d2e5")
        elif game.serve_delay>0:
            self.label("¡Preparado!",400,290,16,"#b8d2e5")
        # Presentar el backbuffer completo impide mostrar un dibujo a medias.
        r.present()
