import tkinter as tk
from tkinter import ttk
from collections import deque
import math
import time

COLORS = {
    "bg": "#0f0f1a",
    "panel": "#1a1a2e",
    "accent": "#4fc3f7",
    "accent2": "#00e5ff",
    "success": "#69f0ae",
    "warning": "#ffd740",
    "danger": "#ff5252",
    "text": "#e0e0e0",
    "subtext": "#90a4ae",
    "card": "#16213e",
    "border": "#1e3a5f",
    "node_default": "#1e3a5f",
    "node_visited": "#0d47a1",
    "node_current": "#ff6b35",
    "node_queued": "#4fc3f7",
    "node_start": "#ffd740",
    "edge_default": "#263238",
    "edge_visited": "#4fc3f7",
}

SAMPLE_GRAPH = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F", "G"],
    "D": ["B"],
    "E": ["B", "H"],
    "F": ["C"],
    "G": ["C", "I"],
    "H": ["E"],
    "I": ["G"],
}

NODE_POSITIONS = {
    "A": (250, 60),
    "B": (130, 160),
    "C": (370, 160),
    "D": (60, 280),
    "E": (200, 280),
    "F": (310, 280),
    "G": (440, 280),
    "H": (200, 380),
    "I": (440, 380),
}


class BFSFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self.graph = {k: list(v) for k, v in SAMPLE_GRAPH.items()}
        self.positions = dict(NODE_POSITIONS)
        self.visited = set()
        self.queue = deque()
        self.bfs_order = []
        self.current_node = None
        self.running = False
        self.step_job = None
        self.node_states = {}  
        self.edge_states = {}
        self.start_node = "A"
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self, bg=COLORS["bg"])
        title_frame.pack(fill="x", padx=30, pady=(20, 5))
        tk.Label(title_frame, text="🕸️  BFS — Breadth-First Search",
                 font=("Segoe UI", 18, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(title_frame, text="Visualisasi pencarian level demi level menggunakan Queue",
                 font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=30, pady=10)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                        highlightbackground=COLORS["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left, text="VISUALISASI GRAF", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"], pady=8).pack(anchor="w", padx=20)

        self.graph_canvas = tk.Canvas(left, width=500, height=470,
                                      bg=COLORS["bg"], highlightthickness=0)
        self.graph_canvas.pack(padx=10, pady=(0, 10))

        legend_frame = tk.Frame(left, bg=COLORS["panel"])
        legend_frame.pack(fill="x", padx=20, pady=(0, 10))
        legends = [
            ("Start", COLORS["node_start"]),
            ("Queued", COLORS["node_queued"]),
            ("Current", COLORS["node_current"]),
            ("Visited", COLORS["node_visited"]),
        ]
        for label, color in legends:
            box = tk.Frame(legend_frame, bg=COLORS["panel"])
            box.pack(side="left", padx=8)
            tk.Canvas(box, width=14, height=14, bg=color, highlightthickness=0).pack(side="left")
            tk.Label(box, text=f" {label}", font=("Segoe UI", 8),
                     bg=COLORS["panel"], fg=COLORS["text"]).pack(side="left")

        right = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                         highlightbackground=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew")

        control_section = tk.Frame(right, bg=COLORS["panel"])
        control_section.pack(fill="x", padx=20, pady=15)
        tk.Label(control_section, text="KONTROL BFS", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        tk.Label(control_section, text="Node Awal:", font=("Segoe UI", 9),
                 bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        node_frame = tk.Frame(control_section, bg=COLORS["panel"])
        node_frame.pack(fill="x")
        self.start_var = tk.StringVar(value="A")
        for node in sorted(self.graph.keys()):
            tk.Radiobutton(node_frame, text=node, variable=self.start_var, value=node,
                           font=("Segoe UI", 10, "bold"), bg=COLORS["panel"],
                           fg=COLORS["accent"], selectcolor=COLORS["card"],
                           activebackground=COLORS["panel"], relief="flat"
                           ).pack(side="left", padx=3)

        tk.Label(control_section, text="Kecepatan:", font=("Segoe UI", 9),
                 bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        self.speed_var = tk.IntVar(value=800)
        tk.Scale(control_section, from_=200, to=2000, orient="horizontal",
                 variable=self.speed_var, bg=COLORS["panel"], fg=COLORS["text"],
                 troughcolor=COLORS["card"], highlightthickness=0,
                 sliderrelief="flat", label="ms per langkah").pack(fill="x")

        btn_frame = tk.Frame(control_section, bg=COLORS["panel"])
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="▶ Start BFS", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["accent"], fg="#000", relief="flat", bd=0,
                  padx=12, pady=6, cursor="hand2", command=self._start_bfs).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="⏭ Step", font=("Segoe UI", 10),
                  bg=COLORS["warning"], fg="#000", relief="flat", bd=0,
                  padx=8, pady=6, cursor="hand2", command=self._manual_step).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="Reset", font=("Segoe UI", 9),
                  bg=COLORS["danger"], fg="white", relief="flat", bd=0,
                  padx=8, pady=6, cursor="hand2", command=self._reset).pack(side="left")

        queue_section = tk.Frame(right, bg=COLORS["panel"])
        queue_section.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(queue_section, text="QUEUE SAAT INI", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        self.queue_canvas = tk.Canvas(queue_section, height=60,
                                      bg=COLORS["card"], highlightthickness=0)
        self.queue_canvas.pack(fill="x", pady=4)

        self.status_label = tk.Label(right, text="",
                                     font=("Segoe UI", 10, "italic"),
                                     bg=COLORS["panel"], fg=COLORS["subtext"], wraplength=250)
        self.status_label.pack(padx=20, pady=4)

        order_section = tk.Frame(right, bg=COLORS["panel"])
        order_section.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(order_section, text="URUTAN TRAVERSAL", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        self.order_frame = tk.Frame(order_section, bg=COLORS["card"], height=50)
        self.order_frame.pack(fill="x", pady=4)

        log_section = tk.Frame(right, bg=COLORS["panel"])
        log_section.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        tk.Label(log_section, text="LOG BFS", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        self.log_text = tk.Text(log_section, font=("Consolas", 9),
                                bg=COLORS["card"], fg=COLORS["text"],
                                relief="flat", bd=0, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("visit", foreground=COLORS["accent"])
        self.log_text.tag_config("enqueue", foreground=COLORS["success"])
        self.log_text.tag_config("done", foreground=COLORS["warning"])

        self._draw_graph()

    def _start_bfs(self):
        if self.running:
            return
        self._reset(clear_log=True)
        start = self.start_var.get()
        self.start_node = start
        self.visited.add(start)
        self.queue.append(start)
        self.node_states[start] = "start"
        self._log(f"[START] BFS dari node '{start}'", "visit")
        self._draw_graph()
        self._draw_queue_strip()
        self.running = True
        self.step_job = self.after(self.speed_var.get(), self._bfs_step)

    def _bfs_step(self):
        if not self.running:
            return
        if not self.queue:
            self.running = False
            self.status_label.config(text="✅ BFS selesai! Semua node terkunjungi.", fg=COLORS["success"])
            self._log(f"[DONE] Traversal selesai: {' → '.join(self.bfs_order)}", "done")
            self._draw_graph()
            return

        node = self.queue.popleft()
        self.current_node = node
        self.bfs_order.append(node)
        self.node_states[node] = "current"
        self._log(f"[VISIT] Memproses node '{node}'", "visit")
        self._draw_graph()
        self._draw_queue_strip()
        self._draw_order()
        self.status_label.config(text=f"🔵 Memproses: {node}", fg=COLORS["node_current"])

        for neighbor in self.graph.get(node, []):
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                self.queue.append(neighbor)
                self.node_states[neighbor] = "queued"
                edge = tuple(sorted([node, neighbor]))
                self.edge_states[edge] = "visited"
                self._log(f"  ↳ [ENQUEUE] Tetangga '{neighbor}' masuk queue", "enqueue")

        self.node_states[node] = "visited"
        self._draw_graph()

        self.step_job = self.after(self.speed_var.get(), self._bfs_step)

    def _manual_step(self):
        if not self.queue and not self.running:
            start = self.start_var.get()
            self.start_node = start
            self.visited.add(start)
            self.queue.append(start)
            self.node_states[start] = "start"
            self._draw_graph()
            self._draw_queue_strip()
            return
        self._bfs_step()

    def _reset(self, clear_log=False):
        self.running = False
        if self.step_job:
            self.after_cancel(self.step_job)
        self.visited = set()
        self.queue = deque()
        self.bfs_order = []
        self.current_node = None
        self.node_states = {}
        self.edge_states = {}
        self.status_label.config(text="Pilih node awal dan tekan Start", fg=COLORS["subtext"])
        if clear_log:
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.config(state="disabled")
        self._draw_graph()
        self._draw_queue_strip()
        self._draw_order()

    def _draw_graph(self):
        c = self.graph_canvas
        c.delete("all")

        #edges
        for node, neighbors in self.graph.items():
            x1, y1 = self.positions[node]
            for nb in neighbors:
                if nb > node: 
                    x2, y2 = self.positions[nb]
                    edge = tuple(sorted([node, nb]))
                    color = COLORS["edge_visited"] if self.edge_states.get(edge) == "visited" else COLORS["edge_default"]
                    width = 3 if self.edge_states.get(edge) == "visited" else 1
                    c.create_line(x1, y1, x2, y2, fill=color, width=width)

        for node, (x, y) in self.positions.items():
            state = self.node_states.get(node, "default")
            color_map = {
                "default": COLORS["node_default"],
                "start": COLORS["node_start"],
                "queued": COLORS["node_queued"],
                "current": COLORS["node_current"],
                "visited": COLORS["node_visited"],
            }
            color = color_map[state]
            r = 24
            outline = "white" if state != "default" else COLORS["border"]
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill=color, outline=outline, width=2)
            c.create_text(x, y, text=node, fill="white",
                          font=("Segoe UI", 12, "bold"))

            if node in self.bfs_order:
                level = self.bfs_order.index(node) + 1
                c.create_text(x + r, y - r, text=str(level),
                              fill=COLORS["warning"], font=("Segoe UI", 8, "bold"))

    def _draw_queue_strip(self):
        c = self.queue_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width() or 300
        items = list(self.queue)
        if not items:
            c.create_text(w // 2, 30, text="Queue kosong",
                          fill=COLORS["subtext"], font=("Segoe UI", 9))
            return

        box_w = min(50, (w - 20) // max(len(items), 1))
        start_x = 10
        for i, node in enumerate(items):
            x = start_x + i * (box_w + 4)
            color = COLORS["node_queued"]
            c.create_rectangle(x, 10, x + box_w, 50, fill=color,
                                outline=COLORS["accent2"] if i == 0 else COLORS["border"],
                                width=2 if i == 0 else 1)
            c.create_text(x + box_w // 2, 30, text=node, fill="white",
                          font=("Segoe UI", 10, "bold"))
        c.create_text(start_x + 5, 55, text="← FRONT", fill=COLORS["accent"],
                      font=("Segoe UI", 7), anchor="w")

    def _draw_order(self):
        for w in self.order_frame.winfo_children():
            w.destroy()
        for i, node in enumerate(self.bfs_order):
            tk.Label(self.order_frame, text=node,
                     font=("Segoe UI", 10, "bold"),
                     bg=COLORS["node_visited"] if i < len(self.bfs_order) - 1 else COLORS["node_current"],
                     fg="white", padx=8, pady=6, relief="flat").pack(side="left", padx=1)
            if i < len(self.bfs_order) - 1:
                tk.Label(self.order_frame, text="→", font=("Segoe UI", 9),
                         bg=COLORS["card"], fg=COLORS["subtext"]).pack(side="left")

    def _log(self, msg, tag=""):
        self.log_text.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")