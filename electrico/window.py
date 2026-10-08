"""Marco y barra de título Luna para ventanas appXP."""
import tkinter as tk
from tkinter import font as tkfont


class XPWindowChrome(tk.Frame):
    TITLE_HEIGHT = 32

    def __init__(self, window, title, key, desktop, on_minimize, on_close):
        super().__init__(window,background="#1457c9",borderwidth=3,relief="flat")
        self.pack(fill="both",expand=True)
        self.window,self.desktop,self.title,self.key=window,desktop,title,key
        self.on_minimize,self.on_close=on_minimize,on_close
        self.maximized=False
        self.restore_geometry=None
        self.drag_origin=None
        self.resize_origin=None
        self.active=True
        self.hover_control=None
        self.titlebar=tk.Canvas(self,height=self.TITLE_HEIGHT,background="#2568df",highlightthickness=0)
        self.titlebar.pack(fill="x")
        self.content=tk.Frame(self,background="#e8eef8")
        self.content.pack(fill="both",expand=True)
        self.grip=tk.Canvas(self,width=12,height=12,background="#e8eef8",highlightthickness=0,cursor="size_nw_se")
        self.grip.place(relx=1,rely=1,anchor="se")
        for offset in (3,6,9):
            self.grip.create_line(offset,11,11,offset,fill="#6482af")
        self.grip.bind("<ButtonPress-1>",self.start_resize)
        self.grip.bind("<B1-Motion>",self.resize)
        self.grip.bind("<ButtonRelease-1>",lambda event:self.end_drag())
        self.titlebar.bind("<Configure>",lambda event:self.draw_titlebar())
        self.titlebar.bind("<ButtonPress-1>",self.press)
        self.titlebar.bind("<B1-Motion>",self.drag)
        self.titlebar.bind("<ButtonRelease-1>",lambda event:self.end_drag())
        self.titlebar.bind("<Double-1>",self.double_click)
        self.titlebar.bind("<Motion>",self.hover)
        self.titlebar.bind("<Leave>",lambda event:self.clear_hover())
        window.bind("<Alt-F4>",lambda event:self.on_close())

    def set_active(self,active):
        if self.active!=active:
            self.active=active
            self.draw_titlebar()

    def draw_titlebar(self):
        c=self.titlebar
        c.delete("all")
        width=max(1,c.winfo_width())
        colors=("#719ff7","#4287ee","#1e67da","#1a59c8","#1452c2") if self.active else ("#9ab8e7","#7e9ed4","#6d8fca","#6386c3","#5d7eba")
        for row in range(self.TITLE_HEIGHT):
            c.create_line(0,row,width,row,fill=colors[min(4,row*5//self.TITLE_HEIGHT)])
        c.create_line(0,0,width,0,fill="#adc9ff")
        self.draw_icon(9,8)
        font=tkfont.Font(root=self,family="Tahoma",size=10,weight="bold")
        text=self.title
        available=max(0,width-126)
        if font.measure(text)>available:
            while text and font.measure(text+"…")>available:
                text=text[:-1]
            text+="…"
        c.create_text(31,17,text=text,anchor="w",fill="#174388",font=("Tahoma",10,"bold"))
        c.create_text(30,16,text=text,anchor="w",fill="white",font=("Tahoma",10,"bold"))
        for index,control in enumerate(("minimize","maximize","close")):
            x=width-80+index*26
            tags=("control:"+control,)
            close=control=="close"
            body=("#e98666" if self.hover_control==control else "#df674d") if close else ("#72a6ff" if self.hover_control==control else "#4382df")
            c.create_rectangle(x,4,x+23,27,fill=body,outline="#f4f7ff",width=1,tags=tags)
            c.create_line(x+2,5,x+21,5,fill="#ffd3ae" if close else "#9dc2ff",tags=tags)
            c.create_line(x+22,6,x+22,25,fill="#a53a27" if close else "#1f53a9",tags=tags)
            if control=="minimize":
                c.create_line(x+5,21,x+16,21,fill="white",width=3,tags=tags)
            elif control=="maximize":
                if self.maximized:
                    c.create_rectangle(x+8,9,x+18,18,outline="white",width=2,tags=tags)
                    c.create_rectangle(x+5,12,x+15,22,fill=body,outline="white",width=2,tags=tags)
                else:
                    c.create_rectangle(x+5,9,x+18,22,outline="white",width=2,tags=tags)
                    c.create_line(x+5,10,x+18,10,fill="white",width=3,tags=tags)
            else:
                c.create_line(x+6,10,x+17,21,fill="white",width=2,tags=tags)
                c.create_line(x+17,10,x+6,21,fill="white",width=2,tags=tags)

    def draw_icon(self,x,y):
        c=self.titlebar
        if self.key=="resistencias":
            c.create_line(x,y+8,x+18,y+8,fill="#e2f1ff",width=2)
            c.create_rectangle(x+3,y+4,x+15,y+12,fill="#ffd88d",outline="#a9692b")
            c.create_line(x+7,y+4,x+7,y+12,fill="#a74731",width=2)
            c.create_line(x+11,y+4,x+11,y+12,fill="#ac852f",width=2)
        elif self.key=="fuentes":
            c.create_rectangle(x+5,y-1,x+12,y+1,fill="#dce6ff",outline="")
            c.create_rectangle(x+2,y+1,x+16,y+16,fill="#8bd9be",outline="#dcffef")
            c.create_text(x+9,y+8,text="+",fill="#246364",font=("Tahoma",9,"bold"))
        elif self.key=="flappy":
            c.create_oval(x,y+3,x+14,y+15,fill="#f4d278",outline="#e8c275")
            c.create_polygon(x+12,y+7,x+19,y+10,x+12,y+12,fill="#ed9859",outline="")
            c.create_oval(x+8,y+5,x+11,y+8,fill="#263948",outline="")
        elif self.key=="pinball":
            c.create_rectangle(x+2,y,x+16,y+17,fill="#142946",outline="#aec9eb")
            c.create_oval(x+6,y+3,x+12,y+9,fill="#e7b96b",outline="")
            c.create_line(x+4,y+13,x+8,y+16,fill="#78cde2",width=2)
            c.create_line(x+14,y+13,x+10,y+16,fill="#78cde2",width=2)
        elif self.key=="pong":
            c.create_rectangle(x,y+1,x+18,y+15,fill="#142851",outline="#b1d4ff")
            c.create_line(x+3,y+4,x+3,y+12,fill="#7bdeff",width=2)
            c.create_line(x+15,y+4,x+15,y+12,fill="#ffc875",width=2)
            c.create_rectangle(x+8,y+7,x+10,y+9,fill="white",outline="")
        else:
            c.create_rectangle(x+2,y,x+16,y+16,fill="#fff3cd",outline="#e1d3ac")
            c.create_rectangle(x+2,y,x+5,y+16,fill="#8a71b5",outline="")
            c.create_text(x+11,y+8,text="V",fill="#386cf5",font=("Tahoma",8,"bold"))

    def control_at(self,event):
        width=self.titlebar.winfo_width()
        if 4<=event.y<=27:
            for index,control in enumerate(("minimize","maximize","close")):
                x=width-80+index*26
                if x<=event.x<=x+23:
                    return control
        return None

    def hover(self,event):
        control=self.control_at(event)
        if control!=self.hover_control:
            self.hover_control=control
            self.titlebar.configure(cursor="hand2" if control else "")
            self.draw_titlebar()

    def clear_hover(self):
        self.hover_control=None
        self.draw_titlebar()

    def press(self,event):
        control=self.control_at(event)
        if control:
            {"minimize":self.on_minimize,"maximize":self.toggle_maximize,"close":self.on_close}[control]()
            return "break"
        self.window.lift()
        self.window.focus_force()
        if not self.maximized:
            self.drag_origin=(event.x_root,event.y_root,self.window.winfo_x(),self.window.winfo_y())

    def drag(self,event):
        if self.drag_origin:
            sx,sy,x,y=self.drag_origin
            nx,ny=max(0,x+event.x_root-sx),max(0,y+event.y_root-sy)
            self.window.geometry(f"+{nx}+{ny}")

    def end_drag(self):
        self.drag_origin=self.resize_origin=None

    def double_click(self,event):
        if not self.control_at(event):
            self.toggle_maximize()
        return "break"

    def start_resize(self,event):
        if not self.maximized:
            self.resize_origin=(event.x_root,event.y_root,self.window.winfo_width(),self.window.winfo_height())

    def resize(self,event):
        if self.resize_origin:
            sx,sy,w,h=self.resize_origin
            self.window.geometry(f"{max(480,w+event.x_root-sx)}x{max(540,h+event.y_root-sy)}")

    def toggle_maximize(self):
        if self.maximized:
            self.maximized=False
            self.window.minsize(480,540)
            if self.restore_geometry:
                self.window.geometry(self.restore_geometry)
            self.grip.place(relx=1,rely=1,anchor="se")
        else:
            self.restore_geometry=self.window.geometry()
            self.maximized=True
            self.window.minsize(320,300)
            self.fit_desktop()
            self.grip.place_forget()
        self.draw_titlebar()

    def fit_desktop(self):
        if self.maximized:
            from .desktop import TASKBAR_HEIGHT
            canvas=self.desktop.canvas
            width=canvas.winfo_width()
            height=max(300,canvas.winfo_height()-TASKBAR_HEIGHT)
            self.window.geometry(f"{width}x{height}+{canvas.winfo_rootx()}+{canvas.winfo_rooty()}")
