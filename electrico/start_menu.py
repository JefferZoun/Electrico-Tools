"""Menú Luna con iconos dibujados: no depende de glifos especiales."""
import tkinter as tk


def draw_icon(c, kind, size=32):
    c.delete("all")
    s = size / 32
    def rect(a,b,d,e,fill,outline=""):
        c.create_rectangle(a*s,b*s,d*s,e*s,fill=fill,outline=outline)
    if kind == "power":
        # Botón XP: bisel blanco, rojo degradado y símbolo de encendido.
        rect(2,2,30,30,"#ffffff")
        rect(3,3,29,29,"#942221")
        for y in range(4,28):
            t=(y-4)/23
            color="#%02x%02x%02x" % (int(247-49*t),int(116-74*t),int(92-55*t))
            c.create_line(4*s,y*s,28*s,y*s,fill=color,width=max(1,s))
        c.create_line(5*s,4*s,27*s,4*s,fill="#ffc1a4",width=s)
        c.create_arc(9*s,9*s,23*s,24*s,start=135,extent=270,style="arc",outline="white",width=3*s)
        c.create_line(16*s,7*s,16*s,16*s,fill="white",width=3*s)
    elif kind == "flappy":
        c.create_oval(2*s,9*s,25*s,27*s,fill="#f4d278",outline="#b99045")
        c.create_polygon(23*s,15*s,32*s,20*s,23*s,23*s,fill="#ed9859",outline="")
        c.create_oval(17*s,11*s,23*s,17*s,fill="white",outline="")
        c.create_oval(20*s,12*s,23*s,16*s,fill="#263948",outline="")
    elif kind == "pinball":
        rect(5,2,27,30,"#142946","#779bd3")
        for x,y in ((12,11),(21,11),(16,18)):
            c.create_oval((x-3)*s,(y-3)*s,(x+3)*s,(y+3)*s,fill="#e7b96b",outline="")
        c.create_line(10*s,24*s,15*s,27*s,fill="#78cde2",width=2*s)
        c.create_line(22*s,24*s,17*s,27*s,fill="#78cde2",width=2*s)
    elif kind == "pong" or kind == "games":
        rect(2,5,30,27,"#142851","#779bd3")
        rect(6,10,9,22,"#76e5ff")
        rect(23,9,26,21,"#ffcd75")
        for y in (9,15,21): rect(15,y,16,y+3,"#6a82ae")
        rect(18,15,21,18,"white")
    elif kind == "resistencias":
        rect(1,15,31,18,"#8b9bad")
        rect(6,8,26,24,"#ffe2a0","#bc8c44")
        for x,color in ((10,"#ac4938"),(15,"#764730"),(22,"#c49740")): rect(x,9,x+2,23,color)
    elif kind == "fuentes":
        rect(11,2,21,5,"#8194af")
        rect(5,5,27,29,"#80dcca","#34877e")
        rect(9,12,17,15,"#246779"); rect(12,9,15,19,"#246779")
        rect(20,12,24,15,"#246779")
    elif kind == "formulas":
        rect(5,3,27,29,"#fff2cd","#b9a780")
        rect(5,3,10,29,"#9074bb")
        for y in (10,16,22): rect(14,y,23,y+2,"#6788bf")
    elif kind == "screen":
        rect(2,4,30,24,"#c7d4e8","#647798")
        rect(5,7,27,21,"#4687dd")
        rect(13,24,19,28,"#7b8fa9"); rect(8,28,24,30,"#7b8fa9")
    else:
        rect(3,3,29,29,"#eef7ff","#bdd1ee")
        c.create_oval(10*s,6*s,22*s,18*s,fill="#f7d5a4",outline="")
        c.create_oval(6*s,18*s,26*s,31*s,fill="#4b95dd",outline="")


