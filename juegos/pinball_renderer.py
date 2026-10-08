"""Mesa espacial original, inspirada en el pinball clásico de Windows XP."""
import math
from pygame._sdl2 import Texture
from .sdl_viewport import SDLViewport,pygame
from .pinball_model import RAILS,BUMPERS,TARGETS


class PinballViewport(SDLViewport):
    title="Pinball · Órbita espacial"
    logical_size=(800,800)

    def build_assets(self):
        # Mesa estática al doble de resolución: líneas suaves al reducirla.
        s=pygame.Surface((960,1440));s.fill("#12243d")
        def line(color,a,b,width=1):
            pygame.draw.line(s,color,(int(a[0]*2),int(a[1]*2)),(int(b[0]*2),int(b[1]*2)),width*2)
        def polygon(color,points):
            pygame.draw.polygon(s,color,[(int(x*2),int(y*2)) for x,y in points])
        for x in range(40,460,30):line("#1c314a",(x,55),(x,690))
        for y in range(65,690,30):line("#1c314a",(30,y),(465,y))
        for i in range(36):
            x=55+(i*97)%345;y=80+(i*137)%420
            pygame.draw.circle(s,"#7387ab",(x*2,y*2),2 if i%4 else 3)
        polygon("#213455",[(65,515),(115,495),(150,565)])
        polygon("#213455",[(365,495),(400,515),(330,565)])
        # Nave y órbita central: ilustración propia de formas geométricas.
        pygame.draw.ellipse(s,"#334569",pygame.Rect(250,770,425,130),3)
        polygon("#827db5",[(230,385),(205,435),(215,448),(245,448),(255,435)])
        polygon("#cbc5e6",[(230,385),(224,440),(230,435),(236,440)])
        polygon("#43aec7",[(219,448),(230,480),(241,448)])
        pygame.draw.circle(s,"#b7edf4",(460,838),9)
        for a,b in RAILS:
            line("#375b80",a,b,9)
            line("#8ca8c5",a,b,3)
        font=pygame.font.SysFont("Tahoma",32,bold=True)
        title=font.render("ÓRBITA ESPACIAL",True,"#a8d3ec")
        s.blit(title,(480-title.get_width()/2,190))
        s=pygame.transform.smoothscale(s,(480,720))
        self.table_texture=Texture.from_surface(self.renderer,s)
        self.bumper_textures=[]
        for color in ("#dfb875","#f3d9a4"):
            sprite=pygame.Surface((144,144),pygame.SRCALPHA)
            pygame.draw.circle(sprite,"#34516d",(72,72),70)
            pygame.draw.circle(sprite,color,(72,72),57)
            pygame.draw.circle(sprite,"#805e4c",(72,72),43)
            pygame.draw.circle(sprite,"#f5e0ae",(72,72),31)
            pygame.draw.circle(sprite,"#bf9966",(72,72),15)
            self.bumper_textures.append(Texture.from_surface(self.renderer,pygame.transform.smoothscale(sprite,(72,72))))
        self.target_textures=[]
        for color in ("#5f85aa","#7fe0ce"):
            sprite=pygame.Surface((64,64),pygame.SRCALPHA)
            pygame.draw.circle(sprite,color,(32,32),30)
            pygame.draw.circle(sprite,"#1c334e",(32,32),20)
            pygame.draw.circle(sprite,color,(32,32),9)
            self.target_textures.append(Texture.from_surface(self.renderer,pygame.transform.smoothscale(sprite,(32,32))))
        for color in ("#9bd6e5","#ecd2a2"):
            sprite=pygame.Surface((200,48),pygame.SRCALPHA)
            pygame.draw.rect(sprite,"#355d7b",pygame.Rect(0,0,200,48),border_radius=24)
            pygame.draw.rect(sprite,color,pygame.Rect(4,4,192,40),border_radius=20)
            # Dos variantes por lado quedan listas para la rotación por GPU.
            if not hasattr(self,"flipper_textures"):self.flipper_textures=[]
            self.flipper_textures.append(Texture.from_surface(self.renderer,sprite))

    def draw(self,g):
        r=self.renderer
        r.draw_color=(12,24,42,255);r.clear()
        self.table_texture.draw(dstrect=pygame.FRect(24,48,480,720))
        for i,(x,y,radius) in enumerate(BUMPERS):
            self.bumper_textures[int(g.hits[i]>0)].draw(dstrect=pygame.FRect(x+24-radius-6,y+48-radius-6,(radius+6)*2,(radius+6)*2))
        for i,(x,y,radius) in enumerate(TARGETS):
            self.target_textures[int(g.targets[i])].draw(dstrect=pygame.FRect(x+24-radius,y+48-radius,radius*2,radius*2))
        for i,left in enumerate((True,False)):
            pivot,end=g.flipper(left)
            angle=g.left_angle if left else g.right_angle
            self.flipper_textures[i].draw(dstrect=pygame.FRect(pivot[0]+24-10,pivot[1]+48-10,g.FLIPPER_LENGTH+20,20),angle=math.degrees(angle),origin=(10,10))
        radius=g.RADIUS
        self.ball_texture.draw(dstrect=pygame.FRect(g.x+24-radius,g.y+48-radius,radius*2,radius*2))
        # Muelle/lanzador: la barra crece al mantener Espacio, sin destellos.
        r.draw_color=(84,112,144,255);r.fill_rect(pygame.FRect(461,741,17,18))
        r.draw_color=(218,192,137,255);r.fill_rect(pygame.FRect(461,741-g.charge*55,17,18+g.charge*55))
        r.draw_color=(24,43,65,255);r.fill_rect(pygame.FRect(532,48,244,720))
        self.label("PINBALL",654,86,29,"#eef5fc",True)
        self.label("ÓRBITA ESPACIAL",654,117,14,"#98bdd9")
        self.label("PUNTUACIÓN",654,169,15,"#99b5ce",True)
        self.label(f"{g.score:,}".replace(","," "),654,209,35,"#f0d9a5",True)
        self.label("MEJOR PARTIDA",654,273,14,"#99b5ce")
        self.label(str(g.best),654,306,23,"#d5e6f5",True)
        self.label("BOLAS",654,369,15,"#99b5ce",True)
        self.label(str(g.balls_left),654,402,27,"#d5e6f5",True)
        self.label(f"BONUS ×{g.multiplier}",654,472,20,"#8dd9cb",True)
        self.label("MISIÓN",654,533,14,"#99b5ce",True)
        self.label("Activa los 4 objetivos",654,563,16,"#d5e6f5")
        self.label(f"{sum(g.targets)} / 4",654,593,22,"#8dd9cb",True)
        self.label("← / →  o  A / D",654,665,17,"#d5e6f5")
        self.label("Espacio: cargar / lanzar",654,700,16,"#b0c6da")
        self.label("P: pausar",654,731,16,"#b0c6da")
        if g.paused or g.state in ("ready","over"):
            r.draw_color=(29,51,76,245);r.fill_rect(pygame.FRect(61,431,407,108))
            r.draw_color=(93,131,163,255);r.draw_rect(pygame.FRect(61,431,407,108))
            title="Partida en pausa" if g.paused else ("Fin de la partida" if g.state=="over" else "Prepara el lanzamiento")
            hint="Pulsa P o Continuar" if g.paused else ("Pulsa Nueva partida" if g.state=="over" else "Mantén Espacio y suelta")
            self.label(title,264,467,22,"#eef5fc",True)
            self.label(hint,264,503,17,"#b6d7ed")
        r.present()

    def close(self):
        self.table_texture=None
        self.bumper_textures=[]
        self.target_textures=[]
        self.flipper_textures=[]
        super().close()
