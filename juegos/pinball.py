"""AppXP de Pinball: tres bolas, lanzador, palas y misión de objetivos."""
import math
import time
import tkinter as tk
from tkinter import ttk
from .pinball_model import PinballGame
from .pinball_renderer import PinballViewport,pygame


class PinballApp(ttk.Frame):
    def __init__(self,master):
        super().__init__(master,padding=10)
        self.pack(fill="both",expand=True)
        self.game=PinballGame()
        self.keys=set()
        self.job=None
        self.ui_state=None
        self.last=self.next_frame=time.perf_counter()
        self.header=tk.Frame(self,bg="#17375d",height=80)
        self.header.pack(fill="x",pady=(0,8));self.header.pack_propagate(False)
        icon=tk.Canvas(self.header,width=46,height=46,bg="#17375d",highlightthickness=0)
        icon.place(x=15,y=17)
        icon.create_oval(3,7,42,39,outline="#7c9bc1",width=2)
        icon.create_polygon(24,2,13,31,24,27,35,31,fill="#c5bbdf",outline="")
        icon.create_oval(26,31,36,41,fill="#efdab0",outline="")
        tk.Label(self.header,text="Pinball",bg="#17375d",fg="white",font=("Tahoma",21,"bold")).place(x=74,y=10)
        self.subtitle=tk.Label(self.header,text="Órbita espacial · Tres bolas, una misión",bg="#17375d",fg="#b5d4ed",font=("Tahoma",10))
        self.subtitle.place(x=74,y=49)
        controls=tk.Frame(self,bg="#dde8f6",padx=8,pady=7)
        controls.pack(fill="x",pady=(0,8))
        self.pause_button=ttk.Button(controls,text="Pausar",style="Accent.TButton",command=self.toggle,width=9)
        self.pause_button.pack(side="left")
        self.launch_button=ttk.Button(controls,text="Lanzar",style="Teal.TButton",command=self.launch,width=8)
        self.launch_button.pack(side="left",padx=6)
        ttk.Button(controls,text="Nueva partida",style="Blue.TButton",command=self.reset).pack(side="left")
        self.canvas=PinballViewport(self)
        self.canvas.pack(fill="both",expand=True)
        ttk.Label(self,text="← / → o A / D: palas · Espacio: cargar y soltar · P: pausa",style="Footer.TLabel",anchor="center",wraplength=430).pack(fill="x",pady=(8,0))
        self.canvas.bind("<Configure>",lambda e:self.draw(),add="+")
        self.canvas.bind("<Map>",lambda e:self.draw(),add="+")
        self.canvas.bind("<Button-1>",lambda e:self.canvas.focus_game())
        self.canvas.bind("<KeyPress>",lambda e:self.key_down(e.keysym.lower()))
        self.canvas.bind("<KeyRelease>",lambda e:self.key_up(e.keysym.lower()))
        self.bind("<Configure>",self.fit_header)
        self.bind("<Destroy>",self.cleanup)
        self.start_job=self.after_idle(self.start_renderer)

    def fit_header(self,event):
        if event.widget is self:
            compact=event.height<420
            self.header.configure(height=60 if compact else 80)
            if compact:self.subtitle.place_forget()
            else:self.subtitle.place(x=74,y=49)

    def start_renderer(self):
        self.start_job=None
        self.canvas.start()
        self.canvas.focus_game()
        self.last=self.next_frame=time.perf_counter()
        self.tick()

    def key_down(self,key):
        if key in self.keys:
            return "break"
        self.keys.add(key)
        if key=="space":self.game.start_charge()
        elif key=="p":
            self.toggle()
            self.keys.add(key)
        return "break"

    def key_up(self,key):
        self.keys.discard(key)
        if key=="space" and self.game.charging:self.game.launch()
        return "break"

    def toggle(self):
        self.game.paused=not self.game.paused
        self.game.charging=False
        self.game.charge=0
        self.keys.clear()
        self.canvas.focus_game()
        self.last=time.perf_counter()
        self.draw()

    def launch(self):
        self.canvas.focus_game()
        self.game.launch()
        self.draw()

    def reset(self):
        self.game.reset();self.keys.clear()
        self.canvas.focus_game()
        self.last=time.perf_counter()
        self.draw()

    def on_minimize(self):
        self.game.paused=True
        self.game.charging=False
        self.game.charge=0
        self.keys.clear()
        self.draw()

    def on_hide(self):
        self.on_minimize()
        self.canvas.suspend()

    def on_restore(self):
        self.canvas.resume()
        self.canvas.focus_game()
        self.last=time.perf_counter()
        self.draw()

    def poll_events(self):
        for event in self.canvas.poll_events():
            if event.type==pygame.KEYDOWN and not getattr(event,"repeat",False):
                self.key_down(pygame.key.name(event.key))
            elif event.type==pygame.KEYUP:
                self.key_up(pygame.key.name(event.key))
            elif event.type==pygame.WINDOWFOCUSLOST:
                # Un aviso SDL de foco no debe cambiar la pausa de una appXP.
                self.keys.clear()
                self.game.charging=False
                self.game.charge=0
            elif event.type==pygame.MOUSEBUTTONDOWN:
                self.canvas.focus_game()

    def tick(self):
        self.job=None
        self.poll_events()
        now=time.perf_counter()
        self.game.step(now-self.last,bool(self.keys & {"left","a"}),bool(self.keys & {"right","d"}))
        self.last=now
        state=(self.game.paused,self.game.state,self.game.score,self.game.balls_left)
        if self.canvas.winfo_ismapped():self.draw()
        if self.canvas.vsync and self.canvas.winfo_ismapped() and not self.game.paused:
            delay=1;self.next_frame=time.perf_counter()
        else:
            self.next_frame+=1/60
            finished=time.perf_counter()
            if self.next_frame<=finished:self.next_frame=finished+1/60
            delay=max(1,math.ceil((self.next_frame-finished)*1000))
        self.job=self.after(delay,self.tick)

    def draw(self):
        if not self.canvas.renderer or self.canvas.suspended or not self.canvas.winfo_ismapped():return
        self.canvas.draw(self.game)
        state=(self.game.paused,self.game.state,self.game.score,self.game.balls_left)
        if state!=self.ui_state:
            self.ui_state=state
            self.pause_button.configure(text="Continuar" if self.game.paused else "Pausar")
            self.launch_button.configure(state="normal" if self.game.state=="ready" and not self.game.paused else "disabled")

    def cleanup(self,event):
        if event.widget is self:
            for job in (self.job,self.start_job):
                if job:self.after_cancel(job)
            self.job=self.start_job=None
            self.canvas.close()
