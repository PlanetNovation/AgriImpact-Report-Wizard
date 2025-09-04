import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class SidebarNavigator(ttk.Frame):
    def __init__(self, parent, pages, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pages = pages
        self.page_names = list(pages.keys())
        self.current_page = None
        self.current_index = 0

        # --- Sidebar ---
        self.sidebar = ttk.Frame(self, padding=20, width=200, bootstyle="secondary")
        self.sidebar.pack(side="left", fill="y")

        # Prepare a style for arrow labels that uses the same background as the sidebar
        self._setup_arrow_style()

        # === NEW: an inner frame that will be centered vertically ===
        self.sidebar_stack = ttk.Frame(
            self.sidebar,
            style=self.sidebar.cget("style")  # match background with sidebar
        )
        # expand=True gives it the extra vertical space; not filling Y keeps it centered
        self.sidebar_stack.pack(side="top", fill="x", expand=True)  # <<<

        # --- Content Area ---
        self.content_area = ttk.Frame(self)
        self.content_area.pack(side="top", fill="both", expand=True)

        # Add buttons for each page with arrows in between
        self.sidebar_buttons = {}
        for i, name in enumerate(self.pages.keys()):
            btn = ttk.Button(
                self.sidebar_stack,   # <<< parent is the centered inner frame
                text=name,
                bootstyle="secondary",
            )
            btn.pack(fill="x", pady=0)
            self.sidebar_buttons[name] = btn

            if i < len(self.pages) - 1:
                arrow = ttk.Label(
                    self.sidebar_stack,   # <<< parent is the centered inner frame
                    text="↓",
                    font=("Segoe UI", 12),
                    style="Sidebar.Arrow.TLabel",
                    anchor="center",
                )
                arrow.pack(padx=0, pady=0)

        # --- Bottom full-width navigation buttons ---
        bottom_nav = ttk.Frame(self)
        bottom_nav.pack(side="bottom", fill="x", pady=5)

        self.prev_btn = ttk.Button(bottom_nav, text="Previous", command=self.go_previous)
        self.prev_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.next_btn = ttk.Button(bottom_nav, text="Next", command=self.go_next)
        self.next_btn.pack(side="right", expand=True, fill="x", padx=5)

        # Keep arrows in sync if theme changes at runtime
        self.bind_all("<<ThemeChanged>>", self._setup_arrow_style)

        # Load the first page by default
        self.show_page(self.page_names[0])

    def _setup_arrow_style(self, *_):
        style = ttk.Style()
        sidebar_style = self.sidebar.cget("style") or "TFrame"
        sidebar_bg = style.lookup(sidebar_style, "background")
        style.configure("Sidebar.Arrow.TLabel", background=sidebar_bg)

    def show_page(self, name):
        if self.current_page is not None:
            self.current_page.destroy()

        if name in self.page_names:
            self.current_index = self.page_names.index(name)

        page_factory = self.pages[name]
        self.current_page = page_factory(self.content_area)
        self.current_page.pack(fill="both", expand=True)

        for btn_name, btn in self.sidebar_buttons.items():
            btn.config(bootstyle="primary" if btn_name == name else "secondary")

        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.prev_btn.config(state="disabled" if self.current_index == 0 else "normal")
        self.next_btn.config(state="disabled" if self.current_index == len(self.page_names) - 1 else "normal")

    def go_previous(self):
        if self.current_index > 0:
            self.show_page(self.page_names[self.current_index - 1])

    def go_next(self):
        if self.current_index < len(self.page_names) - 1:
            self.show_page(self.page_names[self.current_index + 1])
