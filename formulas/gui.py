"""AppXP de consulta: fórmulas, diagramas y ejemplos resueltos."""
import math
import tkinter as tk
from tkinter import ttk
import webbrowser
from .content import TOPICS


class FormulasApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)
        self.index = 0
        self.vir_choice = "V"
        self.layout_job = None
        self._compact = self._short = None
        self.topic_var = tk.StringVar(value=TOPICS[0].title)
        self.status_var = tk.StringVar()
        self._build()
        self.show_topic(0)

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.header = ttk.Frame(self,style="Header.TFrame",padding=(18,12))
        self.header.grid(row=0,column=0,sticky="ew",pady=(0,10))
        ttk.Label(self.header,text="⚡ ELECTRICO TOOLS · FÓRMULAS",style="Brand.TLabel").pack(anchor="w")
        self.subtitle = ttk.Label(self.header,text="Entiende las fórmulas eléctricas",style="Header.TLabel")
        self.subtitle.pack(anchor="w",pady=(4,0))
        navigation = ttk.Frame(self,style="Card.TFrame",padding=10)
        navigation.grid(row=1,column=0,sticky="ew",pady=(0,10))
        navigation.columnconfigure(1,weight=1)
        ttk.Label(navigation,text="Tema",style="Muted.TLabel").grid(row=0,column=0,padx=(0,8))
        self.topic_box = ttk.Combobox(navigation,textvariable=self.topic_var,values=[t.title for t in TOPICS],state="readonly",width=16)
        self.topic_box.grid(row=0,column=1,sticky="ew")
        self.topic_box.bind("<<ComboboxSelected>>",lambda event:self.show_topic(self.topic_box.current()))
        self.previous = ttk.Button(navigation,text="‹",width=3,style="Blue.TButton",command=lambda:self.change_topic(-1))
        self.previous.grid(row=0,column=2,padx=(6,3))
        self.next = ttk.Button(navigation,text="›",width=3,style="Blue.TButton",command=lambda:self.change_topic(1))
        self.next.grid(row=0,column=3)
        self.body = ttk.Frame(self,style="Card.TFrame",padding=10)
        self.body.grid(row=2,column=0,sticky="nsew")
        self.body.columnconfigure(1,weight=1)
        self.body.rowconfigure(0,weight=1)
        self.figure = tk.Canvas(self.body,background="#eef4fc",highlightthickness=0,width=270,height=150,takefocus=True)
        self.figure.bind("<Configure>",lambda event:self.draw_figure())
        self.reading = ttk.Frame(self.body,style="Card.TFrame")
        self.text = tk.Text(self.reading,wrap="word",width=25,height=4,relief="flat",background="#f9fbff",foreground="#243247",font=("Segoe UI",12),padx=16,pady=12,spacing1=3,spacing3=7)
        scrollbar = ttk.Scrollbar(self.reading,command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.pack(side="left",fill="both",expand=True)
        scrollbar.pack(side="right",fill="y")
        self.text.tag_configure("title",font=("Segoe UI",18,"bold"),foreground="#174b86",spacing3=10)
        self.text.tag_configure("subtitle",font=("Segoe UI",11),foreground="#63748b",spacing3=14)
        self.text.tag_configure("heading",font=("Segoe UI",13,"bold"),foreground="#174b86",spacing1=12,spacing3=8)
        self.text.tag_configure("formula",font=("Consolas",14,"bold"),foreground="#386cf5",background="#edf2fc",lmargin1=10,lmargin2=10,spacing1=8,spacing3=10)
        self.text.tag_configure("body",spacing3=9)
        self.text.tag_configure("example",font=("Segoe UI",12),lmargin1=8,lmargin2=8,spacing3=9)
        self.text.tag_configure("result",font=("Segoe UI",12,"bold"),foreground="#126c59",background="#e3f5ef",spacing1=6,spacing3=10)
        self.text.tag_configure("note",font=("Segoe UI",10),foreground="#63748b",spacing1=6,spacing3=10)
        footer = ttk.Frame(self)
        footer.grid(row=3,column=0,sticky="ew",pady=(8,0))
        footer.columnconfigure(0,weight=1)
        self.status_label = ttk.Label(footer,textvariable=self.status_var,style="Footer.TLabel",wraplength=600)
        self.status_label.grid(row=0,column=0,sticky="w",padx=(0,8))
        ttk.Button(footer,text="Referencia ↗",command=self.open_reference).grid(row=0,column=1)
        self.bind("<Configure>",self.schedule_layout)
        self.bind("<Destroy>",self.cleanup)
        window=self.winfo_toplevel()
        window.bind("<Alt-Left>",lambda event:self.change_topic(-1))
        window.bind("<Alt-Right>",lambda event:self.change_topic(1))

    def schedule_layout(self,event):
        if event.widget is self:
            if self.layout_job:
                self.after_cancel(self.layout_job)
            self.layout_job=self.after(40,self.apply_layout)

    def cleanup(self,event):
        if event.widget is self and self.layout_job:
            self.after_cancel(self.layout_job)
            self.layout_job=None

    def apply_layout(self):
        self.layout_job=None
        width,height=self.winfo_width(),self.winfo_height()
        if hasattr(self.winfo_toplevel(),"xp_chrome") and height<570:
            self.header.grid_remove()
        else:
            self.header.grid()
        short=height<650 or width<760
        if short!=self._short:
            self._short=short
            if short:
                self.subtitle.pack_forget()
                self.header.configure(padding=(14,8))
            else:
                self.subtitle.pack(anchor="w",pady=(4,0))
                self.header.configure(padding=(18,12))
        compact=width<860
        if compact!=self._compact:
            self._compact=compact
            self.figure.grid_forget()
            self.reading.grid_forget()
            if compact:
                self.body.columnconfigure(0,weight=1)
                self.body.columnconfigure(1,weight=0)
                self.body.rowconfigure(0,weight=0)
                self.body.rowconfigure(1,weight=1)
                self.figure.grid(row=0,column=0,sticky="ew",pady=(0,8))
                self.reading.grid(row=1,column=0,sticky="nsew")
            else:
                self.body.columnconfigure(0,weight=0)
                self.body.columnconfigure(1,weight=1)
                self.body.rowconfigure(0,weight=1)
                self.body.rowconfigure(1,weight=0)
                self.figure.grid(row=0,column=0,sticky="nsew",padx=(0,10))
                self.reading.grid(row=0,column=1,sticky="nsew")
        self.status_label.configure(wraplength=max(180,width-170))
        self.draw_figure()

    def show_topic(self,index):
        self.index=max(0,min(len(TOPICS)-1,index))
        topic=TOPICS[self.index]
        self.topic_var.set(topic.title)
        self.previous.configure(state="disabled" if self.index==0 else "normal")
        self.next.configure(state="disabled" if self.index==len(TOPICS)-1 else "normal")
        self.text.configure(state="normal")
        self.text.delete("1.0","end")
        self.text.insert("end",topic.title+"\n","title")
        self.text.insert("end",topic.subtitle+"\n\n","subtitle")
        for style,content in topic.blocks:
            self.text.insert("end",content+"\n\n",style)
        self.text.configure(state="disabled")
        self.text.yview_moveto(0)
        self.status_var.set(f"Ficha {self.index+1} de {len(TOPICS)} · Ejemplos y unidades")
        self.draw_figure()

    def change_topic(self,delta):
        self.show_topic(self.index+delta)
        return "break"

    def open_reference(self):
        webbrowser.open(TOPICS[self.index].reference)

    def select_vir(self,symbol):
        self.vir_choice=symbol
        self.draw_figure()

    def draw_figure(self):
        c=self.figure
        c.delete("all")
        width,height=max(1,c.winfo_width()),max(1,c.winfo_height())
        if width<30 or height<30:
            return
        cx=width/2
        compact=self._compact is not False
        top=8 if compact else max(36,height/2-110)
        key=TOPICS[self.index].key
        if key=="vir":
            apex,bottom=top+4,top+100
            c.create_polygon(cx,apex,cx-92,bottom,cx+92,bottom,fill="#dce8ff",outline="#386cf5",width=3)
            middle=top+56
            c.create_line(cx-49,middle,cx+49,middle,fill="#386cf5",width=2)
            c.create_line(cx,middle,cx,bottom,fill="#386cf5",width=2)
            for symbol,x,y in (("V",cx,top+34),("I",cx-38,top+79),("R",cx+38,top+79)):
                tag="vir:"+symbol
                color="#126c59" if symbol==self.vir_choice else "#386cf5"
                c.create_text(x,y,text=symbol,font=("Segoe UI",19,"bold"),fill=color,tags=tag)
                c.tag_bind(tag,"<Button-1>",lambda event,s=symbol:self.select_vir(s))
                c.tag_bind(tag,"<Enter>",lambda event:c.configure(cursor="hand2"))
                c.tag_bind(tag,"<Leave>",lambda event:c.configure(cursor=""))
            formula={"V":"V = I × R","I":"I = V / R","R":"R = V / I"}[self.vir_choice]
            c.create_text(cx,top+128,text=formula,fill="#126c59",font=("Consolas",15,"bold"),tags="vir-formula")
            if not compact:
                c.create_text(cx,top-20,text="Tapa lo que buscas",fill="#63748b",font=("Segoe UI",11))
                c.create_text(cx,top+176,text="V · voltios\nI · amperios\nR · ohmios",fill="#526884",font=("Segoe UI",12),justify="center")
        elif key=="conductor":
            left,right=cx-85,cx+85
            c.create_rectangle(left,top+42,right,top+80,fill="#f5cc79",outline="#d89b35",width=2)
            c.create_oval(left-15,top+42,left+15,top+80,fill="#ffdf9b",outline="#d89b35",width=2)
            c.create_oval(right-15,top+42,right+15,top+80,fill="#e6b459",outline="#d89b35",width=2)
            c.create_line(left,top+24,right,top+24,arrow="both",fill="#386cf5",width=2)
            c.create_text(cx,top+11,text="Longitud L",fill="#386cf5",font=("Segoe UI",10,"bold"))
            c.create_text(right,top+61,text="S",fill="#986217",font=("Segoe UI",12,"bold"))
            c.create_text(cx,top+118,text="R = L / (c × S)",fill="#126c59",font=("Consolas",14,"bold"))
            if not compact:
                c.create_text(cx,top+175,text="Más longitud → más R\nMás sección → menos R",fill="#526884",font=("Segoe UI",11),justify="center")
        elif key=="power":
            c.create_oval(cx-34,top+14,cx+34,top+82,fill="#fff1cc",outline="#e79f31",width=3)
            c.create_text(cx,top+48,text="P",fill="#986217",font=("Segoe UI",26,"bold"))
            c.create_text(cx,top+113,text="P = V × I",fill="#126c59",font=("Consolas",15,"bold"))
            if not compact:
                c.create_text(cx,top+173,text="1 W = 1 J/s\nEnergía por segundo",fill="#526884",font=("Segoe UI",12),justify="center")
        elif key=="energy":
            c.create_oval(cx-32,top+14,cx+32,top+78,fill="#e3f5ef",outline="#0d9488",width=3)
            c.create_line(cx,top+46,cx,top+24,fill="#0d9488",width=3)
            c.create_line(cx,top+46,cx+20,top+57,fill="#0d9488",width=3)
            c.create_text(cx,top+112,text="E = P × t",fill="#126c59",font=("Consolas",15,"bold"))
            if not compact:
                c.create_text(cx,top+175,text="W × s → J\nW × h → Wh\nkW × h → kWh",fill="#526884",font=("Segoe UI",12),justify="center")
        elif key=="joule":
            points=[cx-90,top+70]
            for i in range(12):
                points.extend((cx-78+i*14,top+70+(-12 if i%2==0 else 12)))
            points.extend((cx+90,top+70))
            c.create_line(*points,fill="#dc7850",width=4)
            for offset in (-40,0,40):
                c.create_line(cx+offset,top+45,cx+offset-7,top+31,cx+offset+5,top+16,cx+offset,top+4,smooth=True,fill="#e9ac52",width=2)
            c.create_text(cx,top+121,text="Ecalor = I² × R × t",fill="#986217",font=("Consolas",12,"bold"))
            if not compact:
                c.create_text(cx,top+180,text="Corriente doble\n→ calor × 4",fill="#526884",font=("Segoe UI",12),justify="center")
        else:
            c.create_text(cx,top+38,text="Wh  →  J",fill="#386cf5",font=("Consolas",22,"bold"))
            c.create_text(cx,top+76,text="× 3600",fill="#126c59",font=("Segoe UI",16,"bold"))
            c.create_text(cx,top+120,text="kWh ≠ kW/h",fill="#986217",font=("Consolas",14,"bold"))
            if not compact:
                c.create_text(cx,top+180,text="Conserva siempre\nlas unidades",fill="#526884",font=("Segoe UI",12),justify="center")
