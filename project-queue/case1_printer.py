import tkinter as tk
from tkinter import ttk
from collections import deque
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
    "printer_idle": "#37474f",
    "printer_busy": "#1565c0",
}

DOC_ICONS = {"pdf": "📄", "docx": "📝", "jpg": "🖼️", "txt": "📃", "xlsx": "📊"}

def get_doc_icon(name):
    ext = name.split(".")[-1].lower() if "." in name else "txt"
    return DOC_ICONS.get(ext, "📄")


class PrinterQueueFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self.queue = deque()
        self.printing = False
        self.print_job = None
        self.log_entries = []
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self, bg=COLORS["bg"])
        title_frame.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(title_frame, text="🖨️  Antrian Printer Bersama",
                 font=("Segoe UI", 18, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(title_frame, text="Simulasi FIFO — dokumen dicetak sesuai urutan kedatangan",
                 font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=30, pady=10)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                        highlightbackground=COLORS["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        printer_section = tk.Frame(left, bg=COLORS["panel"])
        printer_section.pack(fill="x", padx=20, pady=15)
        tk.Label(printer_section, text="STATUS PRINTER", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        self.printer_canvas = tk.Canvas(printer_section, width=280, height=130,
                                        bg=COLORS["panel"], highlightthickness=0)
        self.printer_canvas.pack(pady=8)
        self._draw_printer()

        queue_section = tk.Frame(left, bg=COLORS["panel"])
        queue_section.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        tk.Label(queue_section, text="ANTRIAN DOKUMEN", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        queue_container = tk.Frame(queue_section, bg=COLORS["card"], bd=0,
                                   highlightthickness=1, highlightbackground=COLORS["border"])
        queue_container.pack(fill="both", expand=True, pady=6)

        self.queue_canvas = tk.Canvas(queue_container, bg=COLORS["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(queue_container, orient="vertical", command=self.queue_canvas.yview)
        self.queue_frame = tk.Frame(self.queue_canvas, bg=COLORS["card"])
        self.queue_frame.bind("<Configure>",
                              lambda e: self.queue_canvas.configure(scrollregion=self.queue_canvas.bbox("all")))
        self.queue_canvas.create_window((0, 0), window=self.queue_frame, anchor="nw")
        self.queue_canvas.configure(yscrollcommand=scrollbar.set)
        self.queue_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        right = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1,
                         highlightbackground=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew")

        input_section = tk.Frame(right, bg=COLORS["panel"])
        input_section.pack(fill="x", padx=20, pady=15)
        tk.Label(input_section, text="KIRIM DOKUMEN", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")

        entry_frame = tk.Frame(input_section, bg=COLORS["panel"])
        entry_frame.pack(fill="x", pady=6)
        self.doc_entry = tk.Entry(entry_frame, font=("Segoe UI", 11), bg=COLORS["card"],
                                  fg=COLORS["text"], insertbackground=COLORS["accent"],
                                  relief="flat", bd=8)
        self.doc_entry.pack(fill="x", ipady=4)
        self.doc_entry.insert(0, "laporan.pdf")
        self.doc_entry.bind("<Return>", lambda e: self._enqueue())

        btn_frame = tk.Frame(input_section, bg=COLORS["panel"])
        btn_frame.pack(fill="x", pady=4)
        tk.Button(btn_frame, text="  📥  Enqueue", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["accent"], fg="#000", relief="flat", bd=0, padx=12, pady=6,
                  cursor="hand2", command=self._enqueue).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="  🖨️  Cetak", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["success"], fg="#000", relief="flat", bd=0, padx=12, pady=6,
                  cursor="hand2", command=self._start_print).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="Reset", font=("Segoe UI", 9),
                  bg=COLORS["danger"], fg="#fff", relief="flat", bd=0, padx=10, pady=6,
                  cursor="hand2", command=self._reset).pack(side="left")

        preset_frame = tk.Frame(input_section, bg=COLORS["panel"])
        preset_frame.pack(fill="x", pady=4)
        tk.Label(preset_frame, text="Preset:", font=("Segoe UI", 9),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(side="left", padx=(0, 6))
        for name in ["laporan.pdf", "tugas.docx", "foto.jpg", "data.xlsx"]:
            tk.Button(preset_frame, text=name, font=("Segoe UI", 8),
                      bg=COLORS["card"], fg=COLORS["accent"], relief="flat", bd=0, padx=6, pady=3,
                      cursor="hand2",
                      command=lambda n=name: self._quick_add(n)).pack(side="left", padx=2)

        stats_frame = tk.Frame(right, bg=COLORS["panel"])
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(stats_frame, text="STATISTIK", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        stat_row = tk.Frame(stats_frame, bg=COLORS["panel"])
        stat_row.pack(fill="x", pady=4)
        self.stat_labels = {}
        for key, label, color in [("queued", "Antrian", COLORS["warning"]),
                                   ("printed", "Dicetak", COLORS["success"]),
                                   ("total", "Total", COLORS["accent"])]:
            box = tk.Frame(stat_row, bg=COLORS["card"], bd=0, highlightthickness=1,
                           highlightbackground=COLORS["border"])
            box.pack(side="left", expand=True, fill="x", padx=3)
            tk.Label(box, text=label, font=("Segoe UI", 8), bg=COLORS["card"],
                     fg=COLORS["subtext"]).pack(pady=(6, 0))
            lbl = tk.Label(box, text="0", font=("Segoe UI", 20, "bold"),
                           bg=COLORS["card"], fg=color)
            lbl.pack(pady=(0, 6))
            self.stat_labels[key] = lbl

        log_section = tk.Frame(right, bg=COLORS["panel"])
        log_section.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        tk.Label(log_section, text="LOG AKTIVITAS", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["panel"], fg=COLORS["subtext"]).pack(anchor="w")
        self.log_text = tk.Text(log_section, font=("Consolas", 9), bg=COLORS["card"],
                                fg=COLORS["text"], relief="flat", bd=0, state="disabled",
                                height=10, wrap="word")
        self.log_text.pack(fill="both", expand=True, pady=6)
        self.log_text.tag_config("enqueue", foreground=COLORS["accent"])
        self.log_text.tag_config("print", foreground=COLORS["success"])
        self.log_text.tag_config("done", foreground=COLORS["warning"])
        self.log_text.tag_config("error", foreground=COLORS["danger"])

        self._update_stats()

    def _draw_printer(self, busy=False, doc_name=None):
        c = self.printer_canvas
        c.delete("all")
        color = COLORS["printer_busy"] if busy else COLORS["printer_idle"]
        c.create_rectangle(50, 30, 230, 100, fill=color, outline=COLORS["border"], width=2)
        c.create_rectangle(80, 15, 200, 35, fill=COLORS["card"], outline=COLORS["border"], width=1)
        c.create_rectangle(70, 95, 210, 110, fill=COLORS["card"], outline=COLORS["border"], width=1)
        light_color = COLORS["success"] if busy else COLORS["subtext"]
        for i, x in enumerate([70, 85]):
            c.create_oval(x, 55, x+10, 65, fill=light_color if i == 0 else COLORS["subtext"],
                          outline="")
            
        status = f"⚡ Mencetak: {doc_name}" if busy else "💤 Idle — Menunggu dokumen"
        c.create_text(140, 78, text=status, fill=COLORS["text"],
                      font=("Segoe UI", 9, "bold" if busy else "normal"))
        if busy:
            c.create_rectangle(110, 88, 170, 108, fill="white", outline=COLORS["accent"], width=1)
            c.create_text(140, 98, text=get_doc_icon(doc_name or ""), font=("Segoe UI", 8))

    def _enqueue(self):
        name = self.doc_entry.get().strip()
        if not name:
            return
        self.queue.append(name)
        self._log(f"[ENQUEUE] {get_doc_icon(name)} {name} masuk antrian (posisi {len(self.queue)})", "enqueue")
        self._refresh_queue_view()
        self._update_stats()
        self.doc_entry.delete(0, "end")

    def _quick_add(self, name):
        self.doc_entry.delete(0, "end")
        self.doc_entry.insert(0, name)
        self._enqueue()

    def _start_print(self):
        if self.printing:
            self._log("[ERROR] Printer sedang sibuk!", "error")
            return
        if not self.queue:
            self._log("[ERROR] Antrian kosong! Tidak ada yang dicetak.", "error")
            return
        self._print_next()

    def _print_next(self):
        if not self.queue:
            self.printing = False
            self._draw_printer(busy=False)
            self._log("[DONE] Semua dokumen selesai dicetak! ✅", "done")
            return
        self.printing = True
        doc = self.queue.popleft()
        self._log(f"[DEQUEUE] 🖨️  Mencetak: {doc}...", "print")
        self._draw_printer(busy=True, doc_name=doc)
        self._refresh_queue_view()
        self._update_stats(doc)
        self.print_job = self.after(2000, lambda: self._finish_print(doc))

    def _finish_print(self, doc):
        self._log(f"[DONE] ✅ {doc} selesai dicetak!", "done")
        self.printed = getattr(self, "printed", 0) + 1
        self._update_stats()
        self._print_next()

    def _reset(self):
        if self.print_job:
            self.after_cancel(self.print_job)
        self.queue.clear()
        self.printing = False
        self.printed = 0
        self._draw_printer()
        self._refresh_queue_view()
        self._update_stats()
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self._log("[RESET] Sistem direset. 🔄", "done")

    def _refresh_queue_view(self):
        for w in self.queue_frame.winfo_children():
            w.destroy()
        if not self.queue:
            tk.Label(self.queue_frame, text="Antrian kosong", font=("Segoe UI", 10),
                     bg=COLORS["card"], fg=COLORS["subtext"], pady=20).pack()
            return
        for i, doc in enumerate(self.queue):
            row = tk.Frame(self.queue_frame, bg=COLORS["card"])
            row.pack(fill="x", pady=2, padx=8)
            bg = COLORS["accent"] if i == 0 else COLORS["panel"]
            fg_color = "#000" if i == 0 else COLORS["text"]
            tag = "  NEXT  " if i == 0 else f"  #{i+1}  "
            tk.Label(row, text=tag, font=("Segoe UI", 8, "bold"),
                     bg=bg, fg=fg_color, padx=4, pady=4).pack(side="left")
            tk.Label(row, text=f"{get_doc_icon(doc)}  {doc}",
                     font=("Segoe UI", 10), bg=COLORS["card"], fg=COLORS["text"],
                     pady=4).pack(side="left", padx=8)

    def _update_stats(self, current=None):
        queued = len(self.queue)
        printed = getattr(self, "printed", 0)
        self.stat_labels["queued"].config(text=str(queued))
        self.stat_labels["printed"].config(text=str(printed))
        self.stat_labels["total"].config(text=str(queued + printed))

    def _log(self, msg, tag=""):
        self.log_text.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")