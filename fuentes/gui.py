"""Calculadora gráfica de asociación de generadores de tensión continua."""
import tkinter as tk
from tkinter import messagebox, ttk
from electrico.layout import ResponsiveLayoutMixin
from .diagram import SourceDiagram
from .model import Generator, VOLTAGE_UNITS, associate, ohms, parse_number, volts


class SourcesApp(ResponsiveLayoutMixin, ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)
        self.generators = []
        self.counter = 0
        self.mode_var = tk.StringVar(value="serie")
        self.result_var = tk.StringVar(value="— V")
        self.load_var = tk.StringVar()
        self.current_var = tk.StringVar(value="I de carga: — A")
        self.internal_var = tk.StringVar(value="Resistencia interna: — Ω")
        self.status_var = tk.StringVar(value="Añade generadores. r = 0 Ω representa una fuente ideal.")
        self.form = self.new_form()
        self._build()
        self.refresh()

    def new_form(self, generator=None):
        return {
            "name": tk.StringVar(value=generator.name if generator else ""),
            "voltage": tk.StringVar(value=format(generator.voltage, ".17g") if generator else ""),
            "unit": tk.StringVar(value="V"),
            "resistance": tk.StringVar(value=format(generator.resistance, ".17g") if generator else "0"),
            "polarity": tk.StringVar(value="Inversa (−)" if generator and generator.polarity==-1 else "Normal (+)"),
        }

    def source_fields(self, frame, form):
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        for column, text in enumerate(("Nombre", "Tensión E", "Unidad")):
            ttk.Label(frame, text=text, style="Muted.TLabel").grid(row=0, column=column, sticky="w", pady=(0, 3))
        ttk.Entry(frame, textvariable=form["name"], width=10).grid(row=1, column=0, sticky="ew", padx=(0, 5))
        voltage_entry = ttk.Entry(frame, textvariable=form["voltage"], width=10)
        voltage_entry.grid(row=1, column=1, sticky="ew", padx=(0, 5))
        ttk.Combobox(frame, textvariable=form["unit"], values=list(VOLTAGE_UNITS), state="readonly", width=4).grid(row=1, column=2, sticky="ew")
        ttk.Label(frame, text="r interna (Ω)", style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(5, 3))
        ttk.Label(frame, text="Polaridad", style="Muted.TLabel").grid(row=2, column=1, columnspan=2, sticky="w", pady=(5, 3))
        ttk.Entry(frame, textvariable=form["resistance"], width=10).grid(row=3, column=0, sticky="ew", padx=(0, 5))
        ttk.Combobox(frame, textvariable=form["polarity"], values=("Normal (+)", "Inversa (−)"), state="readonly", width=12).grid(row=3, column=1, columnspan=2, sticky="ew")
        return voltage_entry

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.header = ttk.Frame(self, style="Header.TFrame", padding=(18,12))
        self.header.grid(row=0, column=0, sticky="ew", pady=(0,12))
        ttk.Label(self.header, text="⚡ ELECTRICO TOOLS · FUENTES", style="Brand.TLabel").pack(anchor="w")
        self.subtitle = ttk.Label(self.header, text="Fuentes de tensión, paso a paso", style="Header.TLabel")
        self.subtitle.pack(anchor="w", pady=(4,0))
        self.workspace = ttk.Frame(self)
        self.workspace.grid(row=1, column=0, sticky="nsew")
        self.workspace.rowconfigure(0, weight=1)
        self.workspace.columnconfigure((0,1), weight=1)
        self.compact_tabs = ttk.Notebook(self.workspace)
        self.editor = editor = ttk.Frame(self.workspace, style="Card.TFrame", padding=10)
        self.output = output = ttk.Frame(self.workspace, style="Card.TFrame", padding=10)
        editor.columnconfigure(0, weight=1)
        editor.rowconfigure(3, weight=1)
        output.columnconfigure(0, weight=1)
        output.rowconfigure(2, weight=1)
        ttk.Label(editor, text="01  Añade generadores", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0,6))
        entry = ttk.Frame(editor, style="Card.TFrame")
        entry.grid(row=1, column=0, sticky="ew")
        voltage_entry = self.source_fields(entry, self.form)
        voltage_entry.bind("<Return>", lambda event: self.add_source())
        ttk.Button(entry, text="+ Añadir generador", style="Accent.TButton", command=self.add_source).grid(row=4, column=0, columnspan=3, sticky="ew", pady=(6,0))
        connection = ttk.Frame(editor, style="Card.TFrame")
        connection.grid(row=2, column=0, sticky="ew", pady=6)
        connection.columnconfigure(1, weight=1)
        ttk.Label(connection, text="Conexión", style="Muted.TLabel").grid(row=0, column=0, padx=(0,8))
        mode = ttk.Combobox(connection, textvariable=self.mode_var, values=("serie","paralelo"), state="readonly", width=10)
        mode.grid(row=0, column=1, sticky="ew")
        mode.bind("<<ComboboxSelected>>", lambda event: self.change_mode())
        ttk.Label(connection,text="RL (Ω)",style="Muted.TLabel").grid(row=0,column=2,padx=(8,4))
        ttk.Entry(connection,textvariable=self.load_var,width=8).grid(row=0,column=3,sticky="ew")
        self.load_var.trace_add("write",lambda *args:self.load_changed())
        tree_frame = ttk.Frame(editor, style="Card.TFrame")
        tree_frame.grid(row=3, column=0, sticky="nsew")
        self.tree = ttk.Treeview(tree_frame, columns=("voltage","resistance"), selectmode="browse", height=3)
        self.tree.heading("#0", text="Generador")
        self.tree.heading("voltage", text="E · polaridad")
        self.tree.heading("resistance", text="r interna")
        self.tree.column("#0", width=100, minwidth=70)
        self.tree.column("voltage", width=100, minwidth=80, stretch=False)
        self.tree.column("resistance", width=96, minwidth=80, stretch=False)
        self.tree.tag_configure("normal", foreground="#0d9488")
        self.tree.tag_configure("inverse", foreground="#b5494d")
        scroll = ttk.Scrollbar(tree_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", lambda event: self.draw_sources())
        self.tree.bind("<Double-1>", lambda event: self.edit_selected())
        self.tree.bind("<Delete>", self.delete_from_keyboard)
        actions = ttk.Frame(editor, style="Card.TFrame")
        actions.grid(row=4, column=0, sticky="ew", pady=(6,0))
        actions.columnconfigure((0,1), weight=1)
        ttk.Button(actions, text="Editar", command=self.edit_selected).grid(row=0, column=0, sticky="ew", padx=(0,4))
        ttk.Button(actions, text="Eliminar · Supr", style="Danger.TButton", command=self.delete_selected).grid(row=0, column=1, sticky="ew")
        result = ttk.Frame(output, style="Result.TFrame", padding=(12,8))
        result.grid(row=0, column=0, sticky="ew")
        ttk.Label(result, text="02  TENSIÓN EQUIVALENTE EN VACÍO", style="ResultTitle.TLabel").pack(anchor="w")
        self.result_label = ttk.Label(result, textvariable=self.result_var, style="Result.TLabel", wraplength=400)
        self.result_label.pack(anchor="w", pady=(3,0))
        ttk.Label(result, textvariable=self.internal_var, style="ResultTitle.TLabel").pack(anchor="w", pady=(3,0))
        self.current_label=ttk.Label(result,textvariable=self.current_var,style="ResultTitle.TLabel",wraplength=400)
        self.current_label.pack(anchor="w",pady=(3,0))
        result.bind("<Configure>", lambda event: [label.configure(wraplength=max(200,event.width-24)) for label in (self.result_label,self.current_label)])
        bar = ttk.Frame(output, style="Card.TFrame")
        bar.grid(row=1, column=0, sticky="ew", pady=8)
        bar.columnconfigure(0, weight=1)
        ttk.Button(bar, text="Calcular asociación", style="Accent.TButton", command=self.compute).grid(row=0, column=0, sticky="ew", padx=(0,4))
        ttk.Button(bar, text="Ver pasos →", command=self.show_steps).grid(row=0, column=1)
        self.notebook = ttk.Notebook(output)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.diagram = SourceDiagram(self.notebook, self.select_from_diagram)
        self.diagram.canvas.bind("<Delete>", self.delete_from_keyboard)
        self.steps_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        guide_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.diagram,text="Esquema")
        self.notebook.add(self.steps_frame,text="Pasos")
        self.notebook.add(guide_frame,text="Fórmulas")
        self.explanation = self.make_text(self.steps_frame)
        self.explanation.tag_configure("heading",font=("Segoe UI",14,"bold"),foreground="#174b86",spacing1=12,spacing3=8)
        self.explanation.tag_configure("label",font=("Segoe UI",10,"bold"),foreground="#63748b",spacing1=5)
        self.explanation.tag_configure("formula",font=("Consolas",12),foreground="#243247",spacing3=6)
        self.explanation.tag_configure("result",font=("Segoe UI",12,"bold"),foreground="#166b58",background="#e5f3ed",spacing1=7,spacing3=8)
        guide = self.make_text(guide_frame)
        guide.insert("end", "GENERADORES DE TENSIÓN CONTINUA\n\nCada generador se modela como una fuente ideal E con una resistencia interna r en serie. r = 0 Ω significa ideal.\n\nSERIE\nEeq = E1 + E2 + … + En (con signos)\nreq = r1 + r2 + … + rn\n\nPARALELO · FUENTES REALES\nEeq = Σ(Ei/ri) / Σ(1/ri)\nreq = 1 / Σ(1/ri)\n\nPARALELO · FUENTES IDEALES\nTodas las fuentes ideales deben imponer la misma tensión y polaridad. Eeq es esa tensión y req = 0 Ω. Una fuente ideal puede coexistir con ramas reales de tensión diferente: su resistencia interna limita la corriente en esas ramas.\n\nPOLARIDAD\nNormal (+): E positiva, A a mayor tensión que B. Inversa (−): E negativa respecto de la misma referencia.\n\nCON UNA CARGA RL\nI = Eeq / (req + RL)\nVcarga = I × RL\n\nIntroduce RL en Ω para calcular la corriente de carga. Deja RL vacía para circuito abierto (I = 0 A); RL = 0 representa un cortocircuito y requiere resistencia interna positiva.\n\nLa herramienta calcula el equivalente y la corriente de carga de fuentes DC. No calcula capacidades en Ah ni asociaciones de fuentes de corriente o de corriente alterna. El pulso del esquema es decorativo.\n\nModelo educativo: OpenStax, University Physics 2, capítulos 10.1 y 10.3. Consulta el README para los enlaces.")
        guide.configure(state="disabled")
        self.bottom = bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, sticky="ew", pady=(10,0))
        bottom.columnconfigure(4, weight=1)
        ttk.Label(bottom,text="Ejemplos",style="Footer.TLabel").grid(row=0,column=0,padx=(0,4))
        for column, mode in enumerate(("Serie","Paralelo","Oposición"),1):
            ttk.Button(bottom,text=mode,command=lambda m=mode: self.load_example(m)).grid(row=0,column=column,padx=2)
        ttk.Button(bottom,text="Nuevo",command=self.reset).grid(row=0,column=5,padx=(4,0))
        self.status_label = ttk.Label(self,textvariable=self.status_var,style="Footer.TLabel",wraplength=900)
        self.status_label.grid(row=3,column=0,sticky="ew",pady=(6,0))
        self._compact = self._short = None
        self._layout_job = None
        self.bind("<Configure>",self.schedule_layout)
        self.bind("<Destroy>",self.cleanup_layout)
        self.set_explanation("Añade generadores y pulsa Calcular asociación para ver las fórmulas y los pasos.")

    def make_text(self, parent):
        text = tk.Text(parent,wrap="word",width=30,height=6,font=("Segoe UI",12),padx=16,pady=12,spacing1=3,spacing3=4,relief="flat",background="#f5f8fc",foreground="#243247")
        scroll = ttk.Scrollbar(parent,command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left",fill="both",expand=True)
        scroll.pack(side="right",fill="y")
        return text

    def selected(self):
        selection = self.tree.selection()
        return next((g for g in self.generators if selection and g.id==selection[0]), None)

    def read_form(self, form, default_name):
        return Generator(form["name"].get().strip() or default_name,
                         parse_number(form["voltage"].get(),VOLTAGE_UNITS[form["unit"].get()]),
                         parse_number(form["resistance"].get()),
                         -1 if form["polarity"].get()=="Inversa (−)" else 1)

    def add_source(self):
        try:
            generator = self.read_form(self.form,f"G{self.counter+1}")
        except ValueError as exc:
            messagebox.showerror("Valores no válidos",str(exc),parent=self.winfo_toplevel())
            return
        self.counter += 1
        self.generators.append(generator)
        self.form["name"].set("")
        self.form["voltage"].set("")
        self.refresh(generator.id)
        self.invalidate()

    def refresh(self, selected_id=None):
        self.tree.delete(*self.tree.get_children())
        for g in self.generators:
            self.tree.insert("","end",iid=g.id,text=g.name,values=(volts(g.emf),ohms(g.resistance)),tags=("normal" if g.polarity==1 else "inverse",))
        if selected_id and self.tree.exists(selected_id):
            self.tree.selection_set(selected_id)
            self.tree.focus(selected_id)
            self.tree.see(selected_id)
        self.draw_sources()

    def draw_sources(self):
        selected = self.selected()
        try:
            text=self.load_var.get().strip()
            load=parse_number(text) if text else None
        except ValueError:
            load=None
        self.diagram.set_sources(self.generators,self.mode_var.get(),selected.id if selected else None,load)

    def select_from_diagram(self, node_id):
        if self.tree.exists(node_id):
            self.tree.selection_set(node_id)
            self.tree.focus(node_id)
            self.tree.see(node_id)
            self.draw_sources()

    def load_changed(self):
        self.invalidate()
        self.draw_sources()

    def invalidate(self):
        self.diagram.stop_animation()
        self.result_var.set("Pendiente")
        self.current_var.set("I de carga: — A")
        self.internal_var.set("Resistencia interna: — Ω")
        self.set_explanation("La asociación ha cambiado. Pulsa Calcular para actualizar el equivalente.")

    def change_mode(self):
        self.draw_sources()
        self.invalidate()

    def delete_from_keyboard(self,event=None):
        self.delete_selected()
        return "break"

    def delete_selected(self):
        generator = self.selected()
        if generator:
            self.generators.remove(generator)
            self.refresh()
            self.invalidate()

    def edit_selected(self):
        generator = self.selected()
        if not generator:
            return
        dialog = tk.Toplevel(self)
        dialog.title("Editar generador")
        dialog.transient(self.winfo_toplevel())
        dialog.resizable(False,False)
        frame = ttk.Frame(dialog,style="Card.TFrame",padding=16)
        frame.pack(fill="both",expand=True)
        form = self.new_form(generator)
        self.source_fields(frame,form)
        def save():
            try:
                edited = self.read_form(form,generator.name)
            except ValueError as exc:
                messagebox.showerror("Valores no válidos",str(exc),parent=dialog)
                return
            generator.name,generator.voltage,generator.resistance,generator.polarity = edited.name,edited.voltage,edited.resistance,edited.polarity
            self.refresh(generator.id)
            self.invalidate()
            dialog.destroy()
        ttk.Button(frame,text="Guardar",style="Accent.TButton",command=save).grid(row=4,column=0,columnspan=2,sticky="ew",pady=(12,0))
        ttk.Button(frame,text="Cancelar",command=dialog.destroy).grid(row=4,column=2,pady=(12,0),padx=(5,0))
        dialog.bind("<Return>",lambda event: save())
        dialog.bind("<Escape>",lambda event: dialog.destroy())
        dialog.grab_set()

    def set_explanation(self,text):
        self.explanation.configure(state="normal")
        self.explanation.delete("1.0","end")
        for line in text.splitlines(keepends=True):
            stripped=line.strip()
            tag=""
            if stripped.startswith("Paso ") or stripped=="EQUIVALENTE FINAL":
                tag="heading"
            elif stripped in ("Componentes","Fórmula") or stripped.startswith("Sustitución"):
                tag="label"
            elif stripped.startswith("Resultado:"):
                tag="result"
            elif stripped.startswith(("Eeq =","req =")):
                tag="formula"
            self.explanation.insert("end",line,(tag,) if tag else ())
        self.explanation.yview_moveto(0)
        self.explanation.configure(state="disabled")

    def show_steps(self):
        if self._compact:
            self.compact_tabs.select(self.output)
        self.notebook.select(self.steps_frame)

    def compute(self):
        try:
            load_text = self.load_var.get().strip()
            load = parse_number(load_text) if load_text else None
            result = associate(self.generators,self.mode_var.get(),load)
        except ValueError as exc:
            self.result_var.set("Revisa los datos")
            self.internal_var.set("Sin equivalente válido")
            self.current_var.set("I de carga: — A")
            self.set_explanation(str(exc))
            if self._compact:
                self.compact_tabs.select(self.output)
            self.notebook.select(self.steps_frame)
            self.diagram.stop_animation()
            return
        self.result_var.set(volts(result.voltage))
        self.internal_var.set("Resistencia interna: "+ohms(result.resistance))
        self.current_var.set(f"I de carga: {result.current:.8g} A · Vbornes: {volts(result.terminal_voltage)}")
        self.set_explanation("\n\n".join(result.steps))
        self.status_var.set("RL vacía: circuito abierto (I = 0 A). RL en Ω: intensidad de carga.")
        if self._compact:
            self.compact_tabs.select(self.output)
        self.diagram.animate()

    def confirm_replace(self):
        return not self.generators or messagebox.askyesno("Reemplazar asociación","¿Reemplazar los generadores actuales?",parent=self.winfo_toplevel())

    def reset(self):
        if not self.confirm_replace():
            return
        self.generators=[]
        self.load_var.set("")
        self.counter=0
        self.mode_var.set("serie")
        self.refresh()
        self.result_var.set("— V")
        self.internal_var.set("Resistencia interna: — Ω")
        self.set_explanation("Añade generadores para comenzar.")

    def load_example(self, mode):
        if not self.confirm_replace():
            return
        self.mode_var.set("paralelo" if mode=="Paralelo" else "serie")
        if mode=="Paralelo":
            self.generators=[Generator("G1",12,1),Generator("G2",6,2)]
        elif mode=="Oposición":
            self.generators=[Generator("G1",12,0.5),Generator("G2",6,0.5,-1)]
        else:
            self.generators=[Generator("G1",12,0.5),Generator("G2",12,0.5)]
        self.load_var.set("10")
        self.counter=2
        self.refresh()
        self.compute()
