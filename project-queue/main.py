import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from case1_printer import PrinterQueueFrame
from case2_hotpotato import HotPotatoFrame
from case3_hospital import HospitalQueueFrame
from case4_bfs import BFSFrame
from case5_airport import AirportSimFrame

BG = "#0f0f1a"
PANEL = "#1a1a2e"
ACCENT = "#4fc3f7"
TEXT = "#e0e0e0"
SUBTEXT = "#90a4ae"
CARD = "#16213e"
BORDER = "#1e3a5f"

TABS = [
    ("🖨️  Printer", PrinterQueueFrame,  "#4fc3f7"),
    ("🥔  Hot Potato", HotPotatoFrame,   "#ff6b35"),
    ("🏥  Rumah Sakit", HospitalQueueFrame, "#ce93d8"),
    ("🕸️  BFS Graf",   BFSFrame,          "#4fc3f7"),
    ("✈️  Bandara",    AirportSimFrame,    "#ffd740"),
]


def apply_dark_style():
    style = ttk.Style()
    style.theme_use("default")

    style.configure("TNotebook",
                    background=BG,
                    borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
                    background=PANEL,
                    foreground=SUBTEXT,
                    padding=[18, 10],
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", CARD), ("active", BORDER)],
              foreground=[("selected", TEXT), ("active", TEXT)])

    style.configure("TScrollbar",
                    background=PANEL,
                    troughcolor=CARD,
                    borderwidth=0,
                    arrowcolor=ACCENT)
    style.configure("Horizontal.TProgressbar",
                    background=ACCENT,
                    troughcolor=CARD,
                    borderwidth=0)
    style.configure("Vertical.TProgressbar",
                    background=ACCENT,
                    troughcolor=CARD,
                    borderwidth=0)


class QueueVisualApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Struktur Data — Queue Visualizer")
        self.geometry("1200x760")
        self.minsize(900, 640)
        self.configure(bg=BG)
        self.resizable(True, True)
        apply_dark_style()
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        logo_frame = tk.Frame(header, bg=PANEL)
        logo_frame.pack(side="left", padx=20)
        tk.Label(logo_frame, text="⚙️", font=("Segoe UI", 20),
                 bg=PANEL, fg=ACCENT).pack(side="left")
        tk.Label(logo_frame, text="  Data Structure — Queue Visualizer",
                 font=("Segoe UI", 16, "bold"), bg=PANEL, fg=TEXT).pack(side="left")
        tk.Label(logo_frame, text="  |  5 Kasus Queue",
                 font=("Segoe UI", 11), bg=PANEL, fg=SUBTEXT).pack(side="left")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        for label, FrameClass, color in TABS:
            frame = FrameClass(notebook)
            notebook.add(frame, text=f"  {label}  ")

        status = tk.Frame(self, bg=CARD, height=26)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        tk.Label(status, text="  Python · Tkinter · Queue Data Structure",
                 font=("Segoe UI", 8), bg=CARD, fg=SUBTEXT).pack(side="left", padx=10)
        tk.Label(status,
                 text="Kasus 1: FIFO Printer  |  Kasus 2: Hot Potato  |  "
                      "Kasus 3: Priority Queue  |  Kasus 4: BFS  |  Kasus 5: Simulasi Bandara  ",
                 font=("Segoe UI", 8), bg=CARD, fg=SUBTEXT).pack(side="right", padx=10)


if __name__ == "__main__":
    app = QueueVisualApp()
    app.mainloop()