import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class AccordionController:
    """
    Keeps track of multiple CollapsibleSection instances and ensures
    only one is expanded at a time when expand() is requested.

    allow_all_closed=True -> user can collapse the currently open section,
    leaving all sections closed.
    """
    def __init__(self, allow_all_closed: bool = True):
        self.sections = []
        self.allow_all_closed = allow_all_closed

    def register(self, section: "CollapsibleSection"):
        if section not in self.sections:
            self.sections.append(section)

    def expand(self, target: "CollapsibleSection"):
        # collapse everyone else
        for s in self.sections:
            if s is not target:
                s.collapse()
        target.expand()

    def collapse_all(self):
        for s in self.sections:
            s.collapse()

    def expanded_sections(self):
        return [s for s in self.sections if s.expanded]


class CollapsibleSection:
    def __init__(self, parent, title, controller: AccordionController = None,
                 start_expanded: bool = False, **kwargs):
        self.parent = parent
        self.title = title
        self.controller = controller

        # Default padding if not provided
        if "padding" not in kwargs:
            kwargs["padding"] = 5

        # Outer frame with styling support
        self.frame = ttk.Frame(parent, **kwargs)

        # Button to expand/collapse
        self.toggle_button = ttk.Button(
            self.frame,
            text=f"▶ {title}",
            width=40,
            bootstyle="secondary-outline",
            command=self.toggle
        )
        self.toggle_button.pack(fill="x")

        # Frame that holds the content (initially hidden)
        self.sub_frame = ttk.Frame(self.frame, padding=(10, 5))
        self.expanded = False

        # Register with controller if provided
        if self.controller:
            self.controller.register(self)

        # Optionally start expanded (via controller if available)
        if start_expanded:
            if self.controller:
                self.controller.expand(self)
            else:
                self.expand()

    # --- Public control methods ---
    def expand(self):
        if not self.expanded:
            self.sub_frame.pack(fill="x", padx=10, pady=5)
            self.toggle_button.config(text=f"▼ {self.title}")
            self.expanded = True
            # Optional: fire a virtual event
            try:
                self.frame.event_generate("<<SectionExpanded>>")
            except Exception:
                pass

    def collapse(self):
        if self.expanded:
            self.sub_frame.forget()
            self.toggle_button.config(text=f"▶ {self.title}")
            self.expanded = False
            # Optional: fire a virtual event
            try:
                self.frame.event_generate("<<SectionCollapsed>>")
            except Exception:
                pass

    def toggle(self):
        if self.expanded:
            # If controller disallows "all closed", keep one open
            if self.controller and not self.controller.allow_all_closed:
                return
            self.collapse()
        else:
            if self.controller:
                self.controller.expand(self)
            else:
                self.expand()

    # --- Convenience passthroughs ---
    def add_to_subframe(self, widget, **kwargs):
        widget.grid(in_=self.sub_frame, **kwargs)

    def pack(self, **kwargs):
        kwargs.setdefault("padx", 5)
        kwargs.setdefault("pady", 5)
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        kwargs.setdefault("padx", 5)
        kwargs.setdefault("pady", 5)
        self.frame.grid(**kwargs)
