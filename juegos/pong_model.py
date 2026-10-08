"""Pong independiente de Tk: coordenadas lógicas de 800 × 450."""
import math
import random


class PongGame:
    WIDTH=800
    HEIGHT=450
    PADDLE_HEIGHT=88
    RADIUS=10
    SERVE_SPEED=360
    MAX_SPEED=720
    TARGET=7

    def __init__(self,rng=None):
        self.rng=rng or random.Random()
        self.difficulty="Normal"
        self.reset()

    def reset(self):
        self.player=self.cpu=self.HEIGHT/2
        self.player_score=self.cpu_score=0
        self.paused=True
        self.winner=None
        self.serve(self.rng.choice((-1,1)))

    def serve(self,direction):
        self.x,self.y=self.WIDTH/2,self.HEIGHT/2
        angle=self.rng.uniform(-0.45,0.45)
        self.vx=direction*self.SERVE_SPEED*math.cos(angle)
        self.vy=self.SERVE_SPEED*math.sin(angle)
        self.serve_delay=0.65

    def toggle_pause(self):
        if self.winner:
            self.reset()
        self.paused=not self.paused

    def step(self,dt,move=0):
        if self.paused or self.winner:
            return
        # Subpasos mantienen fiables los impactos incluso con un fotograma lento.
        remaining=min(max(dt,0),0.1)
        while remaining>1e-9:
            tick=min(remaining,1/240)
            remaining-=tick
            self._step(tick,max(-1,min(1,move)))
            if self.winner:
                break

    def _step(self,dt,move):
        half=self.PADDLE_HEIGHT/2
        self.player=max(half,min(self.HEIGHT-half,self.player+move*540*dt))
        cpu_speed={"Fácil":180,"Normal":270,"Difícil":360}[self.difficulty]
        target=self.y if self.vx>0 else self.HEIGHT/2
        distance=target-self.cpu
        if abs(distance)>12:
            self.cpu+=max(-cpu_speed*dt,min(cpu_speed*dt,distance))
        self.cpu=max(half,min(self.HEIGHT-half,self.cpu))
        if self.serve_delay>0:
            self.serve_delay=max(0,self.serve_delay-dt)
            return
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        if self.y<self.RADIUS:
            self.y=2*self.RADIUS-self.y
            self.vy=abs(self.vy)
        elif self.y>self.HEIGHT-self.RADIUS:
            self.y=2*(self.HEIGHT-self.RADIUS)-self.y
            self.vy=-abs(self.vy)
        # Caras interiores: izquierda x=40, derecha x=760.
        if self.vx<0 and self.x-self.RADIUS<=40 and self.x>=22 and abs(self.y-self.player)<=half+self.RADIUS:
            self.x=40+self.RADIUS
            self.bounce(self.player,1)
        elif self.vx>0 and self.x+self.RADIUS>=760 and self.x<=778 and abs(self.y-self.cpu)<=half+self.RADIUS:
            self.x=760-self.RADIUS
            self.bounce(self.cpu,-1)
        if self.x < -self.RADIUS:
            self.cpu_score+=1
            self.point(-1)
        elif self.x > self.WIDTH+self.RADIUS:
            self.player_score+=1
            self.point(1)

    def bounce(self,paddle,direction):
        offset=max(-1,min(1,(self.y-paddle)/(self.PADDLE_HEIGHT/2)))
        angle=offset*math.pi/3
        speed=min(self.MAX_SPEED,math.hypot(self.vx,self.vy)*1.05)
        self.vx=direction*speed*math.cos(angle)
        self.vy=speed*math.sin(angle)

    def point(self,direction):
        if self.player_score>=self.TARGET or self.cpu_score>=self.TARGET:
            self.winner="¡Has ganado!" if self.player_score>=self.TARGET else "Gana la CPU"
            self.paused=True
        else:
            self.serve(direction)
