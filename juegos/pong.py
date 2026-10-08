"""AppXP Pong: controles Tk y campo de juego renderizado por SDL."""
import math
import time
import tkinter as tk
from tkinter import ttk
from .pong_model import PongGame
from .pong_renderer import PongViewport, pygame


class PongApp(ttk.Frame):
    FRAME_SECONDS=1/60

    def __init__(self,master):
        super().__init__(master,padding=10)
        self.pack(fill="both",expand=True)
        self.game=PongGame()
        self.keys=set()
        self.job=None
        self.last=time.perf_counter()
        self.next_frame=self.last
        self.ui_state=None
        self.header=tk.Frame(self,bg="#17375d",height=88)
        self.header.pack(fill="x",pady=(0,8))
        self.header.pack_propagate(False)
        icon=tk.Canvas(self.header,width=48,height=48,bg="#17375d",highlightthickness=0)
        icon.place(x=16,y=18)
        icon.create_rectangle(1,5,47,43,fill="#234b75",outline="#6e9fc8")
        icon.create_line(10,14,10,34,fill="#9cd8e9",width=4)
        icon.create_line(38,12,38,32,fill="#e6c48c",width=4)
        icon.create_line(24,10,24,38,fill="#6e8aa8",dash=(3,4))
        icon.create_oval(27,22,35,30,fill="#f1efdc",outline="")
        tk.Label(self.header,text="Pong",bg="#17375d",fg="white",font=("Tahoma",21,"bold"),anchor="w").place(x=78,y=13)
        self.subtitle=tk.Label(self.header,text="Un clásico de arcade · Primero a 7 puntos",bg="#17375d",fg="#b5d4ed",font=("Tahoma",10),anchor="w")
        self.subtitle.place(x=78,y=53)
        controls=tk.Frame(self,bg="#dde8f6",padx=8,pady=7)
        controls.pack(fill="x",pady=(0,8))
        self.play_button=ttk.Button(controls,text="Jugar",style="Accent.TButton",command=self.toggle,width=8)
        self.play_button.pack(side="left")
        ttk.Button(controls,text="Nueva partida",style="Blue.TButton",command=self.reset).pack(side="left",padx=(6,0))
        self.difficulty=tk.StringVar(value="Normal")
        combo=ttk.Combobox(controls,textvariable=self.difficulty,values=("Fácil","Normal","Difícil"),state="readonly",width=8)
        combo.pack(side="right")
        tk.Label(controls,text="Rival",bg="#dde8f6",fg="#49617e",font=("Tahoma",9)).pack(side="right",padx=(8,6))
        combo.bind("<<ComboboxSelected>>",self.change_difficulty)
        self.canvas=PongViewport(self)
        self.canvas.pack(fill="both",expand=True)
        ttk.Label(self,text="W / S o ↑ / ↓: mover · Espacio: jugar / pausar",style="Footer.TLabel",anchor="center",wraplength=430).pack(fill="x",pady=(8,0))
        self.canvas.bind("<Configure>",lambda e:self.draw(),add="+")
        self.canvas.bind("<Map>",lambda e:self.draw(),add="+")
        self.canvas.bind("<Button-1>",lambda e:self.canvas.focus_game())
        self.canvas.bind("<KeyPress>",self.press)
        self.canvas.bind("<KeyRelease>",self.release)
        self.bind("<Configure>",self.fit_header)
        self.bind("<Destroy>",self.cleanup)
        self.start_job=self.after_idle(self.start_renderer)

    def fit_header(self,event):
        if event.widget is not self:
            return
        compact=event.height<420
        self.header.configure(height=64 if compact else 88)
        if compact:
            self.subtitle.place_forget()
        else:
            self.subtitle.place(x=78,y=53)

    def start_renderer(self):
        self.start_job=None
        self.canvas.start()
        self.last=time.perf_counter()
        self.next_frame=self.last
        self.canvas.focus_game()
        self.tick()

    def press(self,event):
        key=event.keysym.lower()
        if key in ("w","s","up","down"):
            self.keys.add(key)
            return "break"
        if key=="space":
            if key not in self.keys:
                self.toggle()
                self.keys.add(key)
            return "break"

    def release(self,event):
        self.keys.discard(event.keysym.lower())
        return "break"

    def toggle(self):
        self.canvas.focus_game()
        self.game.toggle_pause()
        self.last=time.perf_counter()
        self.draw()

    def reset(self):
        self.game.reset()
        self.keys.clear()
        self.canvas.focus_game()
        self.draw()

    def change_difficulty(self,event=None):
        self.game.difficulty=self.difficulty.get()
        self.canvas.focus_game()

    def on_minimize(self):
        self.game.paused=True
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

    def cleanup(self,event):
        if event.widget is self:
            for job in (self.job,self.start_job):
                if job:
                    self.after_cancel(job)
            self.job=self.start_job=None
            self.canvas.close()

    def poll_events(self):
        for event in self.canvas.poll_events():
            if event.type==pygame.KEYDOWN:
                key=pygame.key.name(event.key)
                if key in ("w","s","up","down"):
                    self.keys.add(key)
                elif event.key==pygame.K_SPACE and not getattr(event,"repeat",False):
                    self.toggle()
            elif event.type==pygame.KEYUP:
                self.keys.discard(pygame.key.name(event.key))
            elif event.type==pygame.WINDOWFOCUSLOST:
                # Un aviso SDL de foco no debe cambiar la pausa de una appXP.
                self.keys.clear()
            elif event.type==pygame.MOUSEBUTTONDOWN:
                self.canvas.focus_game()

    def tick(self):
        self.job=None
        self.poll_events()
        now=time.perf_counter()
        move=int(bool(self.keys & {"s","down"}))-int(bool(self.keys & {"w","up"}))
        self.game.step(now-self.last,move)
        self.last=now
        if self.canvas.winfo_ismapped():
            self.draw()
        if self.canvas.vsync and self.canvas.winfo_ismapped() and not self.game.paused:
            # present() ya espera al refresco: no introducir una segunda espera.
            delay=1
            self.next_frame=time.perf_counter()
        else:
            self.next_frame+=self.FRAME_SECONDS
            finished=time.perf_counter()
            if self.next_frame<=finished:
                self.next_frame=finished+self.FRAME_SECONDS
            delay=max(1,math.ceil((self.next_frame-finished)*1000))
        self.job=self.after(delay,self.tick)

    def draw(self):
        if not self.canvas.renderer or self.canvas.suspended or not self.canvas.winfo_ismapped():
            return
        self.canvas.draw(self.game)
        state=self.game.paused
        if state!=self.ui_state:
            self.ui_state=state
            self.play_button.configure(text="Jugar" if state else "Pausar")
