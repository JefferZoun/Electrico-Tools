"""Distribución adaptable compartida por ambas calculadoras."""


class ResponsiveLayoutMixin:
    def schedule_layout(self, event):
        if event.widget is self:
            if self._layout_job:
                self.after_cancel(self._layout_job)
            self._layout_job = self.after(40, self.apply_layout)

    def cleanup_layout(self, event):
        if event.widget is self and self._layout_job:
            self.after_cancel(self._layout_job)
            self._layout_job = None

    def apply_layout(self):
        self._layout_job = None
        width = self.winfo_width()
        height = self.winfo_height()
        has_xp_bar = hasattr(self.winfo_toplevel(), "xp_chrome")
        if has_xp_bar and height < 570:
            self.header.grid_remove()
        else:
            self.header.grid()
        if not hasattr(self, "_editor_heading"):
            self._editor_heading = self.editor.grid_slaves(row=0, column=0)[0]
        if has_xp_bar and height < 520:
            self._editor_heading.grid_remove()
        else:
            self._editor_heading.grid()
        short = self.winfo_height() < 650
        if short != self._short:
            self._short = short
            if short:
                self.subtitle.pack_forget()
                self.header.configure(padding=(14, 8))
            else:
                self.subtitle.pack(anchor="w", pady=(4, 0))
                self.header.configure(padding=(18, 12))
        compact = width < 920
        self.status_label.configure(wraplength=max(300, width-24))
        if compact == self._compact:
            return
        self._compact = compact
        if compact:
            self.editor.grid_forget()
            self.output.grid_forget()
            self.workspace.columnconfigure(1, weight=0)
            self.compact_tabs.add(self.editor, text="  Constructor  ")
            self.compact_tabs.add(self.output, text="  Resultado  ")
            self.compact_tabs.grid(row=0, column=0, columnspan=2, sticky="nsew")
        else:
            for tab in self.compact_tabs.tabs():
                self.compact_tabs.forget(tab)
            self.compact_tabs.grid_forget()
            self.workspace.columnconfigure(0, weight=4)
            self.workspace.columnconfigure(1, weight=5)
            self.editor.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            self.output.grid(row=0, column=1, sticky="nsew")
