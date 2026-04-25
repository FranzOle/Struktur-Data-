import tkinter as tk
from tkinter import ttk
from collections import deque
import random
import time

COLORS = {
    "bg": "#0f0f1a",
    "panel": "#1a1a2e",
    "accent": "#ffd740",
    "accent2": "#ffab00",
    "success": "#69f0ae",
    "warning": "#ffd740",
    "danger": "#ff5252",
    "text": "#e0e0e0",
    "subtext": "#90a4ae",
    "card": "#16213e",
    "border": "#1e3a5f",
    "agent_idle": "#37474f",
    "agent_busy": "#1565c0",
}


class Passenger:
    _counter = 0

    def __init__(self, arrive_time):
        Passenger._counter += 1
        self.id = Passenger._counter
        self.name = f"P{self.id:03d}"
        self.arrive_time = arrive_time
        self.start_service = None
        self.end_service = None

    @property
    def wait_time(self):
        if self.start_service is not None:
            return self.start_service - self.arrive_time
        return 0

    @property
    def service_duration(self):
        if self.start_service is not None and self.end_service is not None:
            return self.end_service - self.start_service
        return 0


class Agent:
    def __init__(self, id):
        self.id = id
        self.busy = False
        self.current_passenger = None
        self.finish_time = 0
        self.total_served = 0


class AirportSimFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self.running = False
        self.paused = False
        self.sim_job = None
        self.cur_time = 0
        self.duration = 60
        self.num_agents = 2
        self.between_time = 4
        self.service_time = 8
        self.queue = deque()
        self.agents = []
        self.all_passengers = []
        self.served = []
        Passenger._counter = 0
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self, bg=COLORS["bg"])
        title_frame.pack(fill="x", padx=30, pady=(20, 5))
        tk.Label(title_frame, text="✈️  Simulasi Loket Tiket Bandara",
                 font=("Segoe UI", 18, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(title_frame, text="Discrete Event Simulation — hitung rata-rata waktu tunggu",
                 font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=30, pady=10)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                        highlightbackground=COLORS["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctrl = tk.Frame(left, bg=COLORS["panel"])
        ctrl.pack(fill="x", padx=20, pady=15)
        tk.Label(ctrl, text="PARAMETER SIMULASI", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        params = [
            ("Durasi (menit):", "duration_var", 60, 10, 300),
            ("Jumlah Agen:", "agents_var", 2, 1, 10),
            ("Interval Kedatangan (menit):", "between_var", 4, 1, 20),
            ("Waktu Layanan (menit):", "service_var", 8, 1, 30),
        ]
        self.param_vars = {}
        for label, var_name, default, lo, hi in params:
            row = tk.Frame(ctrl, bg=COLORS["panel"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=("Segoe UI", 9),
                     bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w")
            var = tk.IntVar(value=default)
            scale = tk.Scale(row, from_=lo, to=hi, orient="horizontal", variable=var,
                             bg=COLORS["panel"], fg=COLORS["text"], troughcolor=COLORS["card"],
                             highlightthickness=0, sliderrelief="flat")
            scale.pack(fill="x")
            self.param_vars[var_name] = var

        btn_frame = tk.Frame(ctrl, bg=COLORS["panel"])
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="▶ Mulai", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["accent"], fg="#000", relief="flat", bd=0,
                  padx=12, pady=6, cursor="hand2", command=self._start_sim).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="⏸ Pause", font=("Segoe UI", 10),
                  bg="#546e7a", fg="white", relief="flat", bd=0,
                  padx=8, pady=6, cursor="hand2", command=self._pause).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="Reset", font=("Segoe UI", 9),
                  bg=COLORS["danger"], fg="white", relief="flat", bd=0,
                  padx=8, pady=6, cursor="hand2", command=self._reset).pack(side="left")

        self.time_label = tk.Label(left, text="⏱  Waktu: 0 / 0 menit",
                                   font=("Segoe UI", 13, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["accent2"])
        self.time_label.pack(padx=20, pady=5)

        self.progress = ttk.Progressbar(left, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(padx=20, fill="x")

        stats_section = tk.Frame(left, bg=COLORS["panel"])
        stats_section.pack(fill="x", padx=20, pady=10)
        tk.Label(stats_section, text="STATISTIK", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0, 4))

        self.stat_labels = {}
        stat_defs = [
            ("avg_wait", "Avg Wait", COLORS["danger"]),
            ("served", "Dilayani", COLORS["success"]),
            ("queue_len", "Antrian", COLORS["warning"]),
            ("arrived", "Tiba", COLORS["accent"]),
        ]
        stats_grid = tk.Frame(stats_section, bg=COLORS["panel"])
        stats_grid.pack(fill="x")
        for i, (key, label, color) in enumerate(stat_defs):
            box = tk.Frame(stats_grid, bg=COLORS["card"], bd=0, highlightthickness=1,
                           highlightbackground=COLORS["border"])
            box.grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="ew")
            stats_grid.columnconfigure(i % 2, weight=1)
            tk.Label(box, text=label, font=("Segoe UI", 8), bg=COLORS["card"],
                     fg=COLORS["subtext"]).pack(pady=(4, 0))
            lbl = tk.Label(box, text="—", font=("Segoe UI", 16, "bold"),
                           bg=COLORS["card"], fg=color)
            lbl.pack(pady=(0, 4))
            self.stat_labels[key] = lbl

        self.insight_label = tk.Label(left, text="",
                                      font=("Segoe UI", 9, "italic"),
                                      bg=COLORS["card"], fg=COLORS["success"],
                                      wraplength=220, justify="left", pady=8, padx=10)
        self.insight_label.pack(fill="x", padx=20, pady=(0, 15))

        # panel
        right = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                         highlightbackground=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew")

        right_inner = tk.Frame(right, bg=COLORS["panel"])
        right_inner.pack(fill="both", expand=True, padx=20, pady=15)

        tk.Label(right_inner, text="LOKET PELAYANAN", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        self.agents_frame = tk.Frame(right_inner, bg=COLORS["panel"])
        self.agents_frame.pack(fill="x", pady=6)

        tk.Label(right_inner, text="ANTRIAN PENUMPANG", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w", pady=(10, 0))
        self.queue_canvas = tk.Canvas(right_inner, height=80,
                                      bg=COLORS["card"], highlightthickness=0)
        self.queue_canvas.pack(fill="x", pady=4)

        tk.Label(right_inner, text="GRAFIK WAKTU TUNGGU", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w", pady=(10, 0))
        self.chart_canvas = tk.Canvas(right_inner, height=150,
                                      bg=COLORS["card"], highlightthickness=0)
        self.chart_canvas.pack(fill="x", pady=4)

        tk.Label(right_inner, text="LOG SIMULASI", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w", pady=(10, 0))
        self.log_text = tk.Text(right_inner, font=("Consolas", 8),
                                bg=COLORS["card"], fg=COLORS["text"],
                                relief="flat", bd=0, height=7, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("arrive", foreground=COLORS["accent"])
        self.log_text.tag_config("serve", foreground=COLORS["success"])
        self.log_text.tag_config("done", foreground=COLORS["warning"])
        self.log_text.tag_config("info", foreground=COLORS["subtext"])

        self._draw_agents([])
        self._draw_queue_visual()

    def _start_sim(self):
        if self.running:
            return
        self._reset(clear_only=True)
        self.duration = self.param_vars["duration_var"].get()
        self.num_agents = self.param_vars["agents_var"].get()
        self.between_time = self.param_vars["between_var"].get()
        self.service_time = self.param_vars["service_var"].get()
        Passenger._counter = 0
        self.agents = [Agent(i + 1) for i in range(self.num_agents)]
        self.running = True
        self.paused = False
        self.cur_time = 0
        self._log(f"[START] Simulasi dimulai: {self.num_agents} agen, durasi {self.duration} menit", "info")
        self._log(f"[CONFIG] Interval={self.between_time} mnt, Layanan={self.service_time} mnt", "info")
        self._tick()

    def _tick(self):
        if not self.running or self.paused:
            return
        t = self.cur_time

        prob = 1 / self.between_time
        if random.random() < prob:
            p = Passenger(t)
            self.queue.append(p)
            self.all_passengers.append(p)
            self._log(f"[t={t:03d}] ✈ {p.name} tiba → antrian [{len(self.queue)}]", "arrive")

        for agent in self.agents:
            if not agent.busy and self.queue:
                p = self.queue.popleft()
                p.start_service = t
                svc = max(1, int(random.gauss(self.service_time, self.service_time * 0.2)))
                p.end_service = t + svc
                agent.busy = True
                agent.current_passenger = p
                agent.finish_time = t + svc
                self._log(f"[t={t:03d}] 🏢 Agen {agent.id} melayani {p.name} (tunggu {p.wait_time} mnt)", "serve")

        for agent in self.agents:
            if agent.busy and t >= agent.finish_time:
                p = agent.current_passenger
                agent.busy = False
                agent.current_passenger = None
                agent.total_served += 1
                self.served.append(p)
                self._log(f"[t={t:03d}] ✅ Agen {agent.id} selesai layani {p.name}", "done")

        self._draw_agents(self.agents)
        self._draw_queue_visual()
        self._update_stats(t)
        self.time_label.config(text=f"⏱  Waktu: {t} / {self.duration} menit")
        self.progress["value"] = (t / self.duration) * 100

        self.cur_time += 1
        if self.cur_time > self.duration:
            self.running = False
            self._finish_sim()
            return

        self.sim_job = self.after(80, self._tick)

    def _finish_sim(self):
        avg = (sum(p.wait_time for p in self.served) / len(self.served)) if self.served else 0
        self._log(f"[DONE] Simulasi selesai! Dilayani={len(self.served)}, Avg Wait={avg:.1f} mnt", "done")
        self.stat_labels["avg_wait"].config(text=f"{avg:.1f}")
        if avg < 5:
            msg = f"✅ Efisien! Avg wait {avg:.1f} mnt.\nCoba kurangi agen."
        elif avg < 15:
            msg = f"⚠️ Avg wait {avg:.1f} mnt.\nPertimbangkan +1 agen."
        else:
            msg = f"🔴 Avg wait {avg:.1f} mnt!\nTambah agen segera."
        self.insight_label.config(text=msg)
        self._draw_wait_chart()

    def _pause(self):
        if self.running:
            self.paused = not self.paused
            if not self.paused:
                self._tick()

    def _reset(self, clear_only=False):
        self.running = False
        self.paused = False
        if self.sim_job:
            self.after_cancel(self.sim_job)
        if not clear_only:
            self.queue.clear()
            self.agents = []
            self.all_passengers = []
            self.served = []
            self.cur_time = 0
            self.time_label.config(text="⏱  Waktu: 0 / 0 menit")
            self.progress["value"] = 0
            self.insight_label.config(text="")
            for key in self.stat_labels:
                self.stat_labels[key].config(text="—")
            self._draw_agents([])
            self._draw_queue_visual()
            self.chart_canvas.delete("all")
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.config(state="disabled")
        else:
            self.queue.clear()
            self.agents = []
            self.all_passengers = []
            self.served = []
            self.cur_time = 0

    def _draw_agents(self, agents):
        for w in self.agents_frame.winfo_children():
            w.destroy()
        if not agents:
            tk.Label(self.agents_frame, text="Belum ada agen",
                     font=("Segoe UI", 9), bg=COLORS["panel"],
                     fg=COLORS["subtext"]).pack()
            return
        for agent in agents:
            box = tk.Frame(self.agents_frame, bg=COLORS["agent_busy"] if agent.busy else COLORS["agent_idle"],
                           bd=0, highlightthickness=1,
                           highlightbackground=COLORS["border"])
            box.pack(side="left", padx=4, pady=4, ipadx=8, ipady=8)
            status = "🧑‍💼" if agent.busy else "💤"
            tk.Label(box, text=f"{status}\nAgen {agent.id}",
                     font=("Segoe UI", 9, "bold"),
                     bg=COLORS["agent_busy"] if agent.busy else COLORS["agent_idle"],
                     fg="white", justify="center").pack()
            if agent.busy and agent.current_passenger:
                tk.Label(box, text=agent.current_passenger.name,
                         font=("Segoe UI", 8),
                         bg=COLORS["agent_busy"],
                         fg=COLORS["accent"]).pack()

    def _draw_queue_visual(self):
        c = self.queue_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width() or 400
        items = list(self.queue)[:20]
        if not items:
            c.create_text(w // 2, 40, text="Antrian kosong ✅",
                          fill=COLORS["success"], font=("Segoe UI", 10))
            return
        box_w = min(35, (w - 20) // max(len(items), 1))
        for i, p in enumerate(items):
            x = 10 + i * (box_w + 2)
            wait = self.cur_time - p.arrive_time
            color = COLORS["danger"] if wait > 10 else (COLORS["warning"] if wait > 5 else COLORS["accent"])
            c.create_rectangle(x, 10, x + box_w, 60, fill=color,
                                outline=COLORS["border"], width=1)
            c.create_text(x + box_w // 2, 28, text=p.name[-3:],
                          fill="black", font=("Segoe UI", 6, "bold"))
            c.create_text(x + box_w // 2, 48, text=f"{wait}m",
                          fill="black", font=("Segoe UI", 6))
        if len(self.queue) > 20:
            c.create_text(w - 30, 35, text=f"+{len(self.queue) - 20}",
                          fill=COLORS["danger"], font=("Segoe UI", 9, "bold"))

    def _draw_wait_chart(self):
        c = self.chart_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width() or 400
        h = 150
        if not self.served:
            return
        waits = [p.wait_time for p in self.served[-50:]]
        max_w = max(waits) if waits else 1
        bar_w = max(4, (w - 20) // len(waits))
        for i, wt in enumerate(waits):
            x = 10 + i * bar_w
            bar_h = int((wt / max(max_w, 1)) * (h - 30))
            color = COLORS["danger"] if wt > 10 else (COLORS["warning"] if wt > 5 else COLORS["success"])
            c.create_rectangle(x, h - bar_h - 10, x + bar_w - 1, h - 10,
                                fill=color, outline="")
        avg = sum(waits) / len(waits)
        avg_y = h - 10 - int((avg / max(max_w, 1)) * (h - 30))
        c.create_line(10, avg_y, w - 10, avg_y, fill=COLORS["accent2"], dash=(4, 2), width=2)
        c.create_text(w - 5, avg_y - 8, text=f"avg {avg:.1f}m",
                      fill=COLORS["accent2"], font=("Segoe UI", 7), anchor="e")

    def _update_stats(self, t):
        avg = (sum(p.wait_time for p in self.served) / len(self.served)) if self.served else 0
        self.stat_labels["avg_wait"].config(text=f"{avg:.1f}")
        self.stat_labels["served"].config(text=str(len(self.served)))
        self.stat_labels["queue_len"].config(text=str(len(self.queue)))
        self.stat_labels["arrived"].config(text=str(len(self.all_passengers)))

    def _log(self, msg, tag=""):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{msg}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")