import tkinter as tk
from tkinter import ttk

class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg, controller=None):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.controller = controller
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", self._resize_inner_width)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _resize_inner_width(self, event):
        try:
            self.canvas.itemconfigure(self.window_id, width=event.width)
        except tk.TclError:
            pass

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass



class BasePage(tk.Frame):
    page_name = ""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.colors["bg"])
        self.controller = controller

    def make_card(self, parent, bg=None, padx=18, pady=18):
        return tk.Frame(parent, bg=bg or self.controller.colors["surface"], highlightbackground=self.controller.colors["border"], highlightthickness=1, bd=0, padx=padx, pady=pady)
