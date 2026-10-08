"""Esquema serie/paralelo en Canvas, con selección y resaltado animado."""
import tkinter as tk
from tkinter import ttk
from .circuit import Group, Resistor, ohms


class CircuitDiagram(ttk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master, style="Card.TFrame")
        self.on_select = on_select
        self.node = None
        self.selected_id = None
        self.animation_job = None
        self.resize_job = None
        self.canvas = tk.Canvas(self, background="#eef4fc", highlightthickness=0, height=180)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview).grid(row=1, column=0, sticky="ew")
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=self._xscroll, yscrollcommand=vertical.set)
        self.horizontal = self.grid_slaves(row=1, column=0)[0]
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", self.schedule_draw)
        self.canvas.bind("<Button-1>", self.click)
        self.bind("<Destroy>", self.cleanup)

    def _xscroll(self, first, last):
        self.horizontal.set(first, last)

    def cleanup(self, event):
        if event.widget is self:
            self.stop_animation()
            if self.resize_job:
                self.after_cancel(self.resize_job)

    def schedule_draw(self, event=None):
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(60, self._redraw)

    def _redraw(self):
        self.resize_job = None
        self.draw()

    def set_circuit(self, node, selected_id):
        self.stop_animation()
        self.node, self.selected_id = node, selected_id
        self.draw()

    def measure(self, node):
        if isinstance(node, Resistor):
            return 166, 104
        if not node.children:
            return 210, 110
        dimensions = [self.measure(child) for child in node.children]
        if node.mode == "serie":
            return sum(w for w, h in dimensions) + 52, max(h for w, h in dimensions) + 54
        return max(w for w, h in dimensions) + 100, sum(h for w, h in dimensions) + 54

    def wire(self, *points):
        self.canvas.create_line(*points, fill="#6386a5", width=3, tags="wire")

    def draw_node(self, node, x, y):
        w, h = self.measure(node)
        cy = y + h / 2
        tag = "node:" + node.id
        if isinstance(node, Resistor):
            active = node.id == self.selected_id
            self.wire(x, cy, x + 36, cy)
            self.wire(x + w - 36, cy, x + w, cy)
            self.canvas.create_rectangle(x+36, cy-18, x+w-36, cy+18, fill="#fff1cc", outline="#e79f31" if not active else "#386cf5", width=3 if active else 2, tags=tag)
            points = [x+43, cy]
            for i in range(10):
                points.extend((x+48+i*7, cy+(-8 if i%2==0 else 8)))
            points.extend((x+w-43, cy))
            self.canvas.create_line(*points, fill="#925b13", width=2, tags=tag)
            self.canvas.create_text(x+w/2, cy-34, text=node.name, fill="#223958", font=("Segoe UI", 11, "bold"), tags=tag)
            self.canvas.create_text(x+w/2, cy+34, text=ohms(node.value), fill="#526884", font=("Segoe UI", 10), tags=tag)
            return
        color = "#386cf5" if node.mode == "serie" else "#0d9488"
        self.canvas.create_rectangle(x+8, y+5, x+w-8, y+h-5, outline=color, width=2 if node.id==self.selected_id else 1, dash=(4,4), tags=tag)
        self.canvas.create_text(x+20, y+18, anchor="w", text=f"{node.name} · {node.mode}", fill=color, font=("Segoe UI", 10, "bold"), tags=tag)
        if not node.children:
            self.canvas.create_text(x+w/2, cy+10, text="Añade componentes", fill="#8394aa", tags=tag)
            return
        dimensions = [self.measure(child) for child in node.children]
        if node.mode == "serie":
            cursor = x+26
            self.wire(x, cy, cursor, cy)
            for child, (cw, ch) in zip(node.children, dimensions):
                self.draw_node(child, cursor, cy-ch/2)
                cursor += cw
            self.wire(cursor, cy, x+w, cy)
        else:
            left, right = x+34, x+w-34
            centers = []
            cursor = y+27
            for child, (cw, ch) in zip(node.children, dimensions):
                center = cursor+ch/2
                centers.append(center)
                self.wire(left, center, x+50, center)
                self.draw_node(child, x+50, cursor)
                self.wire(x+50+cw, center, right, center)
                cursor += ch
            self.wire(left, centers[0], left, centers[-1])
            self.wire(right, centers[0], right, centers[-1])
            self.wire(x, cy, left, cy)
            self.wire(right, cy, x+w, cy)

    def draw(self):
        self.canvas.delete("all")
        if self.node is None:
            return
        w, h = self.measure(self.node)
        x = max(30, (self.canvas.winfo_width()-w)/2)
        y = max(24, (self.canvas.winfo_height()-h)/2)
        self.draw_node(self.node, x, y)
        self.canvas.create_oval(x-5, y+h/2-5, x+5, y+h/2+5, fill="#386cf5", outline="")
        self.canvas.create_oval(x+w-5, y+h/2-5, x+w+5, y+h/2+5, fill="#0d9488", outline="")
        # Mantén las etiquetas legibles: los circuitos grandes se desplazan.
        self.canvas.configure(scrollregion=(0, 0, max(w+60, self.canvas.winfo_width()), max(h+48, self.canvas.winfo_height())))

    def click(self, event):
        self.canvas.focus_set()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        for item in reversed(self.canvas.find_overlapping(x-3, y-3, x+3, y+3)):
            for tag in self.canvas.gettags(item):
                if tag.startswith("node:"):
                    self.on_select(tag[5:])
                    return

    def stop_animation(self):
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        if self.canvas.winfo_exists():
            self.canvas.itemconfigure("wire", fill="#6386a5", width=3)

    def animate(self):
        """Pulso decorativo de conexiones; no representa una simulación de corriente."""
        self.stop_animation()
        def tick(frame=0):
            if frame >= 18:
                self.animation_job = None
                self.canvas.itemconfigure("wire", fill="#6386a5", width=3)
                return
            self.canvas.itemconfigure("wire", fill=("#386cf5", "#24b7a5", "#e9ad45")[frame//3%3], width=4)
            self.animation_job = self.after(65, tick, frame+1)
        tick()
