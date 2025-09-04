import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.collapsible_section import CollapsibleSection, AccordionController
from gui.mouse_scroll import enable_mouse_scroll
from gui.tooltip import make_tooltip


def create_edit_frame(parent, data):
    """
    Create a reusable frame for editing wizard data.
    Can be embedded in any parent (root, notebook tab, sidebar, etc.).
    """
    frame = ttk.Frame(parent)

    # --- Scrollable canvas ---
    canvas = ttk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview, bootstyle="secondary")
    scroll_frame = ttk.Frame(canvas, padding=10)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    enable_mouse_scroll(canvas, scrollbar)

    # --- Group items by category ---
    items = list(data["items"].items())
    grouped = {}
    for key, item in items:
        category = item.get("category", "Uncategorized")
        grouped.setdefault(category, []).append((key, item))

    # --- Desired order of categories. Above items are shown first ---
    category_order = [
        "Land Use",
        "Crop Production",
        "Greenhouse Farming",
        "Livestock",
        "Revenue, Market Value, and Direct Sales",
        "Workforce",
        "Sustainability",
        "Types of Farms",
        "Other",
    ]

    # Sort grouped categories
    sorted_categories = sorted(
        grouped.items(),
        key=lambda x: category_order.index(x[0]) if x[0] in category_order else len(category_order)
    )

    # --- Accordion controller: one-open-at-a-time behavior on expand ---
    # Set allow_all_closed=False if you want exactly one open at all times.
    controller = AccordionController(allow_all_closed=True)

    # --- Display cards ---
    columns = 3
    row = 0
    col = 0

    for category, section_items in sorted_categories:
        section = CollapsibleSection(
            scroll_frame,
            category,
            relief="raised",
            padding=10,
            controller=controller,
            # start_expanded=True  # optionally start one open; better to set after loop
        )
        section.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # --- Add header row ---
        header_style = {"font": ("Segoe UI", 9, "bold")}
        ttk.Label(section.sub_frame, text="Name", **header_style).grid(row=0, column=0, padx=5, pady=(0,5), sticky="e")
        ttk.Label(section.sub_frame, text="Value", **header_style).grid(row=0, column=2, padx=5, pady=(0,5), sticky="w")
        ttk.Label(section.sub_frame, text="Date Saved", **header_style).grid(row=0, column=3, padx=5, pady=(0,5), sticky="w")
        ttk.Label(section.sub_frame, text="Quality", **header_style).grid(row=0, column=4, padx=5, pady=(0,5), sticky="w")

        # Fill the section content
        for i, (key, item) in enumerate(section_items, start=1):
            label = ttk.Label(section.sub_frame, text=item.get("title", key), font=("Segoe UI", 10))
            entry = ttk.Label(
                section.sub_frame, 
                width=15, 
                bootstyle="info", 
                text=str(item["value"]) if item["value"] is not None else ""
            )

            label.grid(row=i, column=0, sticky="e", pady=2, padx=5)

            tooltip_text = item.get("description")
            if tooltip_text:  # only add icon if there is a description
                info_icon = make_tooltip(section.sub_frame, tooltip_text)
                info_icon.grid(row=i, column=1, padx=2)

            entry.grid(row=i, column=2, pady=2, padx=5)

            # Read-only info labels
            date_applied = item.get("date_value_was_applied", "N/A")
            quality = item.get("quality", "N/A")

            date_label = ttk.Label(section.sub_frame, text=str(date_applied), font=("Segoe UI", 9))
            quality_label = ttk.Label(section.sub_frame, text=str(quality), font=("Segoe UI", 9))

            date_label.grid(row=i, column=3, pady=2, padx=5, sticky="w")
            quality_label.grid(row=i, column=4, pady=2, padx=5, sticky="w")

        # Move to next grid position
        col += 1
        if col >= columns:
            col = 0
            row += 1

    # Make columns expand evenly
    for c in range(columns):
        scroll_frame.columnconfigure(c, weight=1)

    # Optional: open the first section by default (use controller to enforce accordion)
    # if controller.sections:
    #     controller.expand(controller.sections[0])

    return frame