class StartMenu(tk.Frame):
    def __init__(self, desktop):
        super().__init__(desktop, bg="#2868d2", highlightthickness=2, highlightbackground="#164cb1")
        self.desktop=desktop
        self.flyout=None
        header=tk.Canvas(self,height=64,bg="#2868d2",highlightthickness=0)
        header.pack(fill="x")
        def paint(event):
            header.delete("all")
            for y in range(64):
                t=y/63
                header.create_line(0,y,event.width,y,fill="#%02x%02x%02x"%(int(52-23*t),int(139-40*t),int(230-30*t)))
            header.create_rectangle(10,8,58,56,fill="#f5faff",outline="#b8dcff",width=2)
            header.create_rectangle(13,11,55,53,fill="#88b5df",outline="")
            header.create_oval(26,17,43,34,fill="#ffe1b6",outline="")
            header.create_oval(18,34,51,59,fill="#2867b6",outline="")
            header.create_rectangle(13,53,55,56,fill="#f5faff",outline="")
            header.create_text(73,33,text="Electrico Tools",anchor="w",font=("Tahoma",15,"bold"),fill="#1c4c98")
            header.create_text(72,32,text="Electrico Tools",anchor="w",font=("Tahoma",15,"bold"),fill="white")
        header.bind("<Configure>",paint)
        body=tk.Frame(self,bg="#d3e5fa",height=278)
        body.pack(fill="both",expand=True)
        body.grid_columnconfigure(0,weight=6,uniform="columns")
        body.grid_columnconfigure(1,weight=5,uniform="columns")
        left=tk.Frame(body,bg="white",padx=5,pady=7)
        right=tk.Frame(body,bg="#d3e5fa",padx=5,pady=7)
        left.grid(row=0,column=0,sticky="nsew")
        right.grid(row=0,column=1,sticky="nsew",padx=(1,0))
        for title,key in (("Resistencias","resistencias"),("Asociación de fuentes","fuentes"),("Fórmulas eléctricas","formulas"),("Pong","pong"),("Pinball","pinball"),("Flappy Volt","flappy")):
            self.row(left,title,key,lambda k=key:desktop.open_tool(k),"white",bold=True)
        self.separator(left,"#d9e0e8")
        self.row(left,"Todos los programas  ▶","games",self.show_programs,"white",small=True)
        self.row(right,"Juegos  ▶","games",self.show_games,"#d3e5fa",bold=True)
        self.separator(right,"#a8c4e6")
        self.row(right,"Consulta de fórmulas","formulas",lambda:desktop.open_tool("formulas"),"#d3e5fa",small=True)
        self.row(right,"Pantalla completa\nF11","screen",desktop.toggle_fullscreen,"#d3e5fa",small=True,variable=desktop.fullscreen_text)
        tk.Label(right,text="Tu laboratorio eléctrico",bg="#d3e5fa",fg="#4e709c",font=("Tahoma",8),wraplength=155,pady=15).pack(fill="x")
        footer=tk.Frame(self,bg="#2876dd",padx=9,pady=6)
        footer.pack(fill="x")
        self.row(footer,"Apagar","power",desktop.shutdown,"#2876dd",foreground="white",side="right")

    @staticmethod
    def separator(parent,color):
        tk.Frame(parent,height=1,bg=color).pack(fill="x",padx=6,pady=5)

    def row(self,parent,text,icon,command,background,bold=False,small=False,foreground="#17375e",side="top",variable=None):
        row=tk.Frame(parent,bg=background,takefocus=True,cursor="hand2")
        row.pack(fill="x" if side=="top" else None,side=side,pady=1)
        canvas=tk.Canvas(row,width=32,height=32,bg=background,highlightthickness=0)
        canvas.pack(side="left",padx=(4,5),pady=4)
        draw_icon(canvas,icon)
        label=tk.Label(row,text=text,bg=background,fg=foreground,anchor="w",justify="left",wraplength=145,font=("Tahoma",9 if small else 10,"bold" if bold else "normal"),pady=4)
        label.pack(side="left",fill="x",expand=True,padx=(0,4))
        if variable:
            label.configure(textvariable=variable)
        def color(value):
            for widget in (row,canvas,label): widget.configure(bg=value)
            label.configure(fg="white" if value=="#316ac5" else foreground)
        def activate(event=None):
            command()
            return "break"
        for widget in (row,canvas,label):
            widget.bind("<Enter>",lambda e:color("#316ac5"))
            widget.bind("<Leave>",lambda e:color(background))
            widget.bind("<Button-1>",activate)
        row.bind("<FocusIn>",lambda e:color("#316ac5"))
        row.bind("<FocusOut>",lambda e:color(background))
        row.bind("<Return>",activate)
        row.bind("<space>",activate)
        row.bind("<Escape>",lambda e:self.desktop.close_menu())
        return row

    def show_programs(self):
        self.show_flyout("Todos los programas",(
            ("Resistencias","resistencias",lambda:self.desktop.open_tool("resistencias")),
            ("Fuentes","fuentes",lambda:self.desktop.open_tool("fuentes")),
            ("Fórmulas eléctricas","formulas",lambda:self.desktop.open_tool("formulas")),
            ("Juegos  ▶","games",self.show_games),
        ))

    def show_games(self):
        self.show_flyout("Juegos",(
            ("Pong","pong",lambda:self.desktop.open_tool("pong")),
            ("Pinball","pinball",lambda:self.desktop.open_tool("pinball")),
            ("Flappy Volt","flappy",lambda:self.desktop.open_tool("flappy")),
        ))

    def show_flyout(self,title,entries):
        if self.flyout:
            same=self.flyout_title==title
            self.flyout.destroy(); self.flyout=None
            if same:
                return
        self.flyout_title=title
        self.flyout=tk.Frame(self,bg="white",highlightthickness=2,highlightbackground="#2866c9")
        tk.Label(self.flyout,text=title,bg="#e9f1fc",fg="#194e9a",font=("Tahoma",10,"bold"),anchor="w",padx=9,pady=7).pack(fill="x")
        for label,icon,command in entries:
            self.row(self.flyout,label,icon,command,"white")
        self.flyout.place(relx=1,x=-8,y=85,anchor="ne",width=195)
        self.flyout.lift()
