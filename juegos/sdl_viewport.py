"""Campo SDL acelerado, integrado como hijo nativo de la appXP de Windows."""
import ctypes
import os
import tkinter as tk
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT","1")
os.environ.setdefault("SDL_RENDER_SCALE_QUALITY","linear")
import pygame
from pygame._sdl2 import Renderer, Texture


class SDLViewport(tk.Frame):
    instances={}
    logical_size=(800,450)
    title="Juego"
    def __init__(self,master):
        super().__init__(master,bg="#172c45",takefocus=True)
        self.window=None
        self.renderer=None
        self.textures={}
        self.fonts={}
        self.timer_enabled=False
        self.vsync=False
        self.events=[]
        self.suspended=False
        self.bind("<Configure>",self.resize)
        self.bind("<Map>",lambda e:self.resume())
        self.bind("<Unmap>",lambda e:self.suspend())

    def start(self):
        if self.window:
            return
        if os.name!="nt":
            raise RuntimeError("La integración de los juegos en el escritorio requiere Windows.")
        self.update_idletasks()
        pygame.display.init()
        pygame.font.init()
        # SDL crea su propio hijo: el renderer no comparte una superficie GDI con Tk.
        self.window=pygame.Window(self.title,size=(max(1,self.winfo_width()),max(1,self.winfo_height())),hidden=True,borderless=True)
        self.user32=ctypes.WinDLL("user32",use_last_error=True)
        self.user32.SetParent.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        self.user32.SetParent.restype=ctypes.c_void_p
        self.user32.SetWindowLongW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_long]
        self.user32.SetWindowLongW.restype=ctypes.c_long
        self.user32.SetWindowPos.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_uint]
        self.user32.SetFocus.argtypes=[ctypes.c_void_p]
        self.user32.SetFocus.restype=ctypes.c_void_p
        self.user32.GetFocus.restype=ctypes.c_void_p
        self.user32.GetForegroundWindow.restype=ctypes.c_void_p
        self.user32.GetAncestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        self.user32.GetAncestor.restype=ctypes.c_void_p
        hwnd=self.window.handle
        self.user32.SetParent(hwnd,self.winfo_id())
        self.user32.SetWindowLongW(hwnd,-16,0x40000000|0x10000000|0x04000000)
        try:
            self.renderer=Renderer(self.window,accelerated=1,vsync=True)
            self.vsync=True
        except pygame.error:
            self.renderer=Renderer(self.window,accelerated=-1,vsync=False)
        self.renderer.logical_size=self.logical_size
        self.renderer.draw_blend_mode=pygame.BLENDMODE_BLEND
        SDLViewport.instances[self.window.id]=self
        self.window.show()
        self.resize()
        # Cada ventana equilibra su llamada a timeBeginPeriod/timeEndPeriod.
        self.winmm=ctypes.WinDLL("winmm")
        self.timer_enabled=self.winmm.timeBeginPeriod(1)==0
        ball=pygame.Surface((80,80),pygame.SRCALPHA)
        pygame.draw.circle(ball,"#f1efdc",(40,40),39)
        ball=pygame.transform.smoothscale(ball,(40,40))
        self.ball_texture=Texture.from_surface(self.renderer,ball)
        self.build_assets()

    def resize(self,event=None):
        if self.window:
            width,height=max(1,self.winfo_width()),max(1,self.winfo_height())
            self.window.size=(width,height)
            self.user32.SetWindowPos(self.window.handle,None,0,0,width,height,0x0014 if self.suspended else 0x0054)
            if self.renderer:
                pygame.event.pump()
                self.renderer.logical_size=(0,0)
                self.renderer.logical_size=self.logical_size

    def suspend(self):
        self.suspended=True
        if self.window:
            self.window.hide()

    def resume(self):
        self.suspended=False
        if self.window:
            self.user32.SetParent(self.window.handle,self.winfo_id())
            self.window.show()
            self.resize()

    def focus_game(self):
        # Tk conserva una ruta de teclado alternativa si el host rechaza el foco SDL.
        self.focus_set()
        if self.window:
            self.user32.SetFocus(self.window.handle)

    def has_focus(self):
        if not self.window:
            return False
        foreground=self.user32.GetForegroundWindow()
        top=self.user32.GetAncestor(self.window.handle,2)
        focused=self.user32.GetFocus()==self.window.handle or self.focus_get() is self
        return focused and (not foreground or foreground==top)

    def label(self,text,x,y,size,color,bold=False):
        key=(text,size,color,bold)
        if key not in self.textures:
            font_key=(size,bold)
            if font_key not in self.fonts:
                self.fonts[font_key]=pygame.font.SysFont("Tahoma",size,bold=bold)
            surface=self.fonts[font_key].render(text,True,color)
            if len(self.textures)>=96:
                self.textures.pop(next(iter(self.textures)))
            self.textures[key]=Texture.from_surface(self.renderer,surface)
        texture=self.textures[key]
        texture.draw(dstrect=pygame.FRect(x-texture.width/2,y-texture.height/2,texture.width,texture.height))

    def build_assets(self):
        pass

    def poll_events(self):
        # Un único drenado de SDL distribuye cada evento a su ventana propietaria.
        for event in pygame.event.get():
            window=getattr(event,"window",None)
            target=SDLViewport.instances.get(getattr(window,"id",window))
            if target is None and window is None:
                target=next((v for v in SDLViewport.instances.values() if v.has_focus()),None)
                if target is None and len(SDLViewport.instances)==1:
                    target=next(iter(SDLViewport.instances.values()))
            if target:
                target.events.append(event)
        events,self.events=self.events,[]
        return events

    def close(self):
        self.textures.clear()
        self.fonts.clear()
        self.ball_texture=None
        self.renderer=None
        if self.window:
            SDLViewport.instances.pop(self.window.id,None)
            self.window.destroy()
            self.window=None
        self.events.clear()
        if not SDLViewport.instances:
            pygame.display.quit()
        if self.timer_enabled:
            self.winmm.timeEndPeriod(1)
            self.timer_enabled=False
