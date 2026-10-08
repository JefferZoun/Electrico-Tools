"""Vuelo entre postes eléctricos, con física independiente del renderizado."""
from dataclasses import dataclass
import random


@dataclass
class ElectricPost:
    x:float
    gap_y:float
    scored:bool=False
    gap_size:float=155


class FlappyGame:
    WIDTH=800
    HEIGHT=500
    FLOOR=458
    BIRD_X=195
    RADIUS=14
    POST_WIDTH=84
    GAP=155
    SPACING=260
    SPEED=215
    GRAVITY=850
    FLAP_SPEED=-305

    def __init__(self,rng=None):
        self.rng=rng or random.Random()
        self.best=0
        self.reset()

    def reset(self):
        self.y=240.0
        self.vy=0.0
        self.scroll=0.0
        self.distance=0.0
        self.speed=float(self.SPEED)
        self.previous_post=None
        self.score=0
        self.paused=False
        self.state="ready"
        self.posts=[]
        for i in range(3):
            self.posts.append(self.make_post(690+i*self.SPACING))

    @property
    def level(self):
        return 1+min(10,self.score//5)

    @property
    def target_speed(self):
        return self.SPEED+9*(self.level-1)

    @property
    def gap_size(self):
        return self.GAP-4*(self.level-1)

    @property
    def spacing(self):
        return self.SPACING-3*(self.level-1)

    def new_gap(self):
        # Limitar el salto de altura mantiene alcanzable el siguiente hueco.
        previous=self.posts[-1].gap_y if self.posts else 240
        return self.rng.uniform(max(135,previous-100),min(323,previous+100))

    def make_post(self,x):
        return ElectricPost(x,self.new_gap(),gap_size=self.gap_size)

    def flap(self):
        if self.paused:
            return
        if self.state=="over":
            self.reset()
        self.state="playing"
        self.vy=self.FLAP_SPEED

    def post_rectangles(self,post):
        """La hitbox sigue el mástil, las crucetas y los aisladores visibles."""
        x=post.x;top=post.gap_y-post.gap_size/2;bottom=post.gap_y+post.gap_size/2
        rects=[(x+32,0,20,top),(x,top-26,self.POST_WIDTH,12),
               (x+32,bottom,20,self.FLOOR-bottom),(x,bottom+14,self.POST_WIDTH,12)]
        for offset in (8,37,66):
            rects.extend(((x+offset,top-14,10,14),(x+offset,bottom,10,14)))
        return rects

    def intersects(self,rect):
        x,y,w,h=rect
        nearest_x=max(x,min(self.BIRD_X,x+w))
        nearest_y=max(y,min(self.y,y+h))
        return (self.BIRD_X-nearest_x)**2+(self.y-nearest_y)**2<=self.RADIUS**2

    def step(self,dt):
        if self.paused or self.state!="playing":
            return
        remaining=min(max(dt,0),.08)
        while remaining>1e-9:
            tick=min(remaining,1/240);remaining-=tick
            self.vy=min(520,self.vy+self.GRAVITY*tick)
            self.y+=self.vy*tick
            self.speed=min(self.target_speed,self.speed+18*tick)
            travel=self.speed*tick
            self.distance+=travel
            self.scroll=(self.scroll+travel)%self.SPACING
            for post in self.posts:post.x-=travel
            if self.previous_post is not None:self.previous_post.x-=travel
            while len(self.posts)>1 and self.posts[0].x+self.POST_WIDTH<0:
                self.previous_post=self.posts.pop(0)
            # Preparar los siguientes postes fuera de pantalla antes de que
            # el último visible deje un tramo vacío a la derecha.
            while self.posts[-1].x<self.WIDTH+self.SPACING:
                self.posts.append(self.make_post(self.posts[-1].x+self.spacing))
            if self.y-self.RADIUS<=0 or self.y+self.RADIUS>=self.FLOOR:
                self.state="over";return
            for post in self.posts:
                if any(self.intersects(rect) for rect in self.post_rectangles(post)):
                    self.state="over";return
                if not post.scored and post.x+self.POST_WIDTH<self.BIRD_X-self.RADIUS:
                    post.scored=True
                    self.score+=1;self.best=max(self.best,self.score)
