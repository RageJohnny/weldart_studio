import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.schedule_hide)

    def schedule_show(self, event):
        self.cancel_hide()
        self.show_id = self.widget.after(300, self.show_tooltip, event)

    def schedule_hide(self, event):
        self.cancel_show()
        self.hide_id = self.widget.after(300, self.hide_tooltip)

    def cancel_show(self):
        if hasattr(self, 'show_id'):
            self.widget.after_cancel(self.show_id)
            del self.show_id

    def cancel_hide(self):
        if hasattr(self, 'hide_id'):
            self.widget.after_cancel(self.hide_id)
            del self.hide_id

    def show_tooltip(self, event):
        self.cancel_hide()
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self):
        self.cancel_show()
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()