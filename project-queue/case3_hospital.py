import tkinter as tk
from tkinter import ttk
import time

COLORS = {
    "bg": "#0f0f1a",
    "panel": "#1a1a2e",
    "accent": "#ce93d8",
    "accent2": "#e040fb",
    "success": "#69f0ae",
    "warning": "#ffd740",
    "danger": "#ff5252",
    "text": "#e0e0e0",
    "subtext": "#90a4ae",
    "card": "#16213e",
    "border": "#1e3a5f",
}

PRIORITY_CONFIG = {
    0: {"label": "KRITIS",    "color": "#ff1744", "emoji": "🔴", "bg": "#b71c1c"},
    1: {"label": "DARURAT",   "color": "#ff9100", "emoji": "🟠", "bg": "#e65100"},
    2: {"label": "MENENGAH",  "color": "#ffd740", "emoji": "🟡", "bg": "#f57f17"},
    3: {"label": "RINGAN",    "color": "#69f0ae", "emoji": "🟢", "bg": "#1b5e20"},
}


class BoundedPriorityQueue:
    """Priority Queue dengan 4 level, FIFO dalam setiap level."""
    def __init__(self, levels=4):
        self.levels = levels
        self.queues = [[] for _ in range(levels)]
        self.counter = 0  # tiebreaker FIFO
    def enqueue(self, item, priority):
        self.counter += 1
        self.queues[priority].append((self.counter, item, priority))

    def dequeue(self):
        for level in range(self.levels):
            if self.queues[level]:
                return self.queues[level].pop(0)
        return None

    def is_empty(self):
        return all(len(q) == 0 for q in self.queues)

    def all_items(self):
        result = []
        for level in range(self.levels):
            for item in self.queues[level]:
                result.append(item)
        return result

    def size(self):
        return sum(len(q) for q in self.queues)


class HospitalQueueFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self.pq = BoundedPriorityQueue(4)
        self.served = []
        self.serving = False
        self.serve_job = None
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self, bg=COLORS["bg"])
        title_frame.pack(fill="x", padx=30, pady=(20, 5))
        tk.Label(title_frame, text="🏥  Antrian Rumah Sakit",
                 font=("Segoe UI", 18, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(title_frame, text="Priority Queue — pasien darurat didahulukan, FIFO dalam level yang sama",
                 font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=30, pady=10)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                        highlightbackground=COLORS["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        input_section = tk.Frame(left, bg=COLORS["panel"])
        input_section.pack(fill="x", padx=20, pady=15)
        tk.Label(input_section, text="DAFTARKAN PASIEN", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        tk.Label(input_section, text="Nama Pasien:", font=("Segoe UI", 9),
                 bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        self.name_entry = tk.Entry(input_section, font=("Segoe UI", 11),
                                   bg=COLORS["card"], fg=COLORS["text"],
                                   insertbackground=COLORS["accent"], relief="flat", bd=6)
        self.name_entry.pack(fill="x", ipady=4)
        self.name_entry.insert(0, "Pasien Baru")

        tk.Label(input_section, text="Tingkat Urgensi:", font=("Segoe UI", 9),
                 bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))

        self.priority_var = tk.IntVar(value=0)
        self.priority_buttons = {}
        for p, cfg in PRIORITY_CONFIG.items():
            btn = tk.Radiobutton(
                input_section,
                text=f"{cfg['emoji']}  {cfg['label']}",
                variable=self.priority_var,
                value=p,
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["panel"],
                fg=cfg["color"],
                selectcolor=COLORS["card"],
                activebackground=COLORS["panel"],
                activeforeground=cfg["color"],
                relief="flat",
                indicatoron=True
            )
            btn.pack(anchor="w", pady=2)
            self.priority_buttons[p] = btn

        btn_frame = tk.Frame(input_section, bg=COLORS["panel"])
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="  ➕  Daftar", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["accent2"], fg="white", relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2", command=self._enqueue).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="🏥 Layani", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["success"], fg="#000", relief="flat", bd=0,
                  padx=10, pady=6, cursor="hand2", command=self._serve_next).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="Auto", font=("Segoe UI", 9),
                  bg=COLORS["warning"], fg="#000", relief="flat", bd=0,
                  padx=8, pady=6, cursor="hand2", command=self._auto_serve).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="Reset", font=("Segoe UI", 9),
                  bg=COLORS["danger"], fg="white", relief="flat", bd=0,
                  padx=8, pady=6, cursor="hand2", command=self._reset).pack(side="left")

        preset_section = tk.Frame(left, bg=COLORS["panel"])
        preset_section.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(preset_section, text="PRESET CEPAT", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0, 4))

        presets = [
            ("Budi", 3), ("Ani", 0), ("Citra", 2), ("Dedi", 0), ("Eka", 1), ("Fajar", 2)
        ]
        for name, prio in presets:
            cfg = PRIORITY_CONFIG[prio]
            tk.Button(preset_section, text=f"{cfg['emoji']} {name}",
                      font=("Segoe UI", 9), bg=COLORS["card"],
                      fg=cfg["color"], relief="flat", bd=0, padx=8, pady=3,
                      cursor="hand2",
                      command=lambda n=name, p=prio: self._quick_add(n, p)).pack(side="left", padx=2, pady=2)

        stats_section = tk.Frame(left, bg=COLORS["panel"])
        stats_section.pack(fill="x", padx=20, pady=(0, 15))
        tk.Label(stats_section, text="STATISTIK", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0, 4))
        self.stat_labels = {}
        stats_row = tk.Frame(stats_section, bg=COLORS["panel"])
        stats_row.pack(fill="x")
        for key, label, color in [("waiting", "Menunggu", COLORS["warning"]),
                                   ("served", "Dilayani", COLORS["success"])]:
            box = tk.Frame(stats_row, bg=COLORS["card"], bd=0, highlightthickness=1,
                           highlightbackground=COLORS["border"])
            box.pack(side="left", expand=True, fill="x", padx=3)
            tk.Label(box, text=label, font=("Segoe UI", 8), bg=COLORS["card"],
                     fg=COLORS["subtext"]).pack(pady=(6, 0))
            lbl = tk.Label(box, text="0", font=("Segoe UI", 20, "bold"),
                           bg=COLORS["card"], fg=color)
            lbl.pack(pady=(0, 6))
            self.stat_labels[key] = lbl

        right = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                         highlightbackground=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew")

        right_inner = tk.Frame(right, bg=COLORS["panel"])
        right_inner.pack(fill="both", expand=True, padx=20, pady=15)

        tk.Label(right_inner, text="ANTRIAN PRIORITY QUEUE", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        self.now_serving = tk.Label(right_inner, text="💊 Belum ada yang dilayani",
                                    font=("Segoe UI", 12, "bold"), bg=COLORS["card"],
                                    fg=COLORS["text"], pady=10)
        self.now_serving.pack(fill="x", pady=(6, 10))

        self.lane_frames = {}
        for p, cfg in PRIORITY_CONFIG.items():
            lane = tk.Frame(right_inner, bg=COLORS["panel"])
            lane.pack(fill="x", pady=4)

            header = tk.Frame(lane, bg=cfg["bg"])
            header.pack(fill="x")
            tk.Label(header, text=f"{cfg['emoji']}  {cfg['label']}  (Prioritas {p})",
                     font=("Segoe UI", 9, "bold"), bg=cfg["bg"],
                     fg="white", pady=4, padx=8).pack(side="left")
            self.lane_count = tk.Label(header, text="0 pasien",
                                       font=("Segoe UI", 8), bg=cfg["bg"], fg="white")
            self.lane_count.pack(side="right", padx=8)

            patients_frame = tk.Frame(lane, bg=COLORS["card"], height=40)
            patients_frame.pack(fill="x")
            patients_frame.pack_propagate(False)
            self.lane_frames[p] = {"frame": patients_frame, "count_label": self.lane_count}

        tk.Label(right_inner, text="RIWAYAT LAYANAN", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w", pady=(10, 2))
        self.served_text = tk.Text(right_inner, font=("Consolas", 9),
                                   bg=COLORS["card"], fg=COLORS["text"],
                                   relief="flat", bd=0, height=5, state="disabled")
        self.served_text.pack(fill="x")
        self.served_text.tag_config("kritis", foreground=PRIORITY_CONFIG[0]["color"])
        self.served_text.tag_config("darurat", foreground=PRIORITY_CONFIG[1]["color"])
        self.served_text.tag_config("menengah", foreground=PRIORITY_CONFIG[2]["color"])
        self.served_text.tag_config("ringan", foreground=PRIORITY_CONFIG[3]["color"])

    def _enqueue(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        p = self.priority_var.get()
        self.pq.enqueue(name, p)
        self._refresh_lanes()
        self._update_stats()
        self.name_entry.delete(0, "end")

    def _quick_add(self, name, priority):
        self.pq.enqueue(name, priority)
        self._refresh_lanes()
        self._update_stats()

    def _serve_next(self):
        result = self.pq.dequeue()
        if result is None:
            self.now_serving.config(text="⚠️ Antrian kosong!", fg=COLORS["danger"])
            return
        _, name, priority = result
        cfg = PRIORITY_CONFIG[priority]
        self.now_serving.config(
            text=f"{cfg['emoji']}  Melayani: {name}  [{cfg['label']}]",
            fg=cfg["color"]
        )
        self.served.append((name, priority))
        self._log_served(name, priority)
        self._refresh_lanes()
        self._update_stats()

    def _auto_serve(self):
        if self.pq.is_empty():
            return
        self._serve_next()
        if not self.pq.is_empty():
            self.serve_job = self.after(1200, self._auto_serve)

    def _reset(self):
        self.pq = BoundedPriorityQueue(4)
        self.served = []
        if self.serve_job:
            self.after_cancel(self.serve_job)
        self.now_serving.config(text="💊 Belum ada yang dilayani", fg=COLORS["text"])
        self._refresh_lanes()
        self._update_stats()
        self.served_text.config(state="normal")
        self.served_text.delete("1.0", "end")
        self.served_text.config(state="disabled")

    def _refresh_lanes(self):
        for p, cfg in PRIORITY_CONFIG.items():
            frame = self.lane_frames[p]["frame"]
            for w in frame.winfo_children():
                w.destroy()

            items = self.pq.queues[p]
            count_lbl = self.lane_frames[p]["count_label"]
            count_lbl.config(text=f"{len(items)} pasien")

            if not items:
                tk.Label(frame, text="—", font=("Segoe UI", 9),
                         bg=COLORS["card"], fg=COLORS["subtext"], pady=8).pack(side="left", padx=8)
            else:
                for i, (_, name, _) in enumerate(items):
                    tag_bg = cfg["bg"] if i == 0 else COLORS["card"]
                    tag_fg = "white"
                    if i == 0:
                        prefix = "▶ "
                    else:
                        prefix = f"  {i+1}. "
                    tk.Label(frame, text=f"{prefix}{name}",
                             font=("Segoe UI", 9, "bold" if i == 0 else "normal"),
                             bg=tag_bg, fg=tag_fg, padx=8, pady=4).pack(side="left", padx=2)

    def _log_served(self, name, priority):
        cfg = PRIORITY_CONFIG[priority]
        tags = ["kritis", "darurat", "menengah", "ringan"]
        ts = time.strftime("%H:%M:%S")
        self.served_text.config(state="normal")
        self.served_text.insert("end", f"[{ts}] {cfg['emoji']} {name} ({cfg['label']}) — dilayani\n",
                                tags[priority])
        self.served_text.see("end")
        self.served_text.config(state="disabled")

    def _update_stats(self):
        self.stat_labels["waiting"].config(text=str(self.pq.size()))
        self.stat_labels["served"].config(text=str(len(self.served)))