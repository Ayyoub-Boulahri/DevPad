import tkinter as tk
from tkinter import ttk, simpledialog

from profile_store import ProfileStore

from constants import *
from styled_buttons import *


class ProfileEditor(tk.Toplevel):
    def __init__(self, parent, store: ProfileStore, profile_index: int, on_save):
        super().__init__(parent)
        self.store = store
        self.profile_index = profile_index
        self.on_save = on_save
        self.profile = store.profiles[profile_index]

        self.title(f"Edit — {self.profile['name']}")
        self.configure(bg=BG)
        self.geometry("560x520")
        self.resizable(False, False)
        self.grab_set()

        self._build()
        self._refresh_actions()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG2, pady=12)
        hdr.pack(fill="x")
        label(hdr, f"✏  {self.profile['name']}", FONT_H2, ACCENT, BG2).pack(padx=20, anchor="w")

        # Actions list
        mid = tk.Frame(self, bg=BG)
        mid.pack(fill="both", expand=True, padx=16, pady=10)
        label(mid, "ACTIONS", ("Segoe UI", 9, "bold"), TEXT_DIM, BG).pack(anchor="w", pady=(0,6))

        self.actions_frame = tk.Frame(mid, bg=BG)
        self.actions_frame.pack(fill="both", expand=True)

        # Add action bar
        add_bar = tk.Frame(self, bg=BG2, pady=10)
        add_bar.pack(fill="x", side="bottom")

        styled_button(add_bar, "+ Shortcut", self._add_shortcut, ACCENT2).pack(side="left", padx=(16,6))
        styled_button(add_bar, "+ Command",  self._add_command,  ACCENT).pack(side="left", padx=6)
        styled_button(add_bar, "💾 Save",     self._save,         GREEN, BG).pack(side="right", padx=16)

    def _refresh_actions(self):
        for w in self.actions_frame.winfo_children():
            w.destroy()

        for i, action in enumerate(self.profile["actions"]):
            row = tk.Frame(self.actions_frame, bg=BG3, pady=6, padx=10)
            row.pack(fill="x", pady=3)

            if action["type"] == "keys":
                icon = "⌨"
                text = " + ".join(action["data"])
                color = ACCENT2
            else:
                icon = "▶"
                text = action["data"]
                color = ACCENT

            tk.Label(row, text=icon, bg=BG3, fg=color, font=("Segoe UI", 13)).pack(side="left", padx=(0,8))
            tk.Label(row, text=text, bg=BG3, fg=TEXT, font=FONT_MONO, anchor="w").pack(side="left", fill="x", expand=True)

            idx = i
            tk.Button(
                row, text="✕", bg=BG3, fg=RED,
                font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                cursor="hand2", command=lambda i=idx: self._delete_action(i)
            ).pack(side="right")

    def _add_shortcut(self):
        val = simpledialog.askstring(
            "Add Shortcut", "Enter keys separated by + (e.g. CTRL+ALT+T):",
            parent=self
        )
        if val:
            keys = [k.strip().upper() for k in val.split("+") if k.strip()]
            self.store.add_action(self.profile_index, {"type": "keys", "data": keys})
            self._refresh_actions()

    def _add_command(self):
        val = simpledialog.askstring(
            "Add Command", "Enter terminal command:",
            parent=self
        )
        if val:
            self.store.add_action(self.profile_index, {"type": "text", "data": val.strip()})
            self._refresh_actions()

    def _delete_action(self, index):
        self.store.delete_action(self.profile_index, index)
        self._refresh_actions()

    def _save(self):
        self.on_save()
        self.destroy()

