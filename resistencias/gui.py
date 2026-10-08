"""Interfaz Tkinter para construir y calcular circuitos por grupos."""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .circuit import Group, Resistor, UNITS, calculate, ohms, parse_resistance
from .diagram import CircuitDiagram
from electrico.theme import configure_theme
from electrico.layout import ResponsiveLayoutMixin


class CalculatorApp(ResponsiveLayoutMixin, ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)
        self.root_group = Group("Circuito", "serie")
        self.nodes = {}
        self.counter = 0
        self.group_counter = 0
        self.name_var = tk.StringVar()
        self.value_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="Ω")
        self.mode_var = tk.StringVar(value="serie")
        self.result_var = tk.StringVar(value="— Ω")
        self.status_var = tk.StringVar(value="Selecciona un grupo para añadir componentes dentro de él.")
        self._build()
        self.refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.header = header = ttk.Frame(self, style="Header.TFrame", padding=(18, 12))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(header, text="⚡ ELECTRICO TOOLS", style="Brand.TLabel").pack(anchor="w")
        self.subtitle = ttk.Label(header, text="Tu circuito, paso a paso", style="Header.TLabel")
        self.subtitle.pack(anchor="w", pady=(4, 0))
        self.workspace = ttk.Frame(self)
        self.workspace.grid(row=1, column=0, sticky="nsew")
        self.workspace.rowconfigure(0, weight=1)
        self.workspace.columnconfigure(0, weight=1)
        self.workspace.columnconfigure(1, weight=1)
        self.compact_tabs = ttk.Notebook(self.workspace)
        self.editor = editor = ttk.Frame(self.workspace, style="Card.TFrame", padding=12)
        self.output = output = ttk.Frame(self.workspace, style="Card.TFrame", padding=12)
        editor.columnconfigure(0, weight=1)
        editor.rowconfigure(3, weight=1)
        output.columnconfigure(0, weight=1)
        output.rowconfigure(2, weight=1)
        ttk.Label(editor, text="01  Construye el circuito", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        entry = ttk.Frame(editor, style="Card.TFrame")
        entry.grid(row=1, column=0, sticky="ew")
        for column in (0, 1):
            entry.columnconfigure(column, weight=1)
        for column, label in enumerate(("Nombre", "Valor", "Unidad")):
            ttk.Label(entry, text=label, style="Muted.TLabel").grid(row=0, column=column, sticky="w", pady=(0, 4))
        ttk.Entry(entry, textvariable=self.name_var, width=10).grid(row=1, column=0, sticky="ew", padx=(0, 6))
        value_entry = ttk.Entry(entry, textvariable=self.value_var, width=12)
        value_entry.grid(row=1, column=1, sticky="ew", padx=(0, 6))
        value_entry.bind("<Return>", lambda event: self.add_resistor())
        ttk.Combobox(entry, textvariable=self.unit_var, values=list(UNITS), state="readonly", width=5).grid(row=1, column=2, sticky="ew")
        ttk.Button(entry, text="+ Añadir resistencia", style="Accent.TButton", command=self.add_resistor).grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        toolbar = ttk.Frame(editor, style="Card.TFrame")
        toolbar.grid(row=2, column=0, sticky="ew", pady=8)
        toolbar.columnconfigure((0, 1), weight=1)
        ttk.Button(toolbar, text="+ Grupo serie", style="Blue.TButton", command=lambda: self.add_group("serie")).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(toolbar, text="+ Grupo paralelo", style="Teal.TButton", command=lambda: self.add_group("paralelo")).grid(row=0, column=1, sticky="ew")
        tree_frame = ttk.Frame(editor, style="Card.TFrame")
        tree_frame.grid(row=3, column=0, sticky="nsew")
        self.tree = ttk.Treeview(tree_frame, columns=("value",), selectmode="browse", height=4)
        self.tree.heading("#0", text="Componentes")
        self.tree.heading("value", text="Valor")
        self.tree.column("#0", width=200, minwidth=100)
        self.tree.column("value", width=106, minwidth=80, stretch=False)
        self.tree.tag_configure("serie", foreground="#386cf5")
        self.tree.tag_configure("paralelo", foreground="#0d9488")
        self.tree.tag_configure("resistor", foreground="#986217")
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda event: self.edit_selected())
        self.tree.bind("<Delete>", self.delete_from_keyboard)
        actions = ttk.Frame(editor, style="Card.TFrame")
        actions.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        actions.columnconfigure((0, 1), weight=1)
        ttk.Button(actions, text="Editar", command=self.edit_selected).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(actions, text="Eliminar · Supr", style="Danger.TButton", command=self.delete_selected).grid(row=0, column=1, sticky="ew")
        ttk.Label(actions, text="Conexión del grupo", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.mode_box = ttk.Combobox(actions, textvariable=self.mode_var, values=("serie", "paralelo"), state="readonly", width=10)
        self.mode_box.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        self.mode_box.bind("<<ComboboxSelected>>", self.change_mode)
        result_card = ttk.Frame(output, style="Result.TFrame", padding=(14, 10))
        result_card.grid(row=0, column=0, sticky="ew")
        result_card.columnconfigure(0, weight=1)
        ttk.Label(result_card, text="02  RESISTENCIA EQUIVALENTE", style="ResultTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.result_label = ttk.Label(result_card, textvariable=self.result_var, style="Result.TLabel", wraplength=400)
        self.result_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        result_card.bind("<Configure>", lambda event: self.result_label.configure(wraplength=max(200, event.width-28)))
        calculate_bar = ttk.Frame(output, style="Card.TFrame")
        calculate_bar.grid(row=1, column=0, sticky="ew", pady=10)
        calculate_bar.columnconfigure(0, weight=1)
        ttk.Button(calculate_bar, text="Calcular circuito", style="Accent.TButton", command=self.compute).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(calculate_bar, text="Ver pasos →", command=self.show_steps).grid(row=0, column=1)
        self.notebook = notebook = ttk.Notebook(output)
        notebook.grid(row=2, column=0, sticky="nsew")
        self.diagram = CircuitDiagram(notebook, self.select_from_diagram)
        self.diagram.canvas.bind("<Delete>", self.delete_from_keyboard)
        self.steps_frame = text_frame = ttk.Frame(notebook, style="Card.TFrame")
        guide_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(self.diagram, text="Esquema")
        notebook.add(text_frame, text="Pasos")
        notebook.add(guide_frame, text="Fórmulas")
        self.explanation = tk.Text(text_frame, wrap="word", width=30, height=6, font=("Segoe UI", 12), padx=16, pady=12, spacing1=3, spacing3=4, relief="flat", background="#f5f8fc", foreground="#243247", state="disabled")
        self.explanation.tag_configure("heading", font=("Segoe UI", 14, "bold"), foreground="#174b86", spacing1=12, spacing3=8)
        self.explanation.tag_configure("label", font=("Segoe UI", 10, "bold"), foreground="#63748b", spacing1=5)
        self.explanation.tag_configure("formula", font=("Consolas", 12), foreground="#243247", lmargin1=8, lmargin2=8, spacing3=6)
        self.explanation.tag_configure("result", font=("Segoe UI", 12, "bold"), foreground="#166b58", background="#e5f3ed", spacing1=7, spacing3=10)
        self.explanation.tag_configure("note", foreground="#63748b", font=("Segoe UI", 10))
        text_scroll = ttk.Scrollbar(text_frame, command=self.explanation.yview)
        self.explanation.configure(yscrollcommand=text_scroll.set)
        self.explanation.pack(side="left", fill="both", expand=True)
        text_scroll.pack(side="right", fill="y")
        guide = tk.Text(guide_frame, wrap="word", width=30, height=6, font=("Segoe UI", 11), padx=16, pady=12, relief="flat", background="#f5f8fc", foreground="#243247")
        guide.tag_configure("title", font=("Segoe UI", 13, "bold"), foreground="#386cf5", spacing1=10, spacing3=6)
        guide.tag_configure("formula", font=("Consolas", 12), foreground="#0d9488", spacing1=6, spacing3=12)
        guide_scroll = ttk.Scrollbar(guide_frame, command=guide.yview)
        guide.configure(yscrollcommand=guide_scroll.set)
        guide.pack(side="left", fill="both", expand=True)
        guide_scroll.pack(side="right", fill="y")
        for title, description, formula in (
            ("Serie", "Suma todas las resistencias.", "Req = R1 + R2 + … + Rn"),
            ("Paralelo", "Suma los inversos y toma el inverso de la suma.", "Req = 1 / (1/R1 + … + 1/Rn)"),
            ("Dos en paralelo", "Divide el producto entre la suma.", "Req = (R1 × R2) / (R1 + R2)"),
            ("Mixto", "Resuelve primero los grupos interiores. Usa su resultado como resistencia del grupo exterior.", "100 Ω + (200 Ω ∥ 300 Ω) = 220 Ω"),
        ):
            guide.insert("end", title+"\n", "title")
            guide.insert("end", description+"\n")
            guide.insert("end", formula+"\n\n", "formula")
        guide.insert("end", "Req = resistencia equivalente. Una rama de 0 Ω en paralelo produce 0 Ω.\n\nEl esquema usa símbolos eléctricos; el pulso de color es decorativo y no simula corriente.")
        guide.configure(state="disabled")
        self.bottom = bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(4, weight=1)
        ttk.Label(bottom, text="Ejemplos", style="Footer.TLabel").grid(row=0, column=0, padx=(0, 6))
        for column, mode in enumerate(("serie", "paralelo", "mixto"), 1):
            ttk.Button(bottom, text=mode.capitalize(), command=lambda m=mode: self.load_example(m)).grid(row=0, column=column, padx=2)
        ttk.Button(bottom, text="Nuevo", command=self.reset).grid(row=0, column=5, padx=(6, 0))
        self.status_label = ttk.Label(self, textvariable=self.status_var, style="Footer.TLabel", wraplength=900)
        self.status_label.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        self._short = None
        self._compact = None
        self._layout_job = None
        self.bind("<Configure>", self.schedule_layout)
        self.bind("<Destroy>", self.cleanup_layout)
        self.set_explanation("Añade resistencias y pulsa Calcular. Aquí encontrarás la resolución de cada grupo.")

    def show_steps(self):
        if self._compact:
            self.compact_tabs.select(self.output)
        self.notebook.select(self.steps_frame)

    def select_from_diagram(self, node_id):
        if node_id in self.nodes:
            self.tree.selection_set(node_id)
            self.tree.focus(node_id)
            self.tree.see(node_id)
            self.on_select()

    def selected(self):
        selection = self.tree.selection()
        return self.nodes.get(selection[0], self.root_group) if selection else self.root_group

    def parent_of(self, target, group=None):
        group = group or self.root_group
        for child in group.children:
            if child.id == target.id:
                return group
            if isinstance(child, Group):
                parent = self.parent_of(target, child)
                if parent is not None:
                    return parent
        return None

    def destination(self):
        node = self.selected()
        return node if isinstance(node, Group) else self.parent_of(node)

    def refresh(self, select_id=None):
        self.tree.delete(*self.tree.get_children())
        self.nodes = {}

        def insert(node, parent=""):
            self.nodes[node.id] = node
            label = f"{node.name} [{node.mode.upper()}]" if isinstance(node, Group) else node.name
            self.tree.insert(parent, "end", iid=node.id, text=label, values=("" if isinstance(node, Group) else ohms(node.value),), tags=(node.mode if isinstance(node, Group) else "resistor",), open=True)
            if isinstance(node, Group):
                for child in node.children:
                    insert(child, node.id)
        insert(self.root_group)
        selected_id = select_id if select_id in self.nodes else self.root_group.id
        self.tree.selection_set(selected_id)
        self.tree.focus(selected_id)
        self.tree.see(selected_id)
        self.on_select()

    def on_select(self, event=None):
        node = self.selected()
        if isinstance(node, Group):
            self.mode_box.configure(state="readonly")
            self.mode_var.set(node.mode)
        else:
            self.mode_box.configure(state="disabled")
        group = self.destination()
        self.status_var.set(f"Destino: {group.name} · {group.mode}. Supr elimina la selección.")
        self.diagram.set_circuit(self.root_group, node.id)

    def invalidate(self):
        self.diagram.stop_animation()
        self.result_var.set("Pendiente de calcular")
        self.set_explanation("Pulsa «Calcular circuito» para actualizar el resultado y los pasos.")

    def set_explanation(self, text):
        self.explanation.configure(state="normal")
        self.explanation.delete("1.0", "end")
        for line in text.splitlines(keepends=True):
            stripped = line.strip()
            tag = ""
            if stripped.startswith("Paso "):
                tag = "heading"
            elif stripped in ("Componentes de este grupo", "Fórmula", "Sustituimos los valores en ohmios"):
                tag = "label"
            elif stripped.startswith("Req ="):
                tag = "formula"
            elif stripped.startswith(("Resultado del grupo:", "RESULTADO TOTAL:")):
                tag = "result"
            elif stripped.startswith("Todos los valores"):
                tag = "note"
            self.explanation.insert("end", line, (tag,) if tag else ())
        self.explanation.yview_moveto(0)
        self.explanation.configure(state="disabled")

    def add_resistor(self):
        try:
            value = parse_resistance(self.value_var.get(), self.unit_var.get())
        except ValueError as exc:
            messagebox.showerror("Valor no válido", str(exc), parent=self.winfo_toplevel())
            return
        self.counter += 1
        name = self.name_var.get().strip() or f"R{self.counter}"
        group = self.destination()
        group.children.append(Resistor(name, value))
        self.name_var.set("")
        self.value_var.set("")
        self.refresh(group.id)
        self.invalidate()

    def add_group(self, mode):
        self.group_counter += 1
        group = Group(f"G{self.group_counter}", mode)
        self.destination().children.append(group)
        self.refresh(group.id)
        self.invalidate()

    def change_mode(self, event=None):
        node = self.selected()
        if isinstance(node, Group):
            node.mode = self.mode_var.get()
            self.refresh(node.id)
            self.invalidate()

    def edit_selected(self):
        node = self.selected()
        if isinstance(node, Resistor):
            text = simpledialog.askstring("Editar resistencia", "Nuevo valor en Ω (admite coma decimal):", initialvalue=format(node.value, ".17g"), parent=self.winfo_toplevel())
            if text is None:
                return
            try:
                value = parse_resistance(text)
            except ValueError as exc:
                messagebox.showerror("Valor no válido", str(exc), parent=self.winfo_toplevel())
                return
        name = simpledialog.askstring("Nombre", "Nombre del componente:", initialvalue=node.name, parent=self.winfo_toplevel())
        if name is None:
            return
        if not name.strip():
            messagebox.showerror("Nombre no válido", "El nombre no puede estar vacío.", parent=self.winfo_toplevel())
            return
        node.name = name.strip()
        if isinstance(node, Resistor):
            node.value = value
        self.refresh(node.id)
        self.invalidate()

    def delete_from_keyboard(self, event=None):
        """Supr/Del sólo elimina cuando el árbol tiene el foco y hay selección."""
        if self.tree.selection():
            self.delete_selected()
        return "break"

    def delete_selected(self):
        node = self.selected()
        if node is self.root_group:
            messagebox.showinfo("Circuito", "Para vaciar el circuito, pulsa «Nuevo circuito».", parent=self.winfo_toplevel())
            return
        if isinstance(node, Group) and node.children:
            if not messagebox.askyesno("Eliminar grupo", "¿Eliminar el grupo y todos sus componentes?", parent=self.winfo_toplevel()):
                return
        parent = self.parent_of(node)
        parent.children.remove(node)
        self.refresh(parent.id)
        self.invalidate()

    def compute(self):
        try:
            result = calculate(self.root_group)
        except ValueError as exc:
            self.result_var.set("Revisa el circuito")
            self.set_explanation(str(exc))
            messagebox.showerror("No se puede calcular", str(exc), parent=self.winfo_toplevel())
            return
        self.result_var.set(ohms(result.value))
        steps = [f"Paso {i} · {step}" for i, step in enumerate(result.steps, 1)]
        self.set_explanation("\n\n".join(steps) + f"\n\nRESULTADO TOTAL: {ohms(result.value)}\n\nTodos los valores se convierten a ohmios antes del cálculo.")
        self.status_var.set("Cálculo listo · explora el esquema o pulsa Ver pasos.")
        if self._compact:
            self.compact_tabs.select(self.output)
        self.diagram.animate()

    def confirm_replace(self):
        return not self.root_group.children or messagebox.askyesno("Reemplazar circuito", "¿Reemplazar el circuito actual?", parent=self.winfo_toplevel())

    def reset(self):
        if not self.confirm_replace():
            return
        self.root_group = Group("Circuito", "serie")
        self.counter = self.group_counter = 0
        self.refresh()
        self.result_var.set("— Ω")
        self.set_explanation("")

    def load_example(self, mode):
        if not self.confirm_replace():
            return
        if mode == "mixto":
            self.root_group = Group("Circuito", "serie", [Resistor("R1", 100), Group("G1", "paralelo", [Resistor("R2", 200), Resistor("R3", 300)])])
            self.counter, self.group_counter = 3, 1
        else:
            self.root_group = Group("Circuito", mode, [Resistor("R1", 100), Resistor("R2", 200), Resistor("R3", 300)])
            self.counter, self.group_counter = 3, 0
        self.refresh()
        self.compute()


def main():
    root = tk.Tk()
    root.title("Electrico Tools · Calculadora de resistencias")
    screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{min(1160, screen_w-80)}x{min(780, screen_h-100)}")
    root.minsize(480, 540)
    configure_theme(root)
    CalculatorApp(root)
    root.mainloop()
