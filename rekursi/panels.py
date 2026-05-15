import tkinter as tk
from tkinter import ttk, messagebox
import threading
from theme import *
from algorithms import solve_nqueens, solve_knights_tour, solve_knapsack


def make_entry(parent, width=8, **kw):
    e = tk.Entry(parent, width=width, bg=CARD2, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=FONT_BODY, bd=0, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT, **kw)
    return e


def make_btn(parent, text, cmd, color=BTN, width=14):
    btn = tk.Button(parent, text=text, command=cmd, bg=color, fg=TEXT,
                    activebackground=BTN_HOV, activeforeground=TEXT,
                    font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                    cursor="hand2", width=width, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOV))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def section_label(parent, text):
    lbl = tk.Label(parent, text=text, bg=CARD, fg=TEXT2, font=FONT_SMALL)
    return lbl


class NQueensPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.solutions = []
        self.current_sol = 0
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(top, text="N-Queens", bg=BG, fg=ACCENT, font=FONT_TITLE).pack(side="left")

        ctrl = tk.Frame(self, bg=CARD, bd=0, relief="flat")
        ctrl.pack(fill="x", padx=24, pady=(0, 12))
        ctrl.configure(highlightbackground=BORDER, highlightthickness=1)

        inner = tk.Frame(ctrl, bg=CARD)
        inner.pack(padx=16, pady=14, fill="x")

        tk.Label(inner, text="Ukuran Papan (N)", bg=CARD, fg=TEXT2, font=FONT_SMALL).pack(side="left", padx=(0, 8))
        self.n_entry = make_entry(inner, width=6)
        self.n_entry.insert(0, "6")
        self.n_entry.pack(side="left", padx=(0, 12))

        self.solve_btn = make_btn(inner, "▶  Solve", self._solve)
        self.solve_btn.pack(side="left", padx=(0, 8))

        self.prev_btn = make_btn(inner, "◀ Prev", self._prev_sol, color="#1C3A5A", width=8)
        self.prev_btn.pack(side="left", padx=2)
        self.next_btn = make_btn(inner, "Next ▶", self._next_sol, color="#1C3A5A", width=8)
        self.next_btn.pack(side="left", padx=2)

        self.sol_label = tk.Label(inner, text="", bg=CARD, fg=ACCENT2, font=FONT_SMALL)
        self.sol_label.pack(side="left", padx=12)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=1)
        bottom.rowconfigure(0, weight=1)

        self.canvas_frame = tk.Frame(bottom, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.canvas = tk.Canvas(self.canvas_frame, bg=CARD, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=16)

        right = tk.Frame(bottom, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="INFO", bg=CARD, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))

        self.info_box = tk.Text(right, bg=CARD2, fg=TEXT, font=FONT_MONO, relief="flat",
                                state="disabled", wrap="word", bd=0, width=24,
                                highlightthickness=0)
        self.info_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _solve(self):
        try:
            n = int(self.n_entry.get())
            if n < 1 or n > 12:
                messagebox.showwarning("Input", "Masukkan N antara 1 - 12")
                return
        except ValueError:
            messagebox.showwarning("Input", "Masukkan angka valid")
            return

        self.solve_btn.config(state="disabled", text="Solving...")
        self.sol_label.config(text="Mencari solusi...")

        def run():
            sols = solve_nqueens(n)
            self.after(0, lambda: self._show_solutions(sols, n))

        threading.Thread(target=run, daemon=True).start()

    def _show_solutions(self, sols, n):
        self.solve_btn.config(state="normal", text="▶  Solve")
        self.solutions = sols
        self.current_sol = 0
        if not sols:
            self.sol_label.config(text="Tidak ada solusi")
            self._update_info(n, 0)
            return
        self.sol_label.config(text=f"Solusi: 1 / {len(sols)}")
        self._draw(n, sols[0])
        self._update_info(n, len(sols))

    def _draw(self, n, queens):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 380
        h = self.canvas.winfo_height() or 380
        size = min(w, h) - 20
        cell = size // n
        ox = (w - cell * n) // 2
        oy = (h - cell * n) // 2

        queen_set = set(queens)
        for r in range(n):
            for c in range(n):
                light = (r + c) % 2 == 0
                color = "#1E3448" if light else "#162030"
                self.canvas.create_rectangle(
                    ox + c * cell, oy + r * cell,
                    ox + (c + 1) * cell, oy + (r + 1) * cell,
                    fill=color, outline=BORDER, width=1)
                if (r, c) in queen_set:
                    cx = ox + c * cell + cell // 2
                    cy = oy + r * cell + cell // 2
                    r2 = cell * 0.35
                    self.canvas.create_oval(cx - r2, cy - r2, cx + r2, cy + r2,
                                            fill=ACCENT, outline=ACCENT2, width=2)
                    self.canvas.create_text(cx, cy, text="♛", fill=BG,
                                            font=("Segoe UI", max(8, cell // 3), "bold"))

    def _prev_sol(self):
        if not self.solutions: return
        n = int(self.n_entry.get())
        self.current_sol = (self.current_sol - 1) % len(self.solutions)
        self.sol_label.config(text=f"Solusi: {self.current_sol + 1} / {len(self.solutions)}")
        self._draw(n, self.solutions[self.current_sol])

    def _next_sol(self):
        if not self.solutions: return
        n = int(self.n_entry.get())
        self.current_sol = (self.current_sol + 1) % len(self.solutions)
        self.sol_label.config(text=f"Solusi: {self.current_sol + 1} / {len(self.solutions)}")
        self._draw(n, self.solutions[self.current_sol])

    def _update_info(self, n, count):
        self.info_box.config(state="normal")
        self.info_box.delete("1.0", "end")
        info = (
            f"Algoritma:\nBacktracking\n\n"
            f"Ukuran N: {n}x{n}\n\n"
            f"Total Solusi:\n{count}\n\n"
            f"Kompleksitas:\nTime: O(N!)\nSpace: O(N²)\n\n"
            f"♛ = Posisi Ratu\n"
            f"■ = Petak Aman"
        )
        self.info_box.insert("1.0", info)
        self.info_box.config(state="disabled")


class KnightsTourPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(top, text="Knight's Tour", bg=BG, fg=ACCENT2, font=FONT_TITLE).pack(side="left")

        ctrl = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=24, pady=(0, 12))

        inner = tk.Frame(ctrl, bg=CARD)
        inner.pack(padx=16, pady=14, fill="x")

        tk.Label(inner, text="Ukuran (N)", bg=CARD, fg=TEXT2, font=FONT_SMALL).pack(side="left", padx=(0, 6))
        self.n_entry = make_entry(inner, width=5)
        self.n_entry.insert(0, "6")
        self.n_entry.pack(side="left", padx=(0, 14))

        tk.Label(inner, text="Baris Awal", bg=CARD, fg=TEXT2, font=FONT_SMALL).pack(side="left", padx=(0, 6))
        self.row_entry = make_entry(inner, width=5)
        self.row_entry.insert(0, "0")
        self.row_entry.pack(side="left", padx=(0, 14))

        tk.Label(inner, text="Kolom Awal", bg=CARD, fg=TEXT2, font=FONT_SMALL).pack(side="left", padx=(0, 6))
        self.col_entry = make_entry(inner, width=5)
        self.col_entry.insert(0, "0")
        self.col_entry.pack(side="left", padx=(0, 14))

        self.solve_btn = make_btn(inner, "▶  Solve", self._solve, color="#006644")
        self.solve_btn.pack(side="left")

        self.status = tk.Label(inner, text="", bg=CARD, fg=ACCENT2, font=FONT_SMALL)
        self.status.pack(side="left", padx=12)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=1)
        bottom.rowconfigure(0, weight=1)

        self.canvas_frame = tk.Frame(bottom, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.canvas = tk.Canvas(self.canvas_frame, bg=CARD, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=16)

        right = tk.Frame(bottom, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="LANGKAH", bg=CARD, fg=ACCENT2, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))

        sb = tk.Scrollbar(right, orient="vertical", bg=CARD)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=8)
        self.step_box = tk.Text(right, bg=CARD2, fg=TEXT, font=FONT_MONO, relief="flat",
                                state="disabled", wrap="word", bd=0, width=22,
                                highlightthickness=0, yscrollcommand=sb.set)
        self.step_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        sb.config(command=self.step_box.yview)

    def _solve(self):
        try:
            n = int(self.n_entry.get())
            r = int(self.row_entry.get())
            c = int(self.col_entry.get())
            if n < 1 or n > 8:
                messagebox.showwarning("Input", "N antara 1 - 8 (lebih besar = lebih lama)")
                return
            if not (0 <= r < n and 0 <= c < n):
                messagebox.showwarning("Input", "Posisi awal di luar papan")
                return
        except ValueError:
            messagebox.showwarning("Input", "Masukkan angka valid")
            return

        self.solve_btn.config(state="disabled", text="Solving...")
        self.status.config(text="Menghitung...")

        def run():
            board = solve_knights_tour(n, r, c)
            self.after(0, lambda: self._show(board, n, r, c))

        threading.Thread(target=run, daemon=True).start()

    def _show(self, board, n, sr, sc):
        self.solve_btn.config(state="normal", text="▶  Solve")
        if board is None:
            self.status.config(text="Tidak ada solusi")
            return
        self.status.config(text="Solusi ditemukan ✓")
        self._draw(board, n, sr, sc)
        self._fill_steps(board, n)

    def _draw(self, board, n, sr, sc):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 380
        h = self.canvas.winfo_height() or 380
        size = min(w, h) - 20
        cell = size // n
        ox = (w - cell * n) // 2
        oy = (h - cell * n) // 2
        max_step = n * n - 1

        for r in range(n):
            for c in range(n):
                step = board[r][c]
                ratio = step / max_step if max_step > 0 else 0
                r1 = int(0x16 + (0x00 - 0x16) * ratio)
                g1 = int(0x20 + (0xFF - 0x20) * ratio)
                b1 = int(0x30 + (0x9C - 0x30) * ratio)
                color = f"#{r1:02x}{g1:02x}{b1:02x}"
                self.canvas.create_rectangle(
                    ox + c * cell, oy + r * cell,
                    ox + (c + 1) * cell, oy + (r + 1) * cell,
                    fill=color, outline=BORDER, width=1)
                fs = max(7, cell // 3)
                self.canvas.create_text(ox + c * cell + cell // 2, oy + r * cell + cell // 2,
                                        text=str(step), fill=TEXT if ratio > 0.4 else TEXT2,
                                        font=("Consolas", fs, "bold"))
        cx = ox + sc * cell + cell // 2
        cy = oy + sr * cell + cell // 2
        r2 = cell * 0.2
        self.canvas.create_oval(cx - r2, cy - r2, cx + r2, cy + r2, fill=ACCENT3, outline="white", width=2)

    def _fill_steps(self, board, n):
        steps = [""] * (n * n)
        for r in range(n):
            for c in range(n):
                steps[board[r][c]] = (r, c)
        self.step_box.config(state="normal")
        self.step_box.delete("1.0", "end")
        for i, (r, c) in enumerate(steps):
            self.step_box.insert("end", f"Step {i:>3}: ({r},{c})\n")
        self.step_box.config(state="disabled")


class KnapsackPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(top, text="Knapsack Problem", bg=BG, fg=ACCENT3, font=FONT_TITLE).pack(side="left")

        ctrl = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=24, pady=(0, 12))

        inner = tk.Frame(ctrl, bg=CARD)
        inner.pack(padx=16, pady=14, fill="x")

        tk.Label(inner, text="Berat Barang\n(pisah koma)", bg=CARD, fg=TEXT2, font=FONT_SMALL, justify="left").pack(side="left", padx=(0, 6))
        self.weights_entry = make_entry(inner, width=28)
        self.weights_entry.insert(0, "2, 5, 6, 9, 12, 14, 20")
        self.weights_entry.pack(side="left", padx=(0, 14))

        tk.Label(inner, text="Target", bg=CARD, fg=TEXT2, font=FONT_SMALL).pack(side="left", padx=(0, 6))
        self.target_entry = make_entry(inner, width=7)
        self.target_entry.insert(0, "30")
        self.target_entry.pack(side="left", padx=(0, 14))

        self.solve_btn = make_btn(inner, "▶  Solve", self._solve, color="#6B2020")
        self.solve_btn.pack(side="left")

        self.status = tk.Label(inner, text="", bg=CARD, fg=ACCENT3, font=FONT_SMALL)
        self.status.pack(side="left", padx=12)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        bottom.columnconfigure(0, weight=3)
        bottom.columnconfigure(1, weight=2)
        bottom.rowconfigure(0, weight=1)

        left = tk.Frame(bottom, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(left, text="SEMUA SOLUSI", bg=CARD, fg=ACCENT3, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))

        sf = tk.Frame(left, bg=CARD)
        sf.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        sb = tk.Scrollbar(sf, orient="vertical", bg=CARD)
        sb.pack(side="right", fill="y")
        self.sol_listbox = tk.Listbox(sf, bg=CARD2, fg=TEXT, font=FONT_MONO, relief="flat",
                                      selectbackground=ACCENT3, selectforeground=BG,
                                      highlightthickness=0, bd=0, yscrollcommand=sb.set,
                                      activestyle="none")
        self.sol_listbox.pack(fill="both", expand=True)
        sb.config(command=self.sol_listbox.yview)
        self.sol_listbox.bind("<<ListboxSelect>>", self._on_select)

        right = tk.Frame(bottom, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="VISUALISASI", bg=CARD, fg=ACCENT3, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        self.canvas = tk.Canvas(right, bg=CARD, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._solutions = []
        self._weights = []
        self._target = 0

    def _solve(self):
        try:
            raw = self.weights_entry.get()
            weights = [int(x.strip()) for x in raw.split(",") if x.strip()]
            target = int(self.target_entry.get())
            if not weights:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input", "Format berat tidak valid")
            return

        self.solve_btn.config(state="disabled", text="Solving...")
        self.status.config(text="Mencari kombinasi...")

        def run():
            sols = solve_knapsack(weights, target)
            self.after(0, lambda: self._show(sols, weights, target))

        threading.Thread(target=run, daemon=True).start()

    def _show(self, sols, weights, target):
        self.solve_btn.config(state="normal", text="▶  Solve")
        self._solutions = sols
        self._weights = weights
        self._target = target
        self.sol_listbox.delete(0, "end")
        if not sols:
            self.status.config(text="Tidak ada solusi")
            self.sol_listbox.insert("end", "  Tidak ada kombinasi yang sesuai")
            return
        self.status.config(text=f"{len(sols)} solusi ditemukan ✓")
        for i, sol in enumerate(sols):
            total = sum(sol)
            items = " + ".join(str(w) for w in sol)
            self.sol_listbox.insert("end", f"  #{i+1:>3}  [{items}]  = {total}")
        self.sol_listbox.selection_set(0)
        self._draw_solution(sols[0], weights, target)

    def _on_select(self, event):
        sel = self.sol_listbox.curselection()
        if not sel or not self._solutions:
            return
        idx = sel[0]
        if idx < len(self._solutions):
            self._draw_solution(self._solutions[idx], self._weights, self._target)

    def _draw_solution(self, solution, all_weights, target):
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width() or 280
        h = self.canvas.winfo_height() or 340
        
        cx = w // 2
        bag_w, bag_h = min(160, w - 40), min(180, h - 120)
        bag_x = cx - bag_w // 2
        bag_y = h // 2 - bag_h // 2 + 20

        self.canvas.create_rectangle(bag_x, bag_y, bag_x + bag_w, bag_y + bag_h,
                                     fill=CARD2, outline=ACCENT3, width=2)
        self.canvas.create_text(cx, bag_y + bag_h // 2,
                                text=f"⚖ {sum(solution)}\n/{target}", fill=ACCENT3,
                                font=("Segoe UI", 14, "bold"), justify="center")

        total = sum(solution)
        fill_ratio = min(total / target, 1.0) if target > 0 else 0
        fill_h = int(bag_h * fill_ratio)
        if fill_h > 0:
            self.canvas.create_rectangle(bag_x + 2, bag_y + bag_h - fill_h,
                                         bag_x + bag_w - 2, bag_y + bag_h - 2,
                                         fill="#6B2020", outline="")

        self.canvas.create_text(cx, bag_y - 18, text="Kombinasi Terpilih:", fill=TEXT2, font=FONT_SMALL)

        sol_set = list(solution)
        x_start = 10
        y_item = 16
        for i, wt in enumerate(all_weights):
            col = x_start + (i % 3) * ((w - 20) // 3)
            row_y = y_item + (i // 3) * 30
            chosen = wt in sol_set
            if chosen:
                sol_set.remove(wt)
            bg_c = ACCENT3 if chosen else CARD2
            fg_c = BG if chosen else TEXT2
            self.canvas.create_rectangle(col, row_y, col + (w - 30) // 3 - 4, row_y + 22,
                                         fill=bg_c, outline=BORDER, width=1)
            self.canvas.create_text(col + (w - 30) // 6 - 2, row_y + 11,
                                    text=f"{wt}", fill=fg_c, font=FONT_MONO)