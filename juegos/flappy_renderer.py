"""Paisaje eléctrico en parallax y postes cableados de Flappy Volt."""
import math

from pygame._sdl2 import Texture
from .sdl_viewport import SDLViewport, pygame


class FlappyViewport(SDLViewport):
    title = "Flappy Volt"
    logical_size = (800, 500)

    def build_assets(self):
        sky = pygame.Surface((1600, 1000))
        sky.fill("#b7dce8")
        for y in range(916):
            t = y / 916
            pygame.draw.line(sky, (int(155 + 43*t), int(201 + 30*t), int(223 + 11*t)), (0, y), (1600, y))
        for x, y in ((100, 150), (470, 100), (1080, 180), (1370, 100)):
            for dx, dy, radius in ((0, 0, 36), (45, -20, 45), (88, 0, 34)):
                pygame.draw.circle(sky, "#e4f1ef", (x+dx, y+dy), radius)
            pygame.draw.rect(sky, "#e4f1ef", (x, y, 88, 34))
        pygame.draw.polygon(sky, "#95b9a8", [(0,850),(0,750),(200,700),(450,770),(710,650),(1000,760),(1300,675),(1600,740),(1600,850)])
        pygame.draw.polygon(sky, "#729c93", [(0,916),(0,850),(300,790),(580,865),(920,785),(1240,850),(1600,775),(1600,916)])
        for x in (100, 700, 1300):
            pygame.draw.line(sky, "#7a9b9d", (x,550), (x,855), 10)
            pygame.draw.line(sky, "#7a9b9d", (x-50,580), (x+50,580), 8)
        pygame.draw.lines(sky, "#7a9b9d", False, [(50,580),(400,630),(750,580),(1000,630),(1350,580),(1600,620)], 3)
        self.sky_texture = Texture.from_surface(self.renderer, pygame.transform.smoothscale(sky,(800,500)))
        self.plant_ground_texture = Texture.from_surface(self.renderer, self._plant_ground())
        self.plant_texture = Texture.from_surface(self.renderer, self._power_plant())
        self.houses_texture = Texture.from_surface(self.renderer, self._houses())

        bird = pygame.Surface((104, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(bird, "#9e7340", (12,10,76,58))
        pygame.draw.ellipse(bird, "#f4d278", (14,8,72,55))
        pygame.draw.ellipse(bird, "#ffe4a4", (28,11,44,25))
        pygame.draw.ellipse(bird, "#c89648", (8,33,43,26))
        pygame.draw.ellipse(bird, "#f3bc63", (12,31,35,21))
        pygame.draw.polygon(bird, "#ed9859", [(78,30),(102,39),(78,46)])
        pygame.draw.circle(bird, "#f8fbf5", (73,24), 13)
        pygame.draw.circle(bird, "#263948", (78,24), 6)
        pygame.draw.polygon(bird, "#855b32", [(49,37),(36,57),(52,48),(47,65),(68,43)])
        self.bird_texture = Texture.from_surface(self.renderer, pygame.transform.smoothscale(bird,(52,40)))

    @staticmethod
    def _plant_ground():
        """Bancal y camino que viajan con la central en la capa intermedia."""
        s = pygame.Surface((410,108), pygame.SRCALPHA)
        # Los lados bajan hasta el pie de la ladera; la nave apoya en la meseta.
        pygame.draw.polygon(s,"#80a99d",[(0,108),(30,83),(65,56),(84,39),
                                           (326,39),(357,58),(383,86),(410,108)])
        pygame.draw.polygon(s,"#91b7a6",[(65,56),(84,39),(326,39),(357,58),
                                           (340,65),(72,65)])
        pygame.draw.line(s,"#a7c7b4",(83,39),(327,39),3)
        pygame.draw.polygon(s,"#6f998f",[(0,108),(31,83),(64,66),(79,67),
                                           (58,87),(39,108)])
        pygame.draw.polygon(s,"#6f998f",[(337,66),(357,58),(384,86),
                                           (410,108),(374,108),(352,83)])
        # El sendero sale de la entrada y se ensancha en primer plano.
        road=[(176,40),(207,40),(219,59),(233,79),(265,108),
              (116,108),(149,79),(159,60)]
        pygame.draw.polygon(s,"#c8bba0",road)
        pygame.draw.line(s,"#e0d0af",(177,41),(205,41),2)
        pygame.draw.lines(s,"#a99f89",False,[(159,61),(149,79),(116,107)],2)
        pygame.draw.lines(s,"#a99f89",False,[(219,59),(233,79),(265,107)],2)
        for x,y in ((174,57),(210,66),(165,88),(187,97),(224,90),(241,104)):
            pygame.draw.line(s,"#a99e86",(x,y),(x+5,y+1),1)
        for x,y in ((53,82),(68,74),(331,74),(349,87)):
            pygame.draw.line(s,"#b8d1b3",(x,y),(x+5,y-2),2)
        return s

    @staticmethod
    def _power_plant():
        """Central lejana: torres, chimenea, subestación y transformadores."""
        s = pygame.Surface((310,145), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (111,151,153,145), (15,120,290,18))
        pygame.draw.rect(s, "#8aa9a7", (50,66,185,60))
        pygame.draw.rect(s, "#bdd2c8", (59,76,168,10))
        pygame.draw.rect(s, "#647f85", (50,120,185,6))
        for x in (72,119,166,208):
            pygame.draw.rect(s, "#617f88", (x,91,18,25))
            pygame.draw.rect(s, "#d1d9c0", (x+4,91,10,25))
        for x in (25,253):
            pygame.draw.polygon(s,"#8ba7a6",[(x,116),(x+7,55),(x+44,55),(x+51,116)])
            pygame.draw.ellipse(s,"#6f9095",(x+7,48,37,10))
            pygame.draw.ellipse(s,"#cee2d8",(x+4,108,45,8))
        pygame.draw.rect(s,"#728f92",(224,17,14,86))
        pygame.draw.rect(s,"#d3e4d8",(224,17,14,6))
        # Entrada y barras de la subestación.
        pygame.draw.rect(s,"#547580",(126,101,26,25))
        for x in (244,263,282):
            pygame.draw.line(s,"#698b8b",(x,101),(x,124),3)
            pygame.draw.circle(s,"#c9d8bd",(x,101),4)
        pygame.draw.line(s,"#698b8b",(240,107),(293,107),2)
        font = pygame.font.SysFont("Tahoma",10,bold=True)
        s.blit(font.render("CENTRAL",True,"#e6eee2"),(105,71))
        return s

    @staticmethod
    def _houses():
        """Viviendas y recinto ICT común RITU como detalle del paisaje cercano."""
        s = pygame.Surface((440,139),pygame.SRCALPHA)
        pygame.draw.ellipse(s,(81,135,110,110),(0,127,438,15))
        colors=(("#eed7b7","#967b70"),("#e6d8bd","#8f8580"),("#efdfc4","#917f78"))
        for i,(wall,roof) in enumerate(colors):
            x=14+i*104
            pygame.draw.rect(s,wall,(x,68,88,61))
            pygame.draw.polygon(s,roof,[(x-7,68),(x+42,38),(x+94,68)])
            pygame.draw.line(s,"#f4ecdd",(x-7,69),(x+94,69),2)
            pygame.draw.rect(s,"#889fa0",(x+14,82,19,19))
            pygame.draw.rect(s,"#d6e7df",(x+17,85,13,13))
            pygame.draw.line(s,"#81999c",(x+23,85),(x+23,99),2)
            pygame.draw.rect(s,"#967b6a",(x+56,91,21,38))
            pygame.draw.circle(s,"#eacb89",(x+74,111),2)
            pygame.draw.rect(s,"#ccd8c7",(x+3,110,13,18))
            pygame.draw.circle(s,"#6d9bb0",(x+9,116),3)
            # Paneles fotovoltaicos y antena de televisión.
            pygame.draw.polygon(s,"#4e8293",[(x+30,45),(x+62,45),(x+73,53),(x+40,53)])
            pygame.draw.line(s,"#bfd0cb",(x+49,46),(x+59,52),1)
            pygame.draw.line(s,"#7e9996",(x+75,57),(x+75,29),2)
            pygame.draw.line(s,"#7e9996",(x+67,34),(x+83,34),2)
            pygame.draw.line(s,"#7e9996",(x+71,41),(x+80,41),2)
        # Arqueta y cable ICT enterrado hacia el recinto común.
        pygame.draw.line(s,"#79a0a4",(28,131),(410,131),2)
        pygame.draw.rect(s,"#aec1b7",(354,73,73,56))
        pygame.draw.polygon(s,"#758d8d",[(348,73),(391,48),(433,73)])
        pygame.draw.rect(s,"#63818b",(371,88,38,41))
        pygame.draw.rect(s,"#e3e8d1",(376,93,28,15))
        font=pygame.font.SysFont("Tahoma",13,bold=True)
        s.blit(font.render("RITU",True,"#3c6571"),(376,94))
        pygame.draw.rect(s,"#7a9b98",(336,121,12,8))
        return s

    @staticmethod
    def _scenery_positions(distance,offset,period,factor,width,left_margin=0):
        left=(offset-distance*factor)%period-width
        yield left
        if left+period-left_margin<800:yield left+period

    def _wire(self,first,second,upper):
        """Dos conductores con catenaria suave entre crucetas consecutivas."""
        x1=first.x+42;x2=second.x+42
        if x2<=x1:return
        y1=first.gap_y+(-first.gap_size/2-20 if upper else first.gap_size/2+20)
        y2=second.gap_y+(-second.gap_size/2-20 if upper else second.gap_size/2+20)
        for offset,color in ((-3,(66,89,99,255)),(3,(118,143,147,255))):
            points=[]
            for i in range(25):
                t=i/24
                points.append((x1+(x2-x1)*t,y1+(y2-y1)*t+8*math.sin(math.pi*t)+offset))
            self.renderer.draw_color=color
            for p1,p2 in zip(points,points[1:]):
                self.renderer.draw_line(p1,p2)

    def draw(self,g):
        r=self.renderer
        r.draw_color=(21,44,64,255);r.clear()
        self.sky_texture.draw(dstrect=pygame.FRect(0,0,800,500))
        for x in self._scenery_positions(g.distance,1560,1770,.16,360,50):
            self.plant_ground_texture.draw(dstrect=pygame.FRect(x-50,350,410,108))
            self.plant_texture.draw(dstrect=pygame.FRect(x,261,310,145))
        for x in self._scenery_positions(g.distance,850,1230,.38,440):
            self.houses_texture.draw(dstrect=pygame.FRect(x,318,440,139))
        # El poste anterior conserva el cable al salir por el borde izquierdo.
        posts=([g.previous_post] if g.previous_post is not None else [])+g.posts
        for first,second in zip(posts,posts[1:]):
            self._wire(first,second,True)
            self._wire(first,second,False)
        for post in g.posts:
            rects=g.post_rectangles(post)
            for index,rect in enumerate(rects):
                r.draw_color=(91,111,126,255) if index<4 else (221,236,222,255)
                r.fill_rect(pygame.FRect(*rect))
                if index>=4:
                    x,y,w,h=rect
                    r.draw_color=(99,155,145,255)
                    for offset in (3,7,11):r.fill_rect(pygame.FRect(x-2,y+offset,w+4,2))
            top=post.gap_y-post.gap_size/2;bottom=post.gap_y+post.gap_size/2
            r.draw_color=(138,161,173,255)
            r.fill_rect(pygame.FRect(post.x+35,0,3,top))
            r.fill_rect(pygame.FRect(post.x+35,bottom,3,g.FLOOR-bottom))
            r.draw_color=(224,193,117,255)
            for y in (top-21,bottom+19):r.fill_rect(pygame.FRect(post.x+39,y,6,4))
        r.draw_color=(69,107,92,255);r.fill_rect(pygame.FRect(0,g.FLOOR,800,42))
        r.draw_color=(146,188,130,255);r.fill_rect(pygame.FRect(0,g.FLOOR,800,8))
        r.draw_color=(91,131,104,255)
        for x in range(-40,840,40):r.fill_rect(pygame.FRect(x-g.scroll%40,g.FLOOR+24,21,3))
        angle=max(-25,min(50,g.vy*.075)) if g.state=="playing" else 0
        self.bird_texture.draw(dstrect=pygame.FRect(g.BIRD_X-24,g.y-19,48,38),angle=angle)
        r.draw_color=(26,56,78,235);r.fill_rect(pygame.FRect(15,13,170,48))
        self.label(f"POSTES  {g.score}",100,37,21,"#f6e0a2",True)
        r.draw_color=(26,56,78,235);r.fill_rect(pygame.FRect(590,13,195,48))
        self.label(f"MEJOR  {g.best}",688,37,20,"#d3e8ec",True)
        r.draw_color=(26,56,78,215);r.fill_rect(pygame.FRect(334,17,132,36))
        self.label(f"NIVEL  {g.level}",400,35,16,"#d9eedc",True)
        if g.paused or g.state!="playing":
            r.draw_color=(27,55,77,245);r.fill_rect(pygame.FRect(170,178,460,139))
            r.draw_color=(129,174,190,255);r.draw_rect(pygame.FRect(170,178,460,139))
            title="Vuelo en pausa" if g.paused else ("FLAPPY VOLT" if g.state=="ready" else "¡Fin del vuelo!")
            hint="Pulsa P o Continuar" if g.paused else "Espacio, ↑ o clic para volar"
            self.label(title,400,211,29,"#f3e2b6",True)
            self.label(hint,400,254,19,"#d0e4ee")
            detail=f"Has superado {g.score} postes" if g.state=="over" else "Cruza los huecos entre los postes"
            self.label(detail,400,290,16,"#9ec4d2")
        r.present()

    def close(self):
        self.sky_texture=None
        self.plant_ground_texture=None
        self.plant_texture=None
        self.houses_texture=None
        self.bird_texture=None
        super().close()
