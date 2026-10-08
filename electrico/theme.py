"""Tema visual compartido por las calculadoras."""
from tkinter import ttk


def configure_theme(root):
    root.configure(background="#e8eef8")
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("TFrame", background="#e8eef8")
    style.configure("Card.TFrame", background="white")
    style.configure("Header.TFrame", background="#17375d")
    style.configure("Result.TFrame", background="#e3f5ef")
    style.configure("TLabel", background="white", foreground="#243247", font=("Segoe UI", 10))
    style.configure("Brand.TLabel", background="#17375d", foreground="#7de1d1", font=("Segoe UI", 11, "bold"))
    style.configure("Header.TLabel", background="#17375d", foreground="white", font=("Segoe UI", 20, "bold"))
    style.configure("Section.TLabel", background="white", foreground="#386cf5", font=("Segoe UI", 13, "bold"))
    style.configure("Muted.TLabel", background="white", foreground="#63748b")
    style.configure("Footer.TLabel", background="#e8eef8", foreground="#526884", font=("Segoe UI", 9))
    style.configure("ResultTitle.TLabel", background="#e3f5ef", foreground="#387f70", font=("Segoe UI", 9, "bold"))
    style.configure("Result.TLabel", background="#e3f5ef", foreground="#126c59", font=("Segoe UI", 24, "bold"))
    style.configure("TButton", font=("Segoe UI", 10), padding=(8, 6), background="#edf2fc", foreground="#345071", borderwidth=0)
    style.map("TButton", background=[("active", "#dbe7fc"), ("pressed", "#cbdaf5")])
    for name, bg, fg, hover in (
        ("Accent", "#386cf5", "white", "#2856d3"),
        ("Blue", "#e7eeff", "#2856d3", "#d3dfff"),
        ("Teal", "#e3f5ef", "#126c59", "#cceee2"),
        ("Danger", "#fff0ef", "#b5494d", "#fbdcda"),
    ):
        style.configure(name+".TButton", background=bg, foreground=fg, padding=(8, 7), borderwidth=0)
        style.map(name+".TButton", background=[("active", hover), ("pressed", hover)])
    style.configure("TEntry", padding=6, fieldbackground="#f6f8fd", bordercolor="#dce5f2")
    style.configure("TCombobox", padding=5, fieldbackground="#f6f8fd")
    style.configure("TNotebook", background="#e8eef8", borderwidth=0)
    style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(12, 8), background="#e8eef8", foreground="#63748b")
    style.map("TNotebook.Tab", background=[("selected", "#386cf5")], foreground=[("selected", "white")])
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=30, background="white", fieldbackground="white", borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#edf2fc", foreground="#526884", padding=6)
    style.map("Treeview", background=[("selected", "#dce8ff")], foreground=[("selected", "#204da6")])
