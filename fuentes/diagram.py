"""Símbolos de generadores y resistencias internas."""
from resistencias.circuit import Group
from resistencias.diagram import CircuitDiagram
from .model import Generator, volts, ohms


class SourceDiagram(CircuitDiagram):
    def measure(self, node):
        if isinstance(node, Generator):
            return (230 if node.resistance else 170), 112
        return super().measure(node)

    def draw_node(self, node, x, y):
        if not isinstance(node, Generator):
            return super().draw_node(node, x, y)
        width, height = self.measure(node)
        cy = y+height/2
        tag = "node:"+node.id
        color = "#386cf5" if node.id == self.selected_id else "#0d9488"
        self.wire(x, cy, x+40, cy)
        self.canvas.create_oval(x+40, cy-23, x+86, cy+23, fill="#e3f5ef", outline=color, width=3, tags=tag)
        self.canvas.create_text(x+63, cy, text="+ −" if node.polarity==1 else "− +", font=("Segoe UI", 12, "bold"), fill=color, tags=tag)
        self.canvas.create_text(x+63, cy-39, text=node.name, fill="#223958", font=("Segoe UI", 11, "bold"), tags=tag)
        self.canvas.create_text(x+63, cy+39, text=volts(node.emf), fill="#526884", font=("Segoe UI", 10), tags=tag)
        if node.resistance:
            self.wire(x+86, cy, x+119, cy)
            self.canvas.create_rectangle(x+119, cy-12, x+166, cy+12, fill="#fff1cc", outline="#e79f31", width=2, tags=tag)
            self.canvas.create_text(x+143, cy+39, text="r = "+ohms(node.resistance), fill="#986217", font=("Segoe UI", 9), tags=tag)
            self.wire(x+166, cy, x+width, cy)
        else:
            self.wire(x+86, cy, x+width, cy)

    def set_sources(self, generators, mode, selected_id, load=None):
        self.load = load
        group = Group("A → B · Generadores", mode, list(generators), id="association")
        self.set_circuit(group, selected_id)

    def draw(self):
        self.canvas.delete("all")
        if not self.node:
            return
        width,height=self.measure(self.node)
        load=getattr(self,"load",None)
        full_height=height+(100 if load is not None else 0)
        x=max(30,(self.canvas.winfo_width()-width)/2)
        y=max(24,(self.canvas.winfo_height()-full_height)/2)
        self.draw_node(self.node,x,y)
        cy=y+height/2
        for px,label,color in ((x,"A","#386cf5"),(x+width,"B","#0d9488")):
            self.canvas.create_oval(px-5,cy-5,px+5,cy+5,fill=color,outline="")
            self.canvas.create_text(px,cy-16,text=label,fill=color,font=("Segoe UI",10,"bold"))
        if load is not None:
            baseline=y+height+38
            center=x+width/2
            self.wire(x,cy,x,baseline,center-28,baseline)
            self.wire(center+28,baseline,x+width,baseline,x+width,cy)
            if load==0:
                self.wire(center-28,baseline,center+28,baseline)
            else:
                self.canvas.create_rectangle(center-28,baseline-12,center+28,baseline+12,fill="#fff1cc",outline="#e79f31",width=2,tags="load")
            self.canvas.create_text(center,baseline+29,text="RL = "+ohms(load),fill="#986217",font=("Segoe UI",11,"bold"),tags="load")
            self.canvas.create_line(x+12,baseline-16,center-38,baseline-16,arrow="last",fill="#386cf5",width=2)
            self.canvas.create_text((x+12+center-38)/2,baseline-31,text="I de carga",fill="#386cf5",font=("Segoe UI",10))
        self.canvas.configure(scrollregion=(0,0,max(width+60,self.canvas.winfo_width()),max(full_height+48,self.canvas.winfo_height())))
