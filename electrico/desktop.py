"""Escritorio de inicio inspirado en Windows XP: acuarela y pixelart."""
from datetime import datetime
from pathlib import Path
from math import sqrt
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from .theme import configure_theme
from .wallpaper import Wallpaper
from .window import XPWindowChrome
from .start_menu import StartMenu
from .icons import IconLayout

ASSETS = Path(__file__).resolve().parent.parent / "assets"
TASKBAR_HEIGHT = 40
GAME_KEYS=("pong","pinball","flappy")


class DesktopApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master, background="#2464c9")
        self.pack(fill="both", expand=True)
        self.windows = {}
        self.apps = {}
        self.chromes = {}
        self.selected_icon = None
        self.icon_layout=IconLayout(ASSETS.parent / ".local" / "desktop.json")
        self.icon_drag=None
        self.icon_status="Arrastra los iconos para organizarlos"
        self.active_tool = None
        self.resize_job = None
        self.clock_job = None
        self.menu = None
        self.background = None
        self.fullscreen = False
        self.windowed_geometry = None
        self.windowed_state = "normal"
        self.fullscreen_text = tk.StringVar(value="Pantalla completa    F11")
        self.canvas = tk.Canvas(self, highlightthickness=0, background="#639ee1", takefocus=True)
        self.canvas.pack(fill="both", expand=True)
        self.wallpaper = Wallpaper(self, ASSETS / "xp-watercolor-pixel.png")
        self.canvas.bind("<Configure>", self.schedule_draw)
        self.canvas.bind("<Tab>", self.cycle_icons)
        self.canvas.bind("<Return>", self.open_selected)
        self.canvas.bind("<space>", self.open_selected)
        self.canvas.bind("<Escape>", self.escape)
        self.winfo_toplevel().bind("<F11>", self.toggle_fullscreen)
        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.shutdown)
        self.canvas.bind("<Button-1>", self.background_click)
        self.canvas.bind("<B1-Motion>",self.drag_icon)
        self.canvas.bind("<ButtonRelease-1>",self.release_icon)
        self.bind("<Destroy>", self.cleanup)
        self.tick_clock()

    def cleanup(self, event):
        if event.widget is self:
            for job in (self.resize_job, self.clock_job):
                if job:
                    self.after_cancel(job)
            self.wallpaper.resized.cache_clear()

    def schedule_draw(self, event=None):
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(100, self.draw)

    def shadow_text(self, x, y, text, font, tags=(), anchor="center"):
        self.canvas.create_text(x+1, y+2, text=text, font=font, fill="#21457c", anchor=anchor, tags=tags)
        self.canvas.create_text(x, y, text=text, font=font, fill="white", anchor=anchor, tags=tags)

    def draw_icon(self, key, x, y, title):
        tag = "icon:"+key
        highlight = self.canvas.create_rectangle(x-14,y-10,x+100,y+106,fill="#aacbff",stipple="gray25",outline="#e2f3ff",width=1,tags=(tag,"selection:"+key))
        self.canvas.itemconfigure(highlight,state="normal" if self.selected_icon==key else "hidden")
        # Siluetas en bloques de cuatro píxeles, con sombras y reflejos.
        c = self.canvas
        if key == "resistencias":
            c.create_rectangle(x+4,y+36,x+80,y+44,fill="#426080",outline="",tags=tag)
            c.create_rectangle(x+20,y+22,x+68,y+58,fill="#8d672c",outline="",tags=tag)
            c.create_rectangle(x+16,y+18,x+64,y+54,fill="#ffd98d",outline="#fff1c7",width=2,tags=tag)
            c.create_rectangle(x+20,y+22,x+60,y+26,fill="#ffeab8",outline="",tags=tag)
            for offset,color in ((28,"#ba4b36"),(36,"#74432d"),(44,"#dda940"),(56,"#c49742")):
                c.create_rectangle(x+offset,y+22,x+offset+4,y+50,fill=color,outline="",tags=tag)
            c.create_rectangle(x+4,y+34,x+16,y+38,fill="#d8e4f4",outline="",tags=tag)
            c.create_rectangle(x+64,y+34,x+80,y+38,fill="#d8e4f4",outline="",tags=tag)
        elif key == "fuentes":
            c.create_rectangle(x+25,y+6,x+65,y+14,fill="#798aaf",outline="",tags=tag)
            c.create_rectangle(x+18,y+12,x+74,y+62,fill="#20516a",outline="",tags=tag)
            c.create_rectangle(x+14,y+8,x+70,y+58,fill="#7dd9c8",outline="#e5fff9",width=2,tags=tag)
            c.create_rectangle(x+18,y+12,x+66,y+20,fill="#b7efdd",outline="",tags=tag)
            c.create_rectangle(x+20,y+24,x+34,y+48,fill="#18667b",outline="",tags=tag)
            c.create_rectangle(x+16,y+29,x+38,y+35,fill="#18667b",outline="",tags=tag)
            c.create_rectangle(x+46,y+29,x+62,y+35,fill="#18667b",outline="",tags=tag)
        elif key == "flappy":
            c.create_rectangle(x+63,y+10,x+69,y+65,fill="#5b6f7e",outline="",tags=tag)
            c.create_rectangle(x+50,y+20,x+80,y+26,fill="#7c929e",outline="",tags=tag)
            for dx in (52,64,76):
                c.create_rectangle(x+dx,y+13,x+dx+4,y+21,fill="#d2e6d7",outline="",tags=tag)
            c.create_oval(x+5,y+28,x+51,y+61,fill="#f4d278",outline="#faf0be",width=2,tags=tag)
            c.create_oval(x+3,y+44,x+27,y+60,fill="#d8a34c",outline="",tags=tag)
            c.create_polygon(x+45,y+40,x+58,y+45,x+45,y+51,fill="#ed9859",outline="",tags=tag)
            c.create_oval(x+35,y+32,x+44,y+41,fill="white",outline="",tags=tag)
            c.create_oval(x+39,y+34,x+43,y+39,fill="#263948",outline="",tags=tag)
        elif key == "pinball":
            c.create_rectangle(x+15,y+8,x+71,y+65,fill="#142946",outline="#d8e7fc",width=2,tags=tag)
            c.create_rectangle(x+19,y+12,x+67,y+61,fill="#233958",outline="",tags=tag)
            for bx,by in ((31,27),(55,27),(43,40)):
                c.create_oval(x+bx-6,y+by-6,x+bx+6,y+by+6,fill="#e7b96b",outline="#fff0ad",tags=tag)
            c.create_line(x+27,y+54,x+39,y+59,fill="#78cde2",width=4,tags=tag)
            c.create_line(x+59,y+54,x+47,y+59,fill="#78cde2",width=4,tags=tag)
            c.create_oval(x+46,y+44,x+52,y+50,fill="#f2f3f5",outline="",tags=tag)
        elif key == "pong":
            c.create_rectangle(x+8,y+14,x+80,y+62,fill="#142851",outline="#c8e2ff",width=2,tags=tag)
            c.create_rectangle(x+17,y+26,x+23,y+52,fill="#7bdeff",outline="",tags=tag)
            c.create_rectangle(x+65,y+22,x+71,y+48,fill="#ffc875",outline="",tags=tag)
            for dy in (22,34,46):
                c.create_rectangle(x+43,y+dy,x+45,y+dy+6,fill="#6688b7",outline="",tags=tag)
            c.create_rectangle(x+50,y+35,x+57,y+42,fill="white",outline="",tags=tag)
        else:
            c.create_rectangle(x+20,y+12,x+76,y+66,fill="#3b527c",outline="",tags=tag)
            c.create_rectangle(x+16,y+8,x+72,y+62,fill="#fff3cd",outline="#fffbe8",width=2,tags=tag)
            c.create_rectangle(x+16,y+8,x+25,y+62,fill="#8a71b5",outline="",tags=tag)
            c.create_rectangle(x+29,y+16,x+65,y+20,fill="#d7c49c",outline="",tags=tag)
            c.create_polygon(x+47,y+25,x+31,y+51,x+63,y+51,fill="#dce9ff",outline="#386cf5",width=2,tags=tag)
            c.create_line(x+37,y+41,x+57,y+41,fill="#386cf5",tags=tag)
            c.create_line(x+47,y+41,x+47,y+51,fill="#386cf5",tags=tag)
            c.create_text(x+47,y+34,text="V",fill="#386cf5",font=("Tahoma",8,"bold"),tags=tag)
        self.shadow_text(x+43,y+82,title,("Tahoma",11,"bold"),(tag,))
        c.tag_bind(tag,"<Button-1>",lambda event,k=key:self.press_icon(event,k))
        c.tag_bind(tag,"<Enter>",lambda event,k=key:self.hover(k,True))
        c.tag_bind(tag,"<Leave>",lambda event,k=key:self.hover(k,False))

    def hover(self,key,active):
        self.canvas.configure(cursor="fleur" if self.icon_drag and self.icon_drag["moved"] else ("hand2" if active else ""))
        self.canvas.itemconfigure("selection:"+key,state="normal" if active or self.selected_icon==key else "hidden")

    def draw(self):
        self.resize_job = None
        if not self.winfo_exists():
            return
        width,height = max(1,self.canvas.winfo_width()),max(1,self.canvas.winfo_height())
        self.background = self.wallpaper.image(self,width,max(1,height-TASKBAR_HEIGHT))
        self.canvas.delete("all")
        self.canvas.create_image(0,0,image=self.background,anchor="nw",tags="wallpaper")
        titles={"resistencias":"Calculadora de\nresistencias","fuentes":"Asociación de\nfuentes","formulas":"Fórmulas\neléctricas","pong":"Pong","pinball":"Pinball","flappy":"Flappy Volt"}
        for key,title in titles.items():
            x,y=self.icon_layout.visible(key,width,height-TASKBAR_HEIGHT)
            self.draw_icon(key,x,y,title)
        if width >= 720:
            self.shadow_text(width-28,38,"Electrico Tools",("Tahoma",22,"bold"),anchor="ne")
            self.shadow_text(width-28,73,"Tu laboratorio eléctrico",("Tahoma",11),anchor="ne")
        self.shadow_text(width-18,height-60,self.icon_status,("Tahoma",9),anchor="se")
        self.draw_taskbar(width,height)
        self.update_clock()
        if self.menu:
            self.place_menu()
        for chrome in self.chromes.values():
            chrome.fit_desktop()

    def draw_taskbar(self,width,height):
        y=height-TASKBAR_HEIGHT
        for offset,color in enumerate(("#6ea6f8","#3c82e8","#276bd8","#2662ce")):
            self.canvas.create_rectangle(0,y+offset*3,width,height,fill=color,outline="")
        self.draw_start_button(height)
        self.draw_task_buttons(width, height)
        self.canvas.create_rectangle(width-78,y+2,width,height,fill="#1599e4",outline="#6dc5fa",tags="tray")
        self.canvas.create_text(width-39,y+TASKBAR_HEIGHT/2,text="",fill="white",font=("Tahoma",10),tags="clock")

    def draw_start_button(self, height):
        """Esquina superior derecha redondeada; esquina inferior recta."""
        top, bottom, right, radius = height-TASKBAR_HEIGHT, height-1, 107, 12
        # Franjas recortadas al arco: el contorno permanece curvo al redimensionar.
        for row in range(top, bottom+1):
            distance = row-top
            extent = right if distance>=radius else right-radius+sqrt(max(0,radius**2-(radius-distance)**2))
            fraction = (row-top)/(bottom-top)
            if fraction < 0.18:
                blend = fraction/0.18
                upper, lower = (140,202,111), (64,161,58)
            else:
                blend = (fraction-0.18)/0.82
                upper, lower = (64,161,58), (40,119,43)
            color = "#"+"".join(f"{round(a+(b-a)*blend):02x}" for a,b in zip(upper,lower))
            self.canvas.create_line(0,row,extent,row,fill=color,tags="start")
        self.canvas.create_line(0,top, right-radius,top,fill="#b3df91",tags="start")
        self.canvas.create_line(0,bottom,right,bottom,fill="#205c29",tags="start")
        for dx,dy,color in ((0,0,"#f55c38"),(8,0,"#86cf50"),(0,8,"#65b8f4"),(8,8,"#ffd269")):
            self.canvas.create_rectangle(12+dx,top+10+dy,18+dx,top+16+dy,fill=color,outline="",tags="start")
        self.canvas.create_text(65,top+20,text="Inicio",fill="white",font=("Tahoma",14,"bold","italic"),tags="start")
        self.canvas.tag_bind("start","<Button-1>",lambda event:self.toggle_menu())
        self.canvas.tag_bind("start","<Enter>",lambda event:self.canvas.configure(cursor="hand2"))
        self.canvas.tag_bind("start","<Leave>",lambda event:self.canvas.configure(cursor=""))

    def draw_task_buttons(self, width=None, height=None):
        """Botones Luna: bisel, icono de 16 px y texto alineado a la izquierda."""
        width = width or self.canvas.winfo_width()
        height = height or self.canvas.winfo_height()
        self.canvas.delete("taskbuttons")
        available = max(90, width-194)
        button_width = min(196, available//max(1,len(self.windows)))
        for index,key in enumerate(self.windows):
            x, top = 112+index*button_width, height-TASKBAR_HEIGHT+5
            right, bottom = x+button_width-5, height-6
            active = key == self.active_tool
            tag = "task:"+key
            tags = (tag,"taskbuttons")
            edge = "#124492" if active else "#1558bb"
            body = "#205abd" if active else "#3980df"
            highlight = "#3e79ca" if active else "#78b5ff"
            shadow = "#123f8a" if active else "#235eb8"
            # Esquinas escalonadas y doble bisel, como los botones de XP.
            self.canvas.create_rectangle(x+1,top,right-1,bottom,fill=edge,outline="",tags=tags)
            self.canvas.create_rectangle(x,top+1,right,bottom-1,fill=edge,outline="",tags=tags)
            self.canvas.create_rectangle(x+2,top+2,right-2,bottom-2,fill=body,outline="",tags=tags)
            self.canvas.create_rectangle(x+2,top+2,right-2,top+6,fill="#2868c5" if active else "#4d94ed",outline="",tags=tags)
            self.canvas.create_line(x+2,top+1,right-2,top+1,fill=highlight,tags=tags)
            self.canvas.create_line(x+1,top+2,x+1,bottom-2,fill=highlight,tags=tags)
            self.canvas.create_line(x+2,bottom-1,right-1,bottom-1,fill=shadow,tags=tags)
            self.canvas.create_line(right-1,top+2,right-1,bottom-1,fill=shadow,tags=tags)
            cy=(top+bottom)/2
            shift=1 if active else 0
            ix=x+9+shift
            if key=="resistencias":
                self.canvas.create_line(ix,cy,ix+17,cy,fill="#e1eeff",width=2,tags=tags)
                self.canvas.create_rectangle(ix+3,cy-4,ix+14,cy+4,fill="#f7d290",outline="#a96c2d",tags=tags)
                for offset,color in ((6,"#bc563c"),(9,"#80442b"),(12,"#c69935")):
                    self.canvas.create_line(ix+offset,cy-3,ix+offset,cy+3,fill=color,width=2,tags=tags)
            elif key=="fuentes":
                self.canvas.create_rectangle(ix+5,cy-9,ix+11,cy-7,fill="#cbdcf4",outline="",tags=tags)
                self.canvas.create_rectangle(ix+2,cy-7,ix+14,cy+8,fill="#89d8bb",outline="#d5f5e9",tags=tags)
                self.canvas.create_line(ix+5,cy-2,ix+11,cy-2,fill="#225d63",width=2,tags=tags)
                self.canvas.create_line(ix+8,cy-5,ix+8,cy+1,fill="#225d63",width=2,tags=tags)
                self.canvas.create_line(ix+5,cy+4,ix+11,cy+4,fill="#225d63",width=2,tags=tags)
            elif key=="flappy":
                self.canvas.create_oval(ix,cy-6,ix+13,cy+6,fill="#f4d278",outline="#e8c275",tags=tags)
                self.canvas.create_polygon(ix+11,cy-2,ix+17,cy+1,ix+11,cy+3,fill="#ed9859",outline="",tags=tags)
                self.canvas.create_oval(ix+7,cy-4,ix+10,cy-1,fill="#263948",outline="",tags=tags)
            elif key=="pinball":
                self.canvas.create_rectangle(ix+2,cy-8,ix+15,cy+8,fill="#142946",outline="#aec9eb",tags=tags)
                self.canvas.create_oval(ix+5,cy-5,ix+10,cy,fill="#e7b96b",outline="",tags=tags)
                self.canvas.create_line(ix+4,cy+5,ix+8,cy+7,fill="#78cde2",width=2,tags=tags)
                self.canvas.create_line(ix+13,cy+5,ix+9,cy+7,fill="#78cde2",width=2,tags=tags)
            elif key=="pong":
                self.canvas.create_rectangle(ix,cy-7,ix+17,cy+7,fill="#142851",outline="#b1d4ff",tags=tags)
                self.canvas.create_line(ix+3,cy-4,ix+3,cy+4,fill="#7bdeff",width=2,tags=tags)
                self.canvas.create_line(ix+14,cy-4,ix+14,cy+4,fill="#ffc875",width=2,tags=tags)
                self.canvas.create_rectangle(ix+8,cy-1,ix+10,cy+1,fill="white",outline="",tags=tags)
            else:
                self.canvas.create_rectangle(ix+2,cy-8,ix+15,cy+8,fill="#fff3cd",outline="#e2d3aa",tags=tags)
                self.canvas.create_rectangle(ix+2,cy-8,ix+5,cy+8,fill="#8a71b5",outline="",tags=tags)
                self.canvas.create_line(ix+8,cy-3,ix+13,cy-3,fill="#587ec7",tags=tags)
                self.canvas.create_line(ix+8,cy+1,ix+13,cy+1,fill="#587ec7",tags=tags)
                self.canvas.create_line(ix+8,cy+5,ix+13,cy+5,fill="#587ec7",tags=tags)
            font=tkfont.Font(root=self, family="Tahoma", size=9, weight="bold" if active else "normal")
            title={"resistencias":"Resistencias","fuentes":"Fuentes","formulas":"Fórmulas","pong":"Pong","pinball":"Pinball","flappy":"Flappy Volt"}[key]
            available_text=max(0,right-x-35)
            if font.measure(title)>available_text:
                while title and font.measure(title+"…")>available_text:
                    title=title[:-1]
                title+="…"
            self.canvas.create_text(x+31+shift,cy+shift,anchor="w",text=title,fill="white",font=("Tahoma",9,"bold" if active else "normal"),tags=tags)
            self.canvas.tag_bind(tag,"<Button-1>",lambda event,k=key:self.toggle_task(k))
            self.canvas.tag_bind(tag,"<Enter>",lambda event:self.canvas.configure(cursor="hand2"))
            self.canvas.tag_bind(tag,"<Leave>",lambda event:self.canvas.configure(cursor=""))

    def set_active_tool(self, key):
        if self.active_tool != key:
            previous=self.apps.get(self.active_tool)
            if hasattr(previous,"on_minimize"):
                previous.on_minimize()
            self.active_tool = key
            self.draw_task_buttons()
            for chrome_key,chrome in self.chromes.items():
                chrome.set_active(chrome_key==key)

    def update_clock(self):
        self.canvas.itemconfigure("clock",text=datetime.now().strftime("%H:%M"))

    def tick_clock(self):
        self.update_clock()
        self.clock_job=self.after(15000,self.tick_clock)

    def cycle_icons(self,event=None):
        keys=("resistencias","fuentes","formulas","pong","pinball","flappy")
        self.selected_icon=keys[(keys.index(self.selected_icon)+1)%len(keys)] if self.selected_icon in keys else keys[0]
        for key in keys:
            self.canvas.itemconfigure("selection:"+key,state="normal" if key==self.selected_icon else "hidden")
        return "break"

    def open_selected(self,event=None):
        if self.selected_icon:
            self.open_tool(self.selected_icon)
        return "break"

    def press_icon(self,event,key):
        self.close_menu()
        self.canvas.focus_set()
        self.selected_icon=key
        for candidate in self.icon_layout.positions:
            self.canvas.itemconfigure("selection:"+candidate,state="normal" if candidate==key else "hidden")
        x,y=self.icon_layout.visible(key,self.canvas.winfo_width(),self.canvas.winfo_height()-TASKBAR_HEIGHT)
        self.icon_drag={"key":key,"mouse":(event.x,event.y),"origin":(x,y),"current":(x,y),"moved":False}
        self.canvas.grab_set()
        return "break"

    def drag_icon(self,event):
        drag=self.icon_drag
        if not drag:
            return
        dx,dy=event.x-drag["mouse"][0],event.y-drag["mouse"][1]
        if not drag["moved"] and dx*dx+dy*dy<36:
            return
        drag["moved"]=True
        key=drag["key"]
        x,y=self.icon_layout.move(key,drag["origin"][0]+dx,drag["origin"][1]+dy,self.canvas.winfo_width(),self.canvas.winfo_height()-TASKBAR_HEIGHT)
        old_x,old_y=drag["current"]
        self.canvas.move("icon:"+key,x-old_x,y-old_y)
        drag["current"]=(x,y)
        self.canvas.configure(cursor="fleur")
        return "break"

    def release_icon(self,event):
        drag,self.icon_drag=self.icon_drag,None
        if not drag:
            return
        self.canvas.grab_release()
        self.canvas.configure(cursor="")
        if drag["moved"]:
            if not self.icon_layout.save():
                self.icon_status="No se pudo guardar la posición de los iconos"
                self.schedule_draw()
        else:
            self.open_tool(drag["key"])
        return "break"

    def background_click(self,event):
        tags=self.canvas.gettags("current")
        if "wallpaper" in tags:
            self.set_active_tool(None)
            self.selected_icon=None
            for key in self.icon_layout.positions:
                self.canvas.itemconfigure("selection:"+key,state="hidden")
            self.close_menu()
            self.canvas.focus_set()

    def toggle_menu(self):
        if self.menu:
            self.close_menu()
            return
        self.set_active_tool(None)
        self.menu=StartMenu(self)
        self.place_menu()

    def place_menu(self):
        if not self.menu:
            return
        self.menu.update_idletasks()
        height=self.menu.winfo_reqheight()
        self.menu.place(x=6,y=max(6,self.canvas.winfo_height()-TASKBAR_HEIGHT-height),width=min(440,self.canvas.winfo_width()-12),height=height)

    def toggle_fullscreen(self,event=None):
        root=self.winfo_toplevel()
        self.fullscreen=not self.fullscreen
        if self.fullscreen:
            self.windowed_geometry=root.geometry()
            self.windowed_state=root.state()
            root.attributes("-fullscreen",True)
        else:
            root.attributes("-fullscreen",False)
            if self.windowed_geometry:
                root.geometry(self.windowed_geometry)
            root.state(self.windowed_state)
        self.fullscreen_text.set("Salir de pantalla completa    F11" if self.fullscreen else "Pantalla completa    F11")
        root.lift()
        self.canvas.focus_set()
        self.schedule_draw()
        return "break"

    def escape(self,event=None):
        if self.menu:
            self.close_menu()
        elif self.fullscreen:
            self.toggle_fullscreen()
        return "break"

    def shutdown(self):
        """Cierra todo Electrico Tools, incluidos diálogos y appXP ocultas."""
        self.winfo_toplevel().destroy()
        self.windows.clear()
        self.apps.clear()
        self.chromes.clear()

    def close_menu(self):
        if self.menu:
            self.menu.destroy()
            self.menu=None

    def minimize_tool(self,key):
        window=self.windows.get(key)
        if window and window.winfo_exists():
            app=self.apps.get(key)
            if hasattr(app,"on_hide"):
                app.on_hide()
            elif hasattr(app,"on_minimize"):
                app.on_minimize()
            window.withdraw()
            if self.active_tool==key:
                self.set_active_tool(None)
            self.winfo_toplevel().lift()
            self.canvas.focus_set()

    def toggle_task(self,key):
        window=self.windows.get(key)
        if not window or not window.winfo_exists():
            self.open_tool(key)
        elif window.state() in ("withdrawn","iconic"):
            self.open_tool(key)
        else:
            self.minimize_tool(key)

    def open_tool(self,key):
        if key not in ("resistencias","fuentes","formulas","pong","pinball","flappy"):
            raise ValueError("Herramienta no disponible.")
        if key in GAME_KEYS:
            for other in tuple(self.windows):
                if other in GAME_KEYS and other!=key:
                    self.close_tool(other)
        self.close_menu()
        self.selected_icon=key
        self.set_active_tool(key)
        existing=self.windows.get(key)
        if existing and existing.winfo_exists():
            existing.deiconify()
            existing.lift()
            existing.focus_force()
            app=self.apps.get(key)
            if hasattr(app,"on_restore"):
                app.on_restore()
            return
        if key=="resistencias":
            from resistencias.gui import CalculatorApp
            app_class,title=CalculatorApp,"Calculadora de resistencias"
        elif key=="fuentes":
            from fuentes.gui import SourcesApp
            app_class,title=SourcesApp,"Asociación de fuentes"
        elif key=="flappy":
            from juegos.flappy import FlappyApp
            app_class,title=FlappyApp,"Flappy Volt"
        elif key=="pinball":
            from juegos.pinball import PinballApp
            app_class,title=PinballApp,"Pinball · Órbita espacial"
        elif key=="pong":
            from juegos.pong import PongApp
            app_class,title=PongApp,"Pong"
        else:
            from formulas.gui import FormulasApp
            app_class,title=FormulasApp,"Fórmulas eléctricas"
        window=tk.Toplevel(self)
        window.withdraw()
        window.overrideredirect(True)
        window.transient(self.winfo_toplevel())
        window.title("Electrico Tools · "+title)
        width=max(480,min(1160,self.canvas.winfo_width()-48))
        height=max(540,min(900 if key=="pinball" else 780,self.canvas.winfo_height()-TASKBAR_HEIGHT-48))
        x=self.canvas.winfo_rootx()+max(0,(self.canvas.winfo_width()-width)//2)
        y=self.canvas.winfo_rooty()+max(0,(self.canvas.winfo_height()-TASKBAR_HEIGHT-height)//2)
        window.geometry(f"{width}x{height}+{x}+{y}")
        window.minsize(480,540)
        window.configure(background="#e8eef8")
        chrome=XPWindowChrome(window,title,key,self,lambda:self.minimize_tool(key),lambda:self.close_tool(key))
        self.chromes[key]=chrome
        window.xp_chrome=chrome
        app=app_class(chrome.content)
        self.windows[key]=window
        self.apps[key]=app
        window.bind("<FocusIn>", lambda event,k=key:self.set_active_tool(k))
        ttk.Button(app.header,text="← Escritorio",style="Blue.TButton",command=lambda:self.return_home(key)).place(relx=1,x=-8,y=6,anchor="ne")
        window.protocol("WM_DELETE_WINDOW",lambda:self.close_tool(key))
        window.deiconify()
        window.lift()
        window.focus_force()
        if hasattr(app,"on_restore"):
            app.on_restore()
        self.schedule_draw()

    def return_home(self,key):
        window=self.windows.get(key)
        if window:
            app=self.apps.get(key)
            if hasattr(app,"on_minimize"):
                app.on_minimize()
            window.withdraw()
        self.set_active_tool(None)
        self.winfo_toplevel().deiconify()
        self.winfo_toplevel().lift()
        self.canvas.focus_set()

    def close_tool(self,key):
        if self.active_tool == key:
            self.active_tool = None
        window=self.windows.pop(key,None)
        self.apps.pop(key,None)
        self.chromes.pop(key,None)
        if window:
            window.destroy()
        self.schedule_draw()
        self.winfo_toplevel().lift()


def main():
    root=tk.Tk()
    root.withdraw()
    root.title("Electrico Tools · Escritorio")
    sw,sh=root.winfo_screenwidth(),root.winfo_screenheight()
    root.geometry(f"{max(480,min(1160,sw-80))}x{max(540,min(780,sh-100))}")
    root.minsize(480,540)
    configure_theme(root)
    desktop=DesktopApp(root)
    desktop.toggle_fullscreen()
    desktop.windowed_geometry=f"{max(480,min(1160,sw-80))}x{max(540,min(780,sh-100))}"
    root.deiconify()
    root.mainloop()
