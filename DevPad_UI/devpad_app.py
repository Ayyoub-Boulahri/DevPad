import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import threading

from serial_manager import SerialManager
from profile_store import ProfileStore
from profile_editor import ProfileEditor

from styled_buttons import *
from constants import *


class DevPadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.store  = ProfileStore()
        self.serial = SerialManager()

        self.title("DevPad")
        self.geometry("900x620")
        self.configure(bg=BG)
        self.resizable(True, True)

        self._build_ui()

    # ── SAMPLE DATA ──────────────────────────
    def _load_sample(self):
        sample = json.dumps({
            "profiles": [
                {
                    "name": "Portfolio",
                    "actions": [
                        {"type": "keys", "data": ["CTRL", "ALT", "T"]},
                        {"type": "text", "data": "cd ~/Desktop/portfolio"},
                        {"type": "text", "data": "npm run dev"}
                    ]
                },
                {
                    "name": "Snake Game",
                    "actions": [
                        {"type": "keys", "data": ["CTRL", "ALT", "T"]},
                        {"type": "text", "data": "cd ~/Desktop/projects/test/snake_game"},
                        {"type": "text", "data": "source .venv/bin/activate"},
                        {"type": "text", "data": "python3 game.py"}
                    ]
                }
            ]
        })
        self.store.load_json(sample)
        self._refresh_cards()

    # ── UI BUILD ─────────────────────────────
    def _build_ui(self):
        # ── Sidebar ──
        self.sidebar = tk.Frame(self, bg=BG2, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=BG2, pady=20)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="⌨", font=("Segoe UI", 28), bg=BG2, fg=ACCENT).pack()
        tk.Label(logo_frame, text="DevPad", font=("Segoe UI", 16, "bold"), bg=BG2, fg=TEXT).pack()
        tk.Label(logo_frame, text="ESP32 Launcher", font=("Segoe UI", 9), bg=BG2, fg=TEXT_DIM).pack()

        tk.Frame(self.sidebar, bg=BG3, height=1).pack(fill="x", padx=16, pady=8)

        # Serial section
        serial_frame = tk.Frame(self.sidebar, bg=BG2, padx=16)
        serial_frame.pack(fill="x", pady=8)
        tk.Label(serial_frame, text="SERIAL PORT", font=("Segoe UI", 9, "bold"),
                 bg=BG2, fg=TEXT_DIM, anchor="w").pack(fill="x")

        port_row = tk.Frame(serial_frame, bg=BG2)
        port_row.pack(fill="x", pady=4)

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_row, textvariable=self.port_var,
                                        font=FONT_MONO, width=14, state="readonly")
        self.port_combo.pack(side="left")
        self._refresh_ports()

        tk.Button(port_row, text="⟳", bg=BG3, fg=TEXT, font=("Segoe UI", 11),
                  relief="flat", bd=0, cursor="hand2",
                  command=self._refresh_ports).pack(side="left", padx=4)

        self.connect_btn = styled_button(serial_frame, "Connect", self._toggle_connect, ACCENT)
        self.connect_btn.pack(fill="x", pady=(4,0))

        self.status_dot = tk.Label(serial_frame, text="● Disconnected",
                                   font=("Segoe UI", 9), bg=BG2, fg=RED)
        self.status_dot.pack(anchor="w", pady=4)

        tk.Frame(self.sidebar, bg=BG3, height=1).pack(fill="x", padx=16, pady=8)

        # ESP32 actions
        esp_frame = tk.Frame(self.sidebar, bg=BG2, padx=16)
        esp_frame.pack(fill="x")
        tk.Label(esp_frame, text="ESP32", font=("Segoe UI", 9, "bold"),
                 bg=BG2, fg=TEXT_DIM, anchor="w").pack(fill="x", pady=(0,6))

        styled_button(esp_frame, "📥  Load from ESP32", self._load_from_esp32, BG3, TEXT).pack(fill="x", pady=3)
        styled_button(esp_frame, "📤  Save to ESP32",   self._save_to_esp32,   BG3, TEXT).pack(fill="x", pady=3)

        tk.Frame(self.sidebar, bg=BG3, height=1).pack(fill="x", padx=16, pady=8)

        # Profile actions
        prof_frame = tk.Frame(self.sidebar, bg=BG2, padx=16)
        prof_frame.pack(fill="x")
        tk.Label(prof_frame, text="PROFILES", font=("Segoe UI", 9, "bold"),
                 bg=BG2, fg=TEXT_DIM, anchor="w").pack(fill="x", pady=(0,6))
        styled_button(prof_frame, "+ New Profile", self._add_profile, ACCENT).pack(fill="x")

        # ── Main area ──
        main = tk.Frame(self, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        # Topbar
        topbar = tk.Frame(main, bg=BG, pady=16, padx=24)
        topbar.pack(fill="x")
        tk.Label(topbar, text="Profiles", font=FONT_H1, bg=BG, fg=TEXT).pack(side="left")

        self.profile_count_label = tk.Label(topbar, text="0 profiles",
                                             font=("Segoe UI", 10), bg=BG, fg=TEXT_DIM)
        self.profile_count_label.pack(side="left", padx=12)

        # Cards scroll area
        canvas_frame = tk.Frame(main, bg=BG)
        canvas_frame.pack(fill="both", expand=True, padx=16, pady=(0,16))

        self.canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.cards_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")

        self.cards_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Log bar
        self.log_var = tk.StringVar(value="Ready.")
        log_bar = tk.Frame(main, bg=BG2, pady=6, padx=16)
        log_bar.pack(fill="x", side="bottom")
        tk.Label(log_bar, textvariable=self.log_var,
                 font=FONT_MONO, bg=BG2, fg=TEXT_DIM, anchor="w").pack(fill="x")

    # ── SCROLL HELPERS ───────────────────────
    def _on_frame_configure(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfig(self.canvas_window, width=e.width)

    def _on_mousewheel(self, e):
        self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")

    # ── CARDS ────────────────────────────────
    def _refresh_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        count = len(self.store.profiles)
        self.profile_count_label.config(text=f"{count} profile{'s' if count != 1 else ''}")

        if count == 0:
            tk.Label(self.cards_frame, text="No profiles yet.\nClick '+ New Profile' to get started.",
                     font=("Segoe UI", 12), bg=BG, fg=TEXT_DIM,
                     justify="center").pack(pady=80)
            return

        # Grid layout: 2 columns
        cols = 2
        for i, profile in enumerate(self.store.profiles):
            row = i // cols
            col = i % cols

            card = tk.Frame(self.cards_frame, bg=BG2, padx=18, pady=14,
                            relief="flat", bd=0)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.cards_frame.columnconfigure(col, weight=1)

            # Card header
            hdr = tk.Frame(card, bg=BG2)
            hdr.pack(fill="x", pady=(0,8))

            # Color accent bar
            accent_color = [ACCENT, ACCENT2, GREEN, "#ff6b35", "#ffd60a"][i % 5]
            tk.Frame(card, bg=accent_color, height=3).pack(fill="x", pady=(0,10))

            tk.Label(hdr, text=profile["name"], font=FONT_CARD,
                     bg=BG2, fg=TEXT, anchor="w").pack(side="left", fill="x", expand=True)

            action_count = len(profile["actions"])
            tk.Label(hdr, text=f"{action_count} action{'s' if action_count != 1 else ''}",
                     font=("Segoe UI", 9), bg=BG2, fg=TEXT_DIM).pack(side="right")

            # Actions preview
            preview = tk.Frame(card, bg=BG3, padx=10, pady=8)
            preview.pack(fill="x", pady=(0,10))

            for j, action in enumerate(profile["actions"][:4]):  # show up to 4
                arow = tk.Frame(preview, bg=BG3)
                arow.pack(fill="x", pady=1)

                if action["type"] == "keys":
                    icon, text, fg = "⌨", " + ".join(action["data"]), ACCENT2
                else:
                    icon, text, fg = "▶", action["data"], ACCENT

                tk.Label(arow, text=icon, bg=BG3, fg=fg,
                         font=("Segoe UI", 9)).pack(side="left", padx=(0,6))
                tk.Label(arow, text=text[:40] + ("…" if len(text) > 40 else ""),
                         bg=BG3, fg=TEXT_DIM, font=FONT_MONO,
                         anchor="w").pack(side="left")

            if len(profile["actions"]) > 4:
                tk.Label(preview, text=f"  +{len(profile['actions'])-4} more…",
                         bg=BG3, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(anchor="w")

            # Card buttons
            btn_row = tk.Frame(card, bg=BG2)
            btn_row.pack(fill="x")

            idx = i
            styled_button(btn_row, "✏ Edit",   lambda i=idx: self._edit_profile(i),   BG3, TEXT).pack(side="left", padx=(0,6))
            styled_button(btn_row, "🗑 Delete", lambda i=idx: self._delete_profile(i), BG3, RED).pack(side="left")

    # ── PROFILE ACTIONS ──────────────────────
    def _add_profile(self):
        name = simpledialog.askstring("New Profile", "Profile name:", parent=self)
        if name and name.strip():
            self.store.add_profile(name.strip())
            self._refresh_cards()
            self._log(f"Profile '{name}' created.")

    def _edit_profile(self, index):
        ProfileEditor(self, self.store, index, self._refresh_cards)

    def _delete_profile(self, index):
        name = self.store.profiles[index]["name"]
        if messagebox.askyesno("Delete Profile", f"Delete '{name}'?", parent=self):
            self.store.delete_profile(index)
            self._refresh_cards()
            self._log(f"Profile '{name}' deleted.")

    # ── SERIAL ───────────────────────────────
    def _refresh_ports(self):
        ports = self.serial.list_ports()
        self.port_combo["values"] = ports
        if ports:
            self.port_var.set(ports[0])

    def _toggle_connect(self):
        if self.serial.is_connected():
            self.serial.disconnect()
            self.connect_btn.config(text="Connect", bg=ACCENT)
            self.status_dot.config(text="● Disconnected", fg=RED)
            self._log("Disconnected.")
        else:
            port = self.port_var.get()
            if not port:
                messagebox.showwarning("No port", "Select a serial port first.", parent=self)
                return
            self._log(f"Connecting to {port}…")
            threading.Thread(target=self._do_connect, args=(port,), daemon=True).start()

    def _do_connect(self, port):
        ok = self.serial.connect(port)
        if ok:
            self.after(0, lambda: self.connect_btn.config(text="Disconnect", bg=RED))
            self.after(0, lambda: self.status_dot.config(text="● Connected", fg=GREEN))
            self.after(0, lambda: self._log(f"Connected to {port}"))
        else:
            self.after(0, lambda: self._log(f"Failed to connect to {port}"))

    def _load_from_esp32(self):
        if not self.serial.is_connected():
            messagebox.showwarning("Not connected", "Connect to ESP32 first.", parent=self)
            return
        self._log("Loading from ESP32…")
        threading.Thread(target=self._do_load, daemon=True).start()

    def _do_load(self):
        response = self.serial.get_profiles()
        if response and response.get("status") == "ok":
            data = response.get("data", {})
            self.store.profiles = data.get("profiles", [])
            self.after(0, self._refresh_cards)
            self.after(0, lambda: self._log("Profiles loaded from ESP32."))
        else:
            self.after(0, lambda: self._log("Failed to load from ESP32."))

    def _save_to_esp32(self):
        if not self.serial.is_connected():
            messagebox.showwarning("Not connected", "Connect to ESP32 first.", parent=self)
            return
        self._log("Saving to ESP32…")
        threading.Thread(target=self._do_save, daemon=True).start()

    def _do_save(self):
        data = {"profiles": self.store.profiles}
        response = self.serial.save_profiles(data)
        if response and response.get("status") == "ok":
            self.after(0, lambda: self._log("Saved to ESP32 successfully!"))
        else:
            self.after(0, lambda: self._log("Failed to save to ESP32."))

    # ── LOG ──────────────────────────────────
    def _log(self, msg: str):
        self.log_var.set(f"› {msg}")

