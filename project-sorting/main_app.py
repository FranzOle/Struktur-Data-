"""
main_app.py - Aplikasi Visualisasi Struktur Data
================================================
Antarmuka Tkinter untuk menampilkan animasi:
  1. Binary Search (custom target)
  2. Bubble Sort
  3. Merge 3 List
  4. Selection Sort
  5. Inversion Counter

Jalankan: python main_app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import sys
import os

# Import modul algoritma
sys.path.insert(0, os.path.dirname(__file__))
from binary_search import binary_search_steps
from bubble_sort import bubble_sort_steps
from merge_three import merge_three_steps
from selection_sort import selection_sort_steps
from inversion_counter import count_inversions_steps


# ─────────────────────────── Konstanta Warna ───────────────────────────
BG_DARK      = "#0f0f1a"
BG_PANEL     = "#1a1a2e"
BG_CARD      = "#16213e"
ACCENT_BLUE  = "#0f3460"
ACCENT_CYAN  = "#00d4ff"
ACCENT_GREEN = "#00ff88"
ACCENT_RED   = "#ff4757"
ACCENT_YELLOW= "#ffd32a"
ACCENT_PURPLE= "#7c4dff"
ACCENT_ORANGE= "#ff6b35"
TEXT_PRIMARY = "#e0e0ff"
TEXT_MUTED   = "#8888aa"
BAR_DEFAULT  = "#2979ff"
BAR_COMPARE  = "#ff6b35"
BAR_SWAP     = "#ff4757"
BAR_SORTED   = "#00ff88"
BAR_MIN      = "#ffd32a"
BAR_FOUND    = "#00ff88"
BAR_RANGE    = "#7c4dff"
BAR_MID      = "#ff4757"


# ─────────────────────────── Utilitas ───────────────────────────
def random_list(n=10, lo=1, hi=99):
    return random.sample(range(lo, hi+1), n)


# ─────────────────────────── Widget Bar Chart ───────────────────────────
class BarCanvas(tk.Canvas):
    """Canvas untuk menampilkan bar chart animasi."""

    def __init__(self, parent, **kw):
        kw.setdefault('bg', BG_CARD)
        kw.setdefault('highlightthickness', 0)
        super().__init__(parent, **kw)
        self._bars = []
        self._labels = []

    def draw_bars(self, values, colors=None, labels=None, title=""):
        self.delete("all")
        if not values:
            return
        w = self.winfo_width() or 700
        h = self.winfo_height() or 200
        pad_l, pad_r, pad_t, pad_b = 20, 20, 40, 30
        n = len(values)
        max_val = max(values) if values else 1
        bar_w = (w - pad_l - pad_r) / n
        chart_h = h - pad_t - pad_b

        if colors is None:
            colors = [BAR_DEFAULT] * n

        # Judul
        if title:
            self.create_text(w // 2, 14, text=title, fill=ACCENT_CYAN,
                             font=("Consolas", 10, "bold"))

        for i, val in enumerate(values):
            x0 = pad_l + i * bar_w + bar_w * 0.08
            x1 = pad_l + (i + 1) * bar_w - bar_w * 0.08
            bar_h = int(chart_h * val / max_val)
            y0 = h - pad_b - bar_h
            y1 = h - pad_b
            col = colors[i] if i < len(colors) else BAR_DEFAULT

            # Shadow
            self.create_rectangle(x0+3, y0+3, x1+3, y1, fill="#000033", outline="")
            # Bar
            self.create_rectangle(x0, y0, x1, y1, fill=col, outline=col,
                                   width=0)
            # Highlight di atas bar
            self.create_rectangle(x0, y0, x1, y0+4, fill=self._lighten(col),
                                   outline="")
            # Nilai di atas bar
            cx = (x0 + x1) / 2
            self.create_text(cx, y0 - 8, text=str(val),
                             fill=TEXT_PRIMARY, font=("Consolas", 8, "bold"))
            # Indeks di bawah bar
            lbl = labels[i] if labels and i < len(labels) else str(i)
            self.create_text(cx, y1 + 10, text=lbl,
                             fill=TEXT_MUTED, font=("Consolas", 7))

    @staticmethod
    def _lighten(hex_color):
        try:
            r = min(255, int(hex_color[1:3], 16) + 60)
            g = min(255, int(hex_color[3:5], 16) + 60)
            b = min(255, int(hex_color[5:7], 16) + 60)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color


# ─────────────────────────── Frame Dasar ───────────────────────────
class AlgoFrame(tk.Frame):
    """Frame dasar untuk setiap tab algoritma."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_PANEL, **kw)
        self._steps = []
        self._step_idx = 0
        self._running = False
        self._after_id = None
        self._speed = 700  # ms per langkah
        self._build_ui()

    def _build_ui(self):
        raise NotImplementedError

    def _btn(self, parent, text, cmd, color=ACCENT_BLUE, width=12):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=TEXT_PRIMARY, activebackground=ACCENT_CYAN,
                      activeforeground=BG_DARK, font=("Segoe UI", 9, "bold"),
                      relief="flat", bd=0, padx=8, pady=5,
                      cursor="hand2", width=width)
        b.bind("<Enter>", lambda e: b.config(bg=self._lighten(color)))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    @staticmethod
    def _lighten(hex_color):
        try:
            r = min(255, int(hex_color[1:3], 16) + 40)
            g = min(255, int(hex_color[3:5], 16) + 40)
            b = min(255, int(hex_color[5:7], 16) + 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def _label(self, parent, text, size=10, bold=False, color=TEXT_PRIMARY):
        style = "bold" if bold else "normal"
        return tk.Label(parent, text=text, bg=parent["bg"],
                        fg=color, font=("Segoe UI", size, style))

    def _entry(self, parent, width=30):
        e = tk.Entry(parent, bg=ACCENT_BLUE, fg=TEXT_PRIMARY,
                     insertbackground=ACCENT_CYAN, relief="flat",
                     font=("Consolas", 10), width=width,
                     highlightthickness=1, highlightcolor=ACCENT_CYAN,
                     highlightbackground="#334466")
        return e

    def _speed_bar(self, parent):
        f = tk.Frame(parent, bg=parent["bg"])
        tk.Label(f, text="⚡ Kecepatan:", bg=parent["bg"],
                 fg=TEXT_MUTED, font=("Segoe UI", 8)).pack(side="left")
        self._speed_var = tk.IntVar(value=700)
        s = ttk.Scale(f, from_=100, to=1500, orient="horizontal",
                      variable=self._speed_var, length=120,
                      command=lambda v: setattr(self, '_speed', int(float(v))))
        s.pack(side="left", padx=4)
        tk.Label(f, text="Lambat", bg=parent["bg"],
                 fg=TEXT_MUTED, font=("Segoe UI", 7)).pack(side="left")
        return f

    def _msg_box(self, parent, height=3):
        f = tk.Frame(parent, bg=BG_CARD, pady=4, padx=4)
        self._msg_var = tk.StringVar(value="Siap. Masukkan data dan klik Mulai Animasi.")
        lbl = tk.Label(f, textvariable=self._msg_var, bg=BG_CARD,
                       fg=ACCENT_CYAN, font=("Consolas", 9),
                       wraplength=700, justify="left", anchor="w",
                       height=height)
        lbl.pack(fill="x")
        return f

    def _step_label(self, parent):
        self._step_var = tk.StringVar(value="Langkah: 0 / 0")
        return tk.Label(parent, textvariable=self._step_var,
                        bg=parent["bg"], fg=TEXT_MUTED,
                        font=("Consolas", 8))

    def _play_controls(self, parent, on_run, on_prev, on_next, on_stop, on_reset):
        f = tk.Frame(parent, bg=parent["bg"])
        self._btn(f, "▶ Mulai", on_run, ACCENT_BLUE, 10).pack(side="left", padx=2)
        self._btn(f, "◀ Prev",  on_prev, "#334466", 8).pack(side="left", padx=2)
        self._btn(f, "Next ▶",  on_next, "#334466", 8).pack(side="left", padx=2)
        self._btn(f, "⏹ Stop",  on_stop, ACCENT_RED, 8).pack(side="left", padx=2)
        self._btn(f, "↺ Reset", on_reset, "#553344", 8).pack(side="left", padx=2)
        return f

    # ── Kontrol animasi umum ──────────────────────────────────
    def _start_anim(self):
        if not self._steps:
            return
        self._running = True
        self._step_idx = 0
        self._run_next()

    def _run_next(self):
        if not self._running or self._step_idx >= len(self._steps):
            self._running = False
            return
        self._render_step(self._steps[self._step_idx])
        self._step_var.set(f"Langkah: {self._step_idx+1} / {len(self._steps)}")
        self._step_idx += 1
        self._after_id = self.after(self._speed, self._run_next)

    def _prev_step(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
        if self._step_idx > 1:
            self._step_idx -= 2
            self._render_step(self._steps[self._step_idx])
            self._step_var.set(f"Langkah: {self._step_idx+1} / {len(self._steps)}")
            self._step_idx += 1

    def _next_step(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
        if self._step_idx < len(self._steps):
            self._render_step(self._steps[self._step_idx])
            self._step_var.set(f"Langkah: {self._step_idx+1} / {len(self._steps)}")
            self._step_idx += 1

    def _stop_anim(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)

    def _render_step(self, step):
        raise NotImplementedError


# ═══════════════════════════════════════════════════════════════
# TAB 1: Binary Search
# ═══════════════════════════════════════════════════════════════
class BinarySearchFrame(AlgoFrame):

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # ── Header ──
        hdr = tk.Frame(self, bg=BG_PANEL, pady=6)
        hdr.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(hdr, text="🔍  BINARY SEARCH", bg=BG_PANEL,
                 fg=ACCENT_CYAN, font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(hdr, text="  Cari elemen target dalam array terurut",
                 bg=BG_PANEL, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left", padx=8)

        # ── Input Panel ──
        inp = tk.Frame(self, bg=BG_CARD, padx=10, pady=8)
        inp.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        # Baris 1: array
        r1 = tk.Frame(inp, bg=BG_CARD)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Array (pisah koma):", bg=BG_CARD,
                 fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left")
        self._arr_entry = self._entry(r1, 35)
        self._arr_entry.pack(side="left", padx=6)
        self._arr_entry.insert(0, ", ".join(map(str, random_list(12))))
        self._btn(r1, "🎲 Acak", self._randomize, "#334455", 8).pack(side="left")

        # Baris 2: target
        r2 = tk.Frame(inp, bg=BG_CARD)
        r2.pack(fill="x", pady=2)
        tk.Label(r2, text="Target (angka):", bg=BG_CARD,
                 fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left")
        self._tgt_entry = self._entry(r2, 8)
        self._tgt_entry.pack(side="left", padx=6)

        # Baris 3: kontrol
        r3 = tk.Frame(inp, bg=BG_CARD)
        r3.pack(fill="x", pady=4)
        self._play_controls(r3, self._run, self._prev_step,
                            self._next_step, self._stop_anim, self._reset).pack(side="left")
        self._speed_bar(r3).pack(side="left", padx=20)
        self._step_label(r3).pack(side="right")

        # ── Legenda ──
        leg = tk.Frame(inp, bg=BG_CARD)
        leg.pack(fill="x")
        for col, txt in [(BAR_RANGE, "Rentang Aktif"), (BAR_MID, "Tengah"),
                         (BAR_FOUND, "Ditemukan"), (BAR_DEFAULT, "Di luar rentang")]:
            tk.Label(leg, text="■", bg=BG_CARD, fg=col, font=("Segoe UI", 11)).pack(side="left")
            tk.Label(leg, text=txt+"  ", bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Segoe UI", 8)).pack(side="left")

        # ── Canvas ──
        self._canvas = BarCanvas(self, height=240)
        self._canvas.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)

        # ── Pesan ──
        self._msg_box(self).grid(row=3, column=0, sticky="ew", padx=10, pady=2)

    def _randomize(self):
        self._arr_entry.delete(0, "end")
        self._arr_entry.insert(0, ", ".join(map(str, random_list(12))))

    def _parse(self):
        try:
            arr = [int(x.strip()) for x in self._arr_entry.get().split(",") if x.strip()]
            tgt = int(self._tgt_entry.get().strip())
            return arr, tgt
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan angka yang valid!\nArray: pisah koma\nTarget: satu angka")
            return None, None

    def _run(self):
        arr, tgt = self._parse()
        if arr is None:
            return
        self._sorted_arr, self._steps = binary_search_steps(arr, tgt)
        self._step_idx = 0
        self._start_anim()

    def _reset(self):
        self._stop_anim()
        self._steps = []
        self._step_idx = 0
        self._step_var.set("Langkah: 0 / 0")
        self._msg_var.set("Siap. Masukkan array, target, lalu klik Mulai.")
        self._canvas.delete("all")

    def _render_step(self, step):
        arr = step['array']
        lo, hi, mid = step['low'], step['high'], step['mid']
        status = step['status']
        self._msg_var.set(step['message'])
        colors = []
        for i in range(len(arr)):
            if status == 'found' and i == mid:
                colors.append(BAR_FOUND)
            elif status == 'not_found':
                colors.append(BAR_COMPARE)
            elif i == mid:
                colors.append(BAR_MID)
            elif lo <= i <= hi:
                colors.append(BAR_RANGE)
            else:
                colors.append(TEXT_MUTED)
        self._canvas.draw_bars(arr, colors,
                               title=f"Target={step['target']} | Low={lo} Mid={mid} High={hi}")


# ═══════════════════════════════════════════════════════════════
# TAB 2: Bubble Sort
# ═══════════════════════════════════════════════════════════════
class BubbleSortFrame(AlgoFrame):

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        hdr = tk.Frame(self, bg=BG_PANEL, pady=6)
        hdr.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(hdr, text="🫧  BUBBLE SORT", bg=BG_PANEL,
                 fg=ACCENT_CYAN, font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(hdr, text="  Gelembungkan elemen terbesar ke kanan",
                 bg=BG_PANEL, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left", padx=8)

        inp = tk.Frame(self, bg=BG_CARD, padx=10, pady=8)
        inp.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        r1 = tk.Frame(inp, bg=BG_CARD)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Array (pisah koma):", bg=BG_CARD,
                 fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left")
        self._arr_entry = self._entry(r1, 40)
        self._arr_entry.pack(side="left", padx=6)
        self._arr_entry.insert(0, ", ".join(map(str, random_list(10))))
        self._btn(r1, "🎲 Acak", self._randomize, "#334455", 8).pack(side="left")

        r2 = tk.Frame(inp, bg=BG_CARD)
        r2.pack(fill="x", pady=4)
        self._play_controls(r2, self._run, self._prev_step,
                            self._next_step, self._stop_anim, self._reset).pack(side="left")
        self._speed_bar(r2).pack(side="left", padx=20)
        self._step_label(r2).pack(side="right")

        leg = tk.Frame(inp, bg=BG_CARD)
        leg.pack(fill="x")
        for col, txt in [(BAR_COMPARE, "Dibandingkan"), (BAR_SWAP, "Swap"),
                         (BAR_SORTED, "Sudah Terurut"), (BAR_DEFAULT, "Normal")]:
            tk.Label(leg, text="■", bg=BG_CARD, fg=col, font=("Segoe UI", 11)).pack(side="left")
            tk.Label(leg, text=txt+"  ", bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Segoe UI", 8)).pack(side="left")

        self._canvas = BarCanvas(self, height=240)
        self._canvas.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        self._msg_box(self).grid(row=3, column=0, sticky="ew", padx=10, pady=2)

    def _randomize(self):
        self._arr_entry.delete(0, "end")
        self._arr_entry.insert(0, ", ".join(map(str, random_list(10))))

    def _parse(self):
        try:
            return [int(x.strip()) for x in self._arr_entry.get().split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan angka yang valid, pisah dengan koma!")
            return None

    def _run(self):
        arr = self._parse()
        if arr is None:
            return
        _, self._steps = bubble_sort_steps(arr)
        self._step_idx = 0
        self._start_anim()

    def _reset(self):
        self._stop_anim(); self._steps = []; self._step_idx = 0
        self._step_var.set("Langkah: 0 / 0")
        self._msg_var.set("Siap.")
        self._canvas.delete("all")

    def _render_step(self, step):
        arr = step['array']
        cmp = step.get('compare', [])
        sb = step.get('sorted_boundary', len(arr))
        is_swap = step.get('swap', False)
        self._msg_var.set(step['message'])
        colors = []
        for i in range(len(arr)):
            if i in cmp:
                colors.append(BAR_SWAP if is_swap else BAR_COMPARE)
            elif i >= sb:
                colors.append(BAR_SORTED)
            else:
                colors.append(BAR_DEFAULT)
        self._canvas.draw_bars(arr, colors)


# ═══════════════════════════════════════════════════════════════
# TAB 3: Merge 3 List
# ═══════════════════════════════════════════════════════════════
class MergeThreeFrame(AlgoFrame):

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        hdr = tk.Frame(self, bg=BG_PANEL, pady=6)
        hdr.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(hdr, text="🔀  MERGE 3 LIST", bg=BG_PANEL,
                 fg=ACCENT_CYAN, font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(hdr, text="  Gabungkan 3 list terurut menjadi satu",
                 bg=BG_PANEL, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left", padx=8)

        inp = tk.Frame(self, bg=BG_CARD, padx=10, pady=8)
        inp.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        labels_txt = ["List 1:", "List 2:", "List 3:"]
        defaults = [
            ", ".join(map(str, sorted(random_list(5)))),
            ", ".join(map(str, sorted(random_list(5)))),
            ", ".join(map(str, sorted(random_list(5)))),
        ]
        self._entries = []
        for i, (lbl, dflt) in enumerate(zip(labels_txt, defaults)):
            row = tk.Frame(inp, bg=BG_CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Segoe UI", 9), width=8, anchor="e").pack(side="left")
            e = self._entry(row, 30)
            e.pack(side="left", padx=6)
            e.insert(0, dflt)
            self._entries.append(e)

        r_rand = tk.Frame(inp, bg=BG_CARD)
        r_rand.pack(fill="x", pady=2)
        self._btn(r_rand, "🎲 Acak Semua", self._randomize, "#334455", 12).pack(side="left")

        r_ctrl = tk.Frame(inp, bg=BG_CARD)
        r_ctrl.pack(fill="x", pady=4)
        self._play_controls(r_ctrl, self._run, self._prev_step,
                            self._next_step, self._stop_anim, self._reset).pack(side="left")
        self._speed_bar(r_ctrl).pack(side="left", padx=20)
        self._step_label(r_ctrl).pack(side="right")

        # Canvas area: 3 list + result
        canvas_frame = tk.Frame(self, bg=BG_PANEL)
        canvas_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.columnconfigure(1, weight=2)
        canvas_frame.rowconfigure(0, weight=1)

        left = tk.Frame(canvas_frame, bg=BG_PANEL)
        left.grid(row=0, column=0, sticky="nsew")
        for attr, lbl in [('_c1', 'List 1'), ('_c2', 'List 2'), ('_c3', 'List 3')]:
            tk.Label(left, text=lbl, bg=BG_PANEL, fg=TEXT_MUTED,
                     font=("Consolas", 8)).pack(fill="x", padx=4)
            c = BarCanvas(left, height=65)
            c.pack(fill="x", padx=4, pady=1)
            setattr(self, attr, c)

        right = tk.Frame(canvas_frame, bg=BG_PANEL)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Hasil Merge", bg=BG_PANEL, fg=ACCENT_GREEN,
                 font=("Consolas", 9, "bold")).pack(fill="x", padx=4)
        self._c_result = BarCanvas(right, height=200)
        self._c_result.pack(fill="both", expand=True, padx=4, pady=1)

        self._msg_box(self).grid(row=3, column=0, sticky="ew", padx=10, pady=2)

    def _randomize(self):
        for e in self._entries:
            e.delete(0, "end")
            e.insert(0, ", ".join(map(str, sorted(random_list(5)))))

    def _parse(self):
        try:
            lists = []
            for e in self._entries:
                lst = [int(x.strip()) for x in e.get().split(",") if x.strip()]
                lists.append(lst)
            return lists
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan angka yang valid!")
            return None

    def _run(self):
        lists = self._parse()
        if not lists:
            return
        _, self._steps = merge_three_steps(*lists)
        self._step_idx = 0
        self._start_anim()

    def _reset(self):
        self._stop_anim(); self._steps = []; self._step_idx = 0
        self._step_var.set("Langkah: 0 / 0")
        self._msg_var.set("Siap.")
        for c in [self._c1, self._c2, self._c3, self._c_result]:
            c.delete("all")

    def _render_step(self, step):
        self._msg_var.set(step['message'])
        pf = step.get('picked_from', -1)
        p = step.get('picked', -1)

        def make_colors(lst, ptr, is_picked):
            cols = []
            for i in range(len(lst)):
                if i == ptr - 1 and is_picked:
                    cols.append(ACCENT_GREEN)
                elif i < ptr:
                    cols.append(TEXT_MUTED)
                elif i == ptr:
                    cols.append(ACCENT_ORANGE)
                else:
                    cols.append(BAR_DEFAULT)
            return cols

        l1, l2, l3 = step['list1'], step['list2'], step['list3']
        p1, p2, p3 = step['ptr1'], step['ptr2'], step['ptr3']
        self._c1.draw_bars(l1, make_colors(l1, p1, pf == 0))
        self._c2.draw_bars(l2, make_colors(l2, p2, pf == 1))
        self._c3.draw_bars(l3, make_colors(l3, p3, pf == 2))

        res = step.get('result', [])
        r_colors = [BAR_SORTED] * (len(res) - 1) + ([ACCENT_GREEN] if res else [])
        self._c_result.draw_bars(res, r_colors, title=f"Merged ({len(res)} elemen)")


# ═══════════════════════════════════════════════════════════════
# TAB 4: Selection Sort
# ═══════════════════════════════════════════════════════════════
class SelectionSortFrame(AlgoFrame):

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        hdr = tk.Frame(self, bg=BG_PANEL, pady=6)
        hdr.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(hdr, text="🎯  SELECTION SORT", bg=BG_PANEL,
                 fg=ACCENT_CYAN, font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(hdr, text="  Pilih minimum, tempatkan ke posisi benar",
                 bg=BG_PANEL, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left", padx=8)

        inp = tk.Frame(self, bg=BG_CARD, padx=10, pady=8)
        inp.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        r1 = tk.Frame(inp, bg=BG_CARD)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Array (pisah koma):", bg=BG_CARD,
                 fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left")
        self._arr_entry = self._entry(r1, 40)
        self._arr_entry.pack(side="left", padx=6)
        self._arr_entry.insert(0, ", ".join(map(str, random_list(10))))
        self._btn(r1, "🎲 Acak", self._randomize, "#334455", 8).pack(side="left")

        r2 = tk.Frame(inp, bg=BG_CARD)
        r2.pack(fill="x", pady=4)
        self._play_controls(r2, self._run, self._prev_step,
                            self._next_step, self._stop_anim, self._reset).pack(side="left")
        self._speed_bar(r2).pack(side="left", padx=20)
        self._step_label(r2).pack(side="right")

        leg = tk.Frame(inp, bg=BG_CARD)
        leg.pack(fill="x")
        for col, txt in [(ACCENT_ORANGE, "Posisi Sekarang"), (BAR_MIN, "Minimum"),
                         (BAR_COMPARE, "Sedang Diperiksa"), (BAR_SORTED, "Terurut"),
                         (BAR_SWAP, "Swap"), (BAR_DEFAULT, "Normal")]:
            tk.Label(leg, text="■", bg=BG_CARD, fg=col, font=("Segoe UI", 11)).pack(side="left")
            tk.Label(leg, text=txt+"  ", bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Segoe UI", 8)).pack(side="left")

        self._canvas = BarCanvas(self, height=240)
        self._canvas.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        self._msg_box(self).grid(row=3, column=0, sticky="ew", padx=10, pady=2)

    def _randomize(self):
        self._arr_entry.delete(0, "end")
        self._arr_entry.insert(0, ", ".join(map(str, random_list(10))))

    def _parse(self):
        try:
            return [int(x.strip()) for x in self._arr_entry.get().split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan angka yang valid!")
            return None

    def _run(self):
        arr = self._parse()
        if arr is None:
            return
        _, self._steps = selection_sort_steps(arr)
        self._step_idx = 0
        self._start_anim()

    def _reset(self):
        self._stop_anim(); self._steps = []; self._step_idx = 0
        self._step_var.set("Langkah: 0 / 0")
        self._msg_var.set("Siap.")
        self._canvas.delete("all")

    def _render_step(self, step):
        arr = step['array']
        cur = step.get('current_pos', -1)
        mn = step.get('min_idx', -1)
        scn = step.get('scanning', -1)
        su = step.get('sorted_until', 0)
        is_swap = step.get('swapped', False)
        self._msg_var.set(step['message'])
        colors = []
        for i in range(len(arr)):
            if i < su:
                colors.append(BAR_SORTED)
            elif is_swap and (i == cur or i == mn):
                colors.append(BAR_SWAP)
            elif i == mn:
                colors.append(BAR_MIN)
            elif i == scn:
                colors.append(BAR_COMPARE)
            elif i == cur:
                colors.append(ACCENT_ORANGE)
            else:
                colors.append(BAR_DEFAULT)
        self._canvas.draw_bars(arr, colors)


# ═══════════════════════════════════════════════════════════════
# TAB 5: Inversion Counter
# ═══════════════════════════════════════════════════════════════
class InversionFrame(AlgoFrame):

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        hdr = tk.Frame(self, bg=BG_PANEL, pady=6)
        hdr.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(hdr, text="🔄  INVERSION COUNTER", bg=BG_PANEL,
                 fg=ACCENT_CYAN, font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(hdr, text="  Hitung pasangan (i,j) dimana i<j tapi arr[i]>arr[j]",
                 bg=BG_PANEL, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left", padx=8)

        inp = tk.Frame(self, bg=BG_CARD, padx=10, pady=8)
        inp.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        r1 = tk.Frame(inp, bg=BG_CARD)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Array (pisah koma):", bg=BG_CARD,
                 fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left")
        self._arr_entry = self._entry(r1, 40)
        self._arr_entry.pack(side="left", padx=6)
        self._arr_entry.insert(0, ", ".join(map(str, random_list(8))))
        self._btn(r1, "🎲 Acak", self._randomize, "#334455", 8).pack(side="left")

        r2 = tk.Frame(inp, bg=BG_CARD)
        r2.pack(fill="x", pady=4)
        self._play_controls(r2, self._run, self._prev_step,
                            self._next_step, self._stop_anim, self._reset).pack(side="left")
        self._speed_bar(r2).pack(side="left", padx=20)
        self._step_label(r2).pack(side="right")

        # Counter badge
        badge = tk.Frame(inp, bg=BG_CARD)
        badge.pack(fill="x")
        tk.Label(badge, text="Total Inversi:", bg=BG_CARD, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        self._inv_var = tk.StringVar(value="—")
        tk.Label(badge, textvariable=self._inv_var, bg=BG_CARD, fg=ACCENT_RED,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=8)

        # Dua canvas: bar chart + daftar inversi
        mid_frame = tk.Frame(self, bg=BG_PANEL)
        mid_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        mid_frame.columnconfigure(0, weight=2)
        mid_frame.columnconfigure(1, weight=1)
        mid_frame.rowconfigure(0, weight=1)

        self._canvas = BarCanvas(mid_frame, height=200)
        self._canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        # Panel inversi list
        rp = tk.Frame(mid_frame, bg=BG_CARD)
        rp.grid(row=0, column=1, sticky="nsew")
        tk.Label(rp, text="Pasangan Inversi", bg=BG_CARD, fg=ACCENT_ORANGE,
                 font=("Consolas", 9, "bold")).pack(fill="x", pady=4)
        self._inv_listbox = tk.Listbox(rp, bg=BG_CARD, fg=ACCENT_ORANGE,
                                        font=("Consolas", 8), selectbackground=ACCENT_BLUE,
                                        relief="flat", highlightthickness=0,
                                        activestyle="none")
        self._inv_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        sb = ttk.Scrollbar(rp, orient="vertical", command=self._inv_listbox.yview)
        sb.pack(side="right", fill="y")
        self._inv_listbox.config(yscrollcommand=sb.set)

        self._msg_box(self).grid(row=3, column=0, sticky="ew", padx=10, pady=2)

    def _randomize(self):
        self._arr_entry.delete(0, "end")
        self._arr_entry.insert(0, ", ".join(map(str, random_list(8))))

    def _parse(self):
        try:
            return [int(x.strip()) for x in self._arr_entry.get().split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan angka yang valid!")
            return None

    def _run(self):
        arr = self._parse()
        if arr is None:
            return
        _, total, pairs, self._steps = count_inversions_steps(arr)
        self._all_pairs = pairs
        self._step_idx = 0
        self._inv_var.set("—")
        self._inv_listbox.delete(0, "end")
        self._start_anim()

    def _reset(self):
        self._stop_anim(); self._steps = []; self._step_idx = 0
        self._step_var.set("Langkah: 0 / 0")
        self._msg_var.set("Siap.")
        self._inv_var.set("—")
        self._inv_listbox.delete(0, "end")
        self._canvas.delete("all")

    def _render_step(self, step):
        arr = step['array']
        hl = step.get('highlight', [])
        pairs = step.get('inv_pairs', [])
        count = step.get('count', 0)
        phase = step.get('phase', '')
        self._msg_var.set(step['message'])

        colors = []
        for i in range(len(arr)):
            if phase == 'done':
                colors.append(BAR_SORTED)
            elif i in hl:
                colors.append(BAR_SWAP)
            else:
                colors.append(BAR_DEFAULT)
        self._canvas.draw_bars(arr, colors,
                               title=f"Array | Inversi ditemukan: {count}")

        if count > 0:
            self._inv_var.set(str(count))

        # Update listbox
        self._inv_listbox.delete(0, "end")
        for pi, (i, j, vi, vj) in enumerate(pairs):
            self._inv_listbox.insert("end", f"#{pi+1}: [{i}]={vi} > [{j}]={vj}")
        if self._inv_listbox.size() > 0:
            self._inv_listbox.see("end")


# ═══════════════════════════════════════════════════════════════
# Aplikasi Utama
# ═══════════════════════════════════════════════════════════════
class DataStructureApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("🧠 Visualisasi Struktur Data & Algoritma")
        self.geometry("900x640")
        self.minsize(780, 540)
        self.configure(bg=BG_DARK)
        self._build_ui()
        self.mainloop()

    def _build_ui(self):
        # ── Top bar ──
        top = tk.Frame(self, bg=ACCENT_BLUE, height=48)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="  🧠 VISUALIZER STRUKTUR DATA",
                 bg=ACCENT_BLUE, fg=ACCENT_CYAN,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=12, pady=8)
        tk.Label(top, text="Struktur Data  •  Sorting  •  Animasi Interaktif",
                 bg=ACCENT_BLUE, fg=TEXT_MUTED,
                 font=("Segoe UI", 8)).pack(side="right", padx=16)

        # ── Notebook (tab) ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        background=BG_CARD, foreground=TEXT_MUTED,
                        font=("Segoe UI", 9, "bold"),
                        padding=[14, 6])
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", ACCENT_CYAN)])

        nb = ttk.Notebook(self, style="Custom.TNotebook")
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        tabs = [
            ("🔍 Binary Search",   BinarySearchFrame),
            ("🫧 Bubble Sort",     BubbleSortFrame),
            ("🔀 Merge 3 List",    MergeThreeFrame),
            ("🎯 Selection Sort",  SelectionSortFrame),
            ("🔄 Inversion Count", InversionFrame),
        ]
        for title, FrameClass in tabs:
            frame = FrameClass(nb)
            nb.add(frame, text=title)

        # ── Status bar ──
        sb = tk.Frame(self, bg="#0a0a15", height=22)
        sb.pack(fill="x", side="bottom")
        tk.Label(sb, text="  Tip: Gunakan tombol Prev/Next untuk langkah manual · Slider kecepatan untuk mengatur kecepatan animasi",
                 bg="#0a0a15", fg=TEXT_MUTED, font=("Segoe UI", 7)).pack(side="left")


# ─────────────────────────── Entry Point ───────────────────────────
if __name__ == "__main__":
    DataStructureApp()
