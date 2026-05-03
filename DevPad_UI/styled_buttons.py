import tkinter as tk

from constants import *

def styled_button(parent, text, command, color=ACCENT, fg=BG, **kwargs):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=fg, font=("Segoe UI", 10, "bold"),
        relief="flat", bd=0, padx=14, pady=7,
        cursor="hand2", activebackground=color, activeforeground=fg,
        **kwargs
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def _lighten(hex_color):
    # simple brighten
    r = min(255, int(hex_color[1:3], 16) + 30)
    g = min(255, int(hex_color[3:5], 16) + 30)
    b = min(255, int(hex_color[5:7], 16) + 30)
    return f"#{r:02x}{g:02x}{b:02x}"

def label(parent, text, font=FONT_UI, fg=TEXT, bg=BG, **kwargs):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)
