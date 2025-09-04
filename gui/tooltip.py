import tkinter as tk
import ttkbootstrap as ttk


class ToolTip:
    """
    Creates a tooltip for a given widget as the mouse hovers over it.
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        # Position the tooltip near the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tooltip_window = tw = tk.Toplevel(self.widget)

        # Remove window decorations
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw, text=self.text,
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def make_tooltip(parent, text, widget=None):
    """
    Helper function:
      - If widget is provided → attaches tooltip to it.
      - If no widget → creates a default ⓘ info icon in `parent` and attaches tooltip.
    
    Returns the widget so you can pack/grid/place it.
    """
    if widget is None:
        widget = ttk.Label(parent, text="ⓘ", cursor="question_arrow")
    ToolTip(widget, text)
    return widget
