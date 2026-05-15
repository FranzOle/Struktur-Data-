import tkinter as tk
from theme import *
from panels import NQueensPanel, KnightsTourPanel, KnapsackPanel


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Struktur Data — Rekursi & Backtracking")
        self.geometry("1000x680")
        self.minsize(860, 580)
        self.configure(bg=BG)
        self._active = 0
        self._panels = []
        self._nav_btns = []
        self._build()

    def _build(self):
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)

        sidebar = tk.Frame(root, bg=CARD, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="⬡", bg=CARD, fg=ACCENT, font=("Segoe UI", 28)).pack(pady=(24, 2))
        tk.Label(sidebar, text="Struktur Data", bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold")).pack()
        tk.Label(sidebar, text="Rekursi & Backtracking", bg=CARD, fg=TEXT2, font=("Segoe UI", 8)).pack(pady=(0, 28))

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 20))

        nav_items = [
            ("♛  N-Queens", ACCENT),
            ("♞  Knight's Tour", ACCENT2),
            ("⚖  Knapsack", ACCENT3),
        ]

        for i, (label, color) in enumerate(nav_items):
            btn = tk.Button(sidebar, text=label, bg=CARD, fg=TEXT2,
                            activebackground=CARD2, activeforeground=TEXT,
                            font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                            anchor="w", padx=20, pady=10, cursor="hand2",
                            command=lambda idx=i: self._switch(idx))
            btn.pack(fill="x", padx=8, pady=2)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(fg=c) if b != self._nav_btns[self._active] else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=TEXT2) if b != self._nav_btns[self._active] else None)
            self._nav_btns.append(btn)

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=20)

        tk.Label(sidebar, text="Algoritma", bg=CARD, fg=TEXT2, font=("Segoe UI", 8)).pack(anchor="w", padx=20)
        for txt in ["Rekursi", "Backtracking", "Warnsdorff Heuristic"]:
            dot = "◆ " if txt != "Warnsdorff Heuristic" else "◇ "
            tk.Label(sidebar, text=dot + txt, bg=CARD, fg=TEXT2, font=("Segoe UI", 8)).pack(anchor="w", padx=24, pady=1)

        self.content = tk.Frame(root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        panel_classes = [NQueensPanel, KnightsTourPanel, KnapsackPanel]
        for cls in panel_classes:
            p = cls(self.content)
            self._panels.append(p)

        self._switch(0)

    def _switch(self, idx):
        colors = [ACCENT, ACCENT2, ACCENT3]
        for i, (btn, panel) in enumerate(zip(self._nav_btns, self._panels)):
            if i == idx:
                btn.config(bg=CARD2, fg=colors[i])
                panel.place(in_=self.content, x=0, y=0, relwidth=1, relheight=1)
                panel.lift()
            else:
                btn.config(bg=CARD, fg=TEXT2)
                panel.place_forget()
        self._active = idx


if __name__ == "__main__":
    app = App()
    app.mainloop()