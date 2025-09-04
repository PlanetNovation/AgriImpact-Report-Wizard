def enable_mouse_scroll(canvas, scrollbar):
    """
    Enable scrolling of a ttk Canvas with the mouse wheel.
    Hides scrollbar when not needed.
    """

    def update_scrollbar():
        # Get bounding box of all content inside canvas
        bbox = canvas.bbox("all")
        if not bbox:
            return

        x1, y1, x2, y2 = bbox
        content_height = y2 - y1
        visible_height = canvas.winfo_height()

        if content_height > visible_height:
            # Show scrollbar if hidden
            if not scrollbar.winfo_ismapped():
                scrollbar.pack(side="right", fill="y")
        else:
            # Hide scrollbar if content fits
            if scrollbar.winfo_ismapped():
                scrollbar.pack_forget()

    def _on_mousewheel(event):
        update_scrollbar()

        bbox = canvas.bbox("all")
        if not bbox:
            return

        x1, y1, x2, y2 = bbox
        content_height = y2 - y1
        visible_height = canvas.winfo_height()

        if content_height <= visible_height:
            return  # nothing to scroll

        # Normal scrolling
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Bind mousewheel
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Also check when canvas resizes
    canvas.bind("<Configure>", lambda e: update_scrollbar())

    # Initial check
    update_scrollbar()