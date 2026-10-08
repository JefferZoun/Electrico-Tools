"""Pinball de órbita espacial: gravedad y contactos en pasos de 1/240 s."""
import math

RAILS=(
    ((30,155),(55,85)),((55,85),(110,45)),((110,45),(365,45)),
    ((365,45),(420,72)),((420,72),(465,140)),
    ((30,155),(30,580)),((465,140),(465,720)),
    ((418,180),(418,675)),
    ((30,580),(145,645)),((400,580),(335,645)),
    ((65,515),(115,495)),((115,495),(150,565)),((150,565),(65,515)),
    ((365,495),(400,515)),((400,515),(330,565)),((330,565),(365,495)),
)
BUMPERS=((155,225,27),(305,225,27),(230,335,30))
TARGETS=((82,175,12),(380,175,12),(85,380,12),(375,380,12))


class PinballGame:
    WIDTH=480
    HEIGHT=720
    RADIUS=9
    FLIPPER_LENGTH=83
    GRAVITY=760

    def __init__(self):
        self.best=0
        self.reset()

    def reset(self):
        self.score=0
        self.balls_left=3
        self.multiplier=1
        self.targets=[False]*4
        self.hits=[0.0]*3
        self.target_cooldowns=[0.0]*4
        self.left_angle=.48
        self.right_angle=math.pi-.48
        self.paused=False
        self.elapsed=0.0
        self.charging=False
        self.charge=0.0
        self.prepare_ball()

    def prepare_ball(self):
        self.x,self.y=443.0,665.0
        self.vx=self.vy=0.0
        self.state="ready" if self.balls_left else "over"
        self.charging=False
        self.charge=0.0

    def start_charge(self):
        if self.state=="ready" and not self.paused:
            self.charging=True

    def launch(self):
        if self.state!="ready" or self.paused:
            return
        self.vx=-18.0
        self.vy=-(1060+220*self.charge)
        self.charging=False
        self.charge=0.0
        self.state="playing"

    def add_score(self,points):
        self.score+=points*self.multiplier
        self.best=max(self.best,self.score)

    def flipper(self,left):
        pivot=(145,630) if left else (335,630)
        angle=self.left_angle if left else self.right_angle
        return pivot,(pivot[0]+math.cos(angle)*self.FLIPPER_LENGTH,pivot[1]+math.sin(angle)*self.FLIPPER_LENGTH)

    @staticmethod
    def approach(value,target,amount):
        return value+max(-amount,min(amount,target-value))

    def step(self,dt,left=False,right=False):
        if self.paused or self.state=="over":
            return
        remaining=min(max(0,dt),.08)
        while remaining>1e-9:
            tick=min(remaining,1/240)
            remaining-=tick
            self._step(tick,left,right)
            if self.state=="over":
                break

    def _step(self,dt,left,right):
        old_left,old_right=self.left_angle,self.right_angle
        self.left_angle=self.approach(old_left,-.46 if left else .48,9*dt)
        self.right_angle=self.approach(old_right,math.pi+.46 if right else math.pi-.48,9*dt)
        if self.state=="ready":
            if self.charging:
                self.charge=min(1,self.charge+dt/.8)
            return
        self.elapsed+=dt
        self.hits=[max(0,t-dt) for t in self.hits]
        self.target_cooldowns=[max(0,t-dt) for t in self.target_cooldowns]
        self.vy+=self.GRAVITY*dt
        self.vx*=math.exp(-.075*dt)
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        for a,b in RAILS:
            self.segment(a,b,3,.82)
        for i,(x,y,radius) in enumerate(BUMPERS):
            if self.circle(x,y,radius,boost=470):
                if not self.hits[i]:
                    self.add_score(100)
                self.hits[i]=.16
        for i,(x,y,radius) in enumerate(TARGETS):
            if self.circle(x,y,radius,boost=240):
                if not self.target_cooldowns[i]:
                    self.add_score(50)
                    self.targets[i]=True
                    if all(self.targets):
                        self.add_score(500)
                        self.multiplier=min(5,self.multiplier+1)
                        self.targets=[False]*4
                self.target_cooldowns[i]=.2
        for left_paddle,old_angle in ((True,old_left),(False,old_right)):
            a,b=self.flipper(left_paddle)
            angle=self.left_angle if left_paddle else self.right_angle
            self.segment(a,b,10,.86,angular=(angle-old_angle)/dt)
        speed=math.hypot(self.vx,self.vy)
        if speed>1300:
            self.vx*=1300/speed;self.vy*=1300/speed
        if self.y>self.HEIGHT+25:
            self.balls_left-=1
            self.prepare_ball()

    def circle(self,x,y,radius,boost=0):
        dx,dy=self.x-x,self.y-y
        distance=math.hypot(dx,dy)
        reach=radius+self.RADIUS
        if distance>=reach:
            return False
        nx,ny=(dx/distance,dy/distance) if distance>1e-8 else (0,-1)
        self.x=x+nx*(reach+.1);self.y=y+ny*(reach+.1)
        impact=self.vx*nx+self.vy*ny
        if impact<0:
            self.vx-=1.85*impact*nx;self.vy-=1.85*impact*ny
        outward=self.vx*nx+self.vy*ny
        if outward<boost:
            self.vx+=(boost-outward)*nx;self.vy+=(boost-outward)*ny
        return True

    def segment(self,a,b,thickness,restitution,angular=0):
        ax,ay=a;bx,by=b
        dx,dy=bx-ax,by-ay
        length2=dx*dx+dy*dy
        t=max(0,min(1,((self.x-ax)*dx+(self.y-ay)*dy)/length2))
        cx,cy=ax+t*dx,ay+t*dy
        nx,ny=self.x-cx,self.y-cy
        distance=math.hypot(nx,ny)
        reach=self.RADIUS+thickness
        if distance>=reach:
            return False
        if distance>1e-8:
            nx/=distance;ny/=distance
        else:
            length=math.sqrt(length2);nx,ny=-dy/length,dx/length
            if self.vx*nx+self.vy*ny>0:nx,ny=-nx,-ny
        self.x=cx+nx*(reach+.1);self.y=cy+ny*(reach+.1)
        surface_vx=-angular*(cy-ay)
        surface_vy=angular*(cx-ax)
        impact=(self.vx-surface_vx)*nx+(self.vy-surface_vy)*ny
        if impact<0:
            self.vx-=(1+restitution)*impact*nx
            self.vy-=(1+restitution)*impact*ny
        return True
