import tkinter as tk
from tkinter import ttk
from logic import (
    create_grid,
    create_empty_grid,
    next_generation,
    randomize_grid,
    clear_grid,
    toggle_cell,
)

DEFAULT_ROWS = 30
DEFAULT_COLS = 40
DEFAULT_CELL_SIZE = 16
DEFAULT_DELAY = 150

ROWS = DEFAULT_ROWS
COLS = DEFAULT_COLS
CELL_SIZE = DEFAULT_CELL_SIZE
DELAY = DEFAULT_DELAY
WRAP = False

grid = create_grid(ROWS, COLS, randomize=False)
running = False
_after_id = None

def canvas_size():
    return COLS * CELL_SIZE, ROWS * CELL_SIZE

def draw_grid():
    canvas.delete("all")
    w, h = canvas_size()
    canvas.config(width=w, height=h)
    for r in range(ROWS):
        y1 = r * CELL_SIZE
        y2 = y1 + CELL_SIZE
        for c in range(COLS):
            x1 = c * CELL_SIZE
            x2 = x1 + CELL_SIZE
            if grid[r][c]:
                canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")
            else:
                canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="lightgray")

def step_generation():
    global grid
    grid = next_generation(grid, wrap=wrap_var.get())
    draw_grid()

def _run_loop():
    global _after_id, running
    if not running:
        return
    print("Stepping generation...")
    step_generation()
    delay_ms = int(speed_scale.get())
    _after_id = root.after(delay_ms, _run_loop)


def start():
    global running, _after_id
    if not running:
        running = True
        start_btn.config(text="Pause")
        _run_loop()
    else:
        running = False
        start_btn.config(text="Start")
        if _after_id is not None:
            try:
                root.after_cancel(_after_id)
            except Exception:
                pass
            _after_id = None


def step_button_clicked():
    if running:
        return
    step_generation()

def randomize_clicked():
    try:
        p = float(prob_entry.get())
        if p < 0 or p > 1:
            raise ValueError
    except Exception:
        p = 0.2
        prob_entry.delete(0, tk.END)
        prob_entry.insert(0, "0.2")
    randomize_grid(grid, prob_alive=p)
    draw_grid()

def clear_clicked():
    clear_grid(grid)
    draw_grid()

def on_canvas_click(event):
    c = event.x // CELL_SIZE
    r = event.y // CELL_SIZE
    if 0 <= r < ROWS and 0 <= c < COLS:
        toggle_cell(grid, r, c)
        draw_grid()

def apply_resize():
    global ROWS, COLS, grid
    try:
        new_rows = int(rows_entry.get())
        new_cols = int(cols_entry.get())
        if new_rows <= 0 or new_cols <= 0:
            raise ValueError
    except Exception:
        rows_entry.delete(0, tk.END)
        rows_entry.insert(0, str(ROWS))
        cols_entry.delete(0, tk.END)
        cols_entry.insert(0, str(COLS))
        return

    ROWS = new_rows
    COLS = new_cols

    if resize_random_var.get():
        grid = create_grid(ROWS, COLS, randomize=True, prob_alive=float(prob_entry.get() or 0.2))
    else:
        grid = create_empty_grid(ROWS, COLS)
    draw_grid()

def export_text():
    s = "\n".join("".join("1" if cell else "0" for cell in row) for row in grid)
    top = tk.Toplevel(root)
    top.title("Grid text (copy/save)")
    txt = tk.Text(top, width=60, height=20)
    txt.insert("1.0", s)
    txt.pack(fill="both", expand=True)
    ttk.Button(top, text="Close", command=top.destroy).pack(pady=4)

root = tk.Tk()
root.title("Game of Life - Lionel Jevon")

top_frame = ttk.Frame(root)
top_frame.pack(padx=8, pady=8, fill="both", expand=True)

canvas = tk.Canvas(top_frame, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg="white")
canvas.grid(row=0, column=0, sticky="nw")
canvas.bind("<Button-1>", on_canvas_click)

ctrl = ttk.Frame(top_frame)
ctrl.grid(row=0, column=1, padx=12, sticky="n")

start_btn = ttk.Button(ctrl, text="Start", width=12, command=start)
start_btn.grid(row=0, column=0, columnspan=2, pady=(0, 6))

step_btn = ttk.Button(ctrl, text="Step", width=12, command=step_button_clicked)
step_btn.grid(row=1, column=0, columnspan=2, pady=(0, 8))

ttk.Label(ctrl, text="Randomize prob (0-1):").grid(row=2, column=0, columnspan=2, sticky="w")
prob_entry = ttk.Entry(ctrl, width=10)
prob_entry.insert(0, "0.2")
prob_entry.grid(row=3, column=0, columnspan=2, pady=(0, 6))

rand_btn = ttk.Button(ctrl, text="Randomize", command=randomize_clicked)
rand_btn.grid(row=4, column=0, columnspan=2, pady=(0, 6))

clear_btn = ttk.Button(ctrl, text="Clear", command=clear_clicked)
clear_btn.grid(row=5, column=0, columnspan=2, pady=(0, 8))

ttk.Label(ctrl, text="Delay (ms)").grid(row=6, column=0, columnspan=2, sticky="w")
speed_scale = ttk.Scale(ctrl, from_=20, to=1000, orient="horizontal")
speed_scale.set(DELAY)
speed_scale.grid(row=7, column=0, columnspan=2, pady=(0, 8), sticky="ew")

wrap_var = tk.BooleanVar(value=WRAP)
wrap_check = ttk.Checkbutton(ctrl, text="Wrap (toroidal)", variable=wrap_var)
wrap_check.grid(row=8, column=0, columnspan=2, pady=(0, 8))

ttk.Label(ctrl, text="Rows:").grid(row=9, column=0, sticky="e")
rows_entry = ttk.Entry(ctrl, width=6)
rows_entry.insert(0, str(ROWS))
rows_entry.grid(row=9, column=1, sticky="w")

ttk.Label(ctrl, text="Cols:").grid(row=10, column=0, sticky="e")
cols_entry = ttk.Entry(ctrl, width=6)
cols_entry.insert(0, str(COLS))
cols_entry.grid(row=10, column=1, sticky="w")

resize_random_var = tk.BooleanVar(value=False)
resize_rand_check = ttk.Checkbutton(ctrl, text="Randomize on resize", variable=resize_random_var)
resize_rand_check.grid(row=11, column=0, columnspan=2, pady=(2, 6))

apply_btn = ttk.Button(ctrl, text="Apply Resize", command=apply_resize)
apply_btn.grid(row=12, column=0, columnspan=2, pady=(0, 8))

export_btn = ttk.Button(ctrl, text="Export Text", command=export_text)
export_btn.grid(row=13, column=0, columnspan=2, pady=(0, 6))

instr = (
    ""
)
ttk.Label(ctrl, text=instr, justify="left").grid(row=14, column=0, columnspan=2, pady=(8, 0))

for i in range(2):
    ctrl.columnconfigure(i, weight=1)

draw_grid()

root.mainloop()
