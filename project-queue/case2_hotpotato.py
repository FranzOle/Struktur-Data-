import tkinter as tk
from tkinter import ttk
from collections import deque
import math
import random

COLORS = {
    "bg": "#0f0f1a",
    "panel": "#1a1a2e",
    "accent": "#ff6b35",
    "accent2": "#ffd700",
    "success": "#69f0ae",
    "warning": "#ffd740",
    "danger": "#ff5252",
    "text": "#e0e0e0",
    "subtext": "#90a4ae",
    "card": "#16213e",
    "border": "#1e3a5f",
    "eliminated": "#37474f",
    "active": "#e65100",
    "holder": "#ff6b35",
}

PLAYER_COLORS = ["#ff6b35", "#4fc3f7", "#69f0ae", "#ffd740", "#ce93d8",
                  "#f48fb1", "#80cbc4", "#ffcc02", "#81d4fa", "#a5d6a7"]


class HotPotatoFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self.players = []
        self.queue = deque()
        self.eliminated = []
        self.running = False
        self.pass_count = 0
        self.num_passes = 5
        self.speed = 700
        self.step_job = None
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self, bg=COLORS["bg"])
        title_frame.pack(fill="x", padx=30, pady=(20, 5))
        tk.Label(title_frame, text="🥔  Permainan Hot Potato",
                 font=("Segoe UI", 18, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(title_frame, text="Simulasi circular queue — pemain tersingkir setelah N kali oper",
                 font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=30, pady=10)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                        highlightbackground=COLORS["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        arena_label = tk.Frame(left, bg=COLORS["panel"])
        arena_label.pack(fill="x", padx=20, pady=(15, 0))
        tk.Label(arena_label, text="ARENA PERMAINAN", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        self.arena_canvas = tk.Canvas(left, width=420, height=320,
                                      bg=COLORS["card"], highlightthickness=0)
        self.arena_canvas.pack(padx=20, pady=10)

        pass_frame = tk.Frame(left, bg=COLORS["panel"])
        pass_frame.pack(fill="x", padx=20, pady=(0, 5))
        tk.Label(pass_frame, text="Oper ke:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(side="left")
        self.pass_label = tk.Label(pass_frame, text="0 / 0",
                                   font=("Segoe UI", 14, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["accent2"])
        self.pass_label.pack(side="left", padx=10)
        self.status_label = tk.Label(pass_frame, text="Belum mulai",
                                     font=("Segoe UI", 10, "italic"),
                                     bg=COLORS["panel"], fg=COLORS["subtext"])
        self.status_label.pack(side="left")

        elim_frame = tk.Frame(left, bg=COLORS["panel"])
        elim_frame.pack(fill="x", padx=20, pady=(0, 15))
        tk.Label(elim_frame, text="TERSINGKIR:", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        self.elim_var = tk.StringVar(value="—")
        self.elim_display = tk.Label(elim_frame, textvariable=self.elim_var,
                                     font=("Segoe UI", 10), bg=COLORS["panel"],
                                     fg=COLORS["danger"], wraplength=380, justify="left")
        self.elim_display.pack(anchor="w", pady=3)

        right = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                         highlightbackground=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew")

        setup_section = tk.Frame(right, bg=COLORS["panel"])
        setup_section.pack(fill="x", padx=20, pady=15)
        tk.Label(setup_section, text="SETUP PERMAINAN", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        tk.Label(setup_section, text="Nama Pemain (pisah koma):",
                 font=("Segoe UI", 9), bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        self.players_entry = tk.Entry(setup_section, font=("Segoe UI", 10),
                                      bg=COLORS["card"], fg=COLORS["text"],
                                      insertbackground=COLORS["accent"], relief="flat", bd=6)
        self.players_entry.pack(fill="x", ipady=4)
        self.players_entry.insert(0, "Ani,Budi,Citra,Dedi,Eka,Fajar")

        tk.Label(setup_section, text="Jumlah Oper (N):",
                 font=("Segoe UI", 9), bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        passes_frame = tk.Frame(setup_section, bg=COLORS["panel"])
        passes_frame.pack(fill="x")
        self.passes_var = tk.IntVar(value=5)
        self.passes_spin = tk.Spinbox(passes_frame, from_=1, to=20, textvariable=self.passes_var,
                                      font=("Segoe UI", 12, "bold"), bg=COLORS["card"],
                                      fg=COLORS["accent2"], relief="flat", bd=4, width=5,
                                      buttonbackground=COLORS["panel"])
        self.passes_spin.pack(side="left")

        tk.Label(setup_section, text="Kecepatan Animasi:",
                 font=("Segoe UI", 9), bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        self.speed_var = tk.IntVar(value=700)
        speed_scale = tk.Scale(setup_section, from_=200, to=1500, orient="horizontal",
                               variable=self.speed_var, bg=COLORS["panel"], fg=COLORS["text"],
                               troughcolor=COLORS["card"], highlightthickness=0,
                               sliderrelief="flat", label="ms per oper")
        speed_scale.pack(fill="x")

        btn_frame = tk.Frame(setup_section, bg=COLORS["panel"])
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="▶  Mulai", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["accent"], fg="white", relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2", command=self._start_game).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="⏸  Pause", font=("Segoe UI", 10),
                  bg=COLORS["warning"], fg="#000", relief="flat", bd=0,
                  padx=10, pady=6, cursor="hand2", command=self._pause).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="Reset", font=("Segoe UI", 9),
                  bg=COLORS["danger"], fg="white", relief="flat", bd=0,
                  padx=10, pady=6, cursor="hand2", command=self._reset).pack(side="left")

        queue_section = tk.Frame(right, bg=COLORS["panel"])
        queue_section.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        tk.Label(queue_section, text="CIRCULAR QUEUE", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        self.queue_canvas = tk.Canvas(queue_section, height=160,
                                      bg=COLORS["card"], highlightthickness=0)
        self.queue_canvas.pack(fill="x", pady=6)

        self.winner_label = tk.Label(right, text="", font=("Segoe UI", 13, "bold"),
                                     bg=COLORS["panel"], fg=COLORS["success"])
        self.winner_label.pack(pady=5)

        self._draw_arena([])

    def _start_game(self):
        if self.running:
            return
        names = [n.strip() for n in self.players_entry.get().split(",") if n.strip()]
        if len(names) < 2:
            self.status_label.config(text="⚠ Minimal 2 pemain!", fg=COLORS["danger"])
            return
        self.players = names
        self.queue = deque(range(len(names)))
        self.eliminated = []
        self.pass_count = 0
        self.num_passes = self.passes_var.get()
        self.speed = self.speed_var.get()
        self.running = True
        self.winner_label.config(text="")
        self.elim_var.set("—")
        self._draw_arena(list(self.queue))
        self._draw_queue_strip()
        self.status_label.config(text="🥔 Permainan dimulai!", fg=COLORS["success"])
        self._step()

    def _step(self):
        if not self.running:
            return
        if len(self.queue) <= 1:
            winner_idx = self.queue[0] if self.queue else -1
            winner = self.players[winner_idx] if winner_idx >= 0 else "?"
            self.running = False
            self.status_label.config(text=f"🏆 Selesai!", fg=COLORS["success"])
            self.winner_label.config(text=f"🏆 PEMENANG: {winner}!")
            self._draw_arena(list(self.queue), winner=winner_idx)
            self._draw_queue_strip()
            return

        self.pass_count = (self.pass_count % self.num_passes) + 1
        self.queue.append(self.queue.popleft())
        holder = self.queue[-1]  
        self.pass_label.config(text=f"{self.pass_count} / {self.num_passes}")
        self._draw_arena(list(self.queue), highlight=self.queue[0])
        self._draw_queue_strip(highlight=self.queue[0])
        self.status_label.config(text=f"🥔 Oper ke-{self.pass_count}...", fg=COLORS["text"])

        if self.pass_count == self.num_passes:
            elim_idx = self.queue.popleft()
            self.eliminated.append(self.players[elim_idx])
            self.elim_var.set(" → ".join(f"❌ {e}" for e in self.eliminated))
            self.status_label.config(text=f"💥 {self.players[elim_idx]} tersingkir!", fg=COLORS["danger"])
            self.pass_count = 0
            self._draw_arena(list(self.queue))
            self._draw_queue_strip()

        self.step_job = self.after(self.speed_var.get(), self._step)

    def _pause(self):
        if self.running:
            self.running = False
            if self.step_job:
                self.after_cancel(self.step_job)
            self.status_label.config(text="⏸ Dijeda", fg=COLORS["warning"])
        else:
            if len(self.queue) > 1:
                self.running = True
                self._step()
                self.status_label.config(text="▶ Lanjut...", fg=COLORS["success"])

    def _reset(self):
        self.running = False
        if self.step_job:
            self.after_cancel(self.step_job)
        self.queue.clear()
        self.eliminated = []
        self.pass_count = 0
        self.winner_label.config(text="")
        self.elim_var.set("—")
        self.status_label.config(text="Belum mulai", fg=COLORS["subtext"])
        self.pass_label.config(text="0 / 0")
        self._draw_arena([])
        self._draw_queue_strip()

    def _draw_arena(self, active_indices, highlight=None, winner=None):
        c = self.arena_canvas
        c.delete("all")
        w, h = 420, 320
        cx, cy, r = w // 2, h // 2, 120

        c.create_oval(cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10,
                      outline=COLORS["border"], width=2, fill=COLORS["bg"])

        all_players = list(range(len(self.players))) if self.players else []
        n = len(all_players)
        if n == 0:
            c.create_text(cx, cy, text="Tambahkan pemain\ndan mulai permainan",
                          fill=COLORS["subtext"], font=("Segoe UI", 11), justify="center")
            return

        for i, idx in enumerate(all_players):
            angle = 2 * math.pi * i / n - math.pi / 2
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            eliminated = idx not in active_indices
            color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
            if eliminated:
                color = COLORS["eliminated"]
            elif idx == winner:
                color = COLORS["success"]
            elif idx == highlight:
                color = COLORS["accent2"]

            rad = 22 if not eliminated else 16
            c.create_oval(px - rad, py - rad, px + rad, py + rad,
                          fill=color, outline="white" if not eliminated else COLORS["border"],
                          width=2 if not eliminated else 1)
            name = self.players[idx][:4] if self.players else str(idx)
            c.create_text(px, py, text=("❌" if eliminated else name),
                          fill="white" if not eliminated else COLORS["subtext"],
                          font=("Segoe UI", 7, "bold"))

        if active_indices:
            holder = active_indices[0]
            angle = 2 * math.pi * (all_players.index(holder)) / n - math.pi / 2
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            c.create_text(px, py - 32, text="🥔", font=("Segoe UI", 14))

        if winner is not None:
            c.create_text(cx, cy, text=f"🏆\n{self.players[winner]}",
                          fill=COLORS["success"], font=("Segoe UI", 12, "bold"), justify="center")

    def _draw_queue_strip(self, highlight=None):
        c = self.queue_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width() or 300
        h = 160

        if not self.queue:
            c.create_text(w // 2, h // 2, text="Queue kosong",
                          fill=COLORS["subtext"], font=("Segoe UI", 10))
            return

        items = list(self.queue)
        box_w = min(60, (w - 20) // max(len(items), 1))
        start_x = (w - box_w * len(items)) // 2
        cy = h // 2

        c.create_text(10, 20, text="FRONT →", fill=COLORS["accent"],
                      font=("Segoe UI", 8, "bold"), anchor="w")

        for i, idx in enumerate(items):
            x = start_x + i * box_w
            color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
            is_front = i == 0
            outline_color = COLORS["accent2"] if is_front else COLORS["border"]
            outline_w = 3 if is_front else 1
            c.create_rectangle(x + 2, cy - 22, x + box_w - 2, cy + 22,
                                fill=color, outline=outline_color, width=outline_w)
            name = (self.players[idx][:4] if self.players else str(idx))
            c.create_text(x + box_w // 2, cy, text=name,
                          fill="white", font=("Segoe UI", 7, "bold"))
            if i < len(items) - 1:
                c.create_text(x + box_w, cy, text="→",
                              fill=COLORS["subtext"], font=("Segoe UI", 9))

        c.create_text(w - 10, 20, text="← BACK", fill=COLORS["subtext"],
                      font=("Segoe UI", 8), anchor="e")