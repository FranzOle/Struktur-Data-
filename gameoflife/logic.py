from typing import List
import random

Grid = List[List[int]]  # 0 = dead, 1 = alive


def create_empty_grid(rows: int, cols: int) -> Grid:
    if rows <= 0 or cols <= 0:
        return []
    return [[0 for _ in range(cols)] for _ in range(rows)]


def create_grid(rows: int, cols: int, randomize: bool = False, prob_alive: float = 0.2) -> Grid:
    if prob_alive < 0:
        prob_alive = 0.0
    elif prob_alive > 1:
        prob_alive = 1.0

    if rows <= 0 or cols <= 0:
        return []

    if randomize:
        return [[1 if random.random() < prob_alive else 0 for _ in range(cols)] for _ in range(rows)]
    return create_empty_grid(rows, cols)


def randomize_grid(grid: Grid, prob_alive: float = 0.2) -> None:
    if not grid:
        return
    # clamp prob_alive
    if prob_alive < 0:
        prob_alive = 0.0
    elif prob_alive > 1:
        prob_alive = 1.0

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = 1 if random.random() < prob_alive else 0


def clear_grid(grid: Grid) -> None:
    if not grid:
        return
    rows = len(grid)
    cols = len(grid[0])
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = 0


def toggle_cell(grid: Grid, row: int, col: int) -> None:
    if not grid:
        return
    rows = len(grid)
    cols = len(grid[0])
    if 0 <= row < rows and 0 <= col < cols:
        grid[row][col] = 0 if grid[row][col] else 1


def set_cell(grid: Grid, row: int, col: int, value: int) -> None:
    if value not in (0, 1):
        raise ValueError("value harus 0 atau 1")
    if not grid:
        return
    rows = len(grid)
    cols = len(grid[0])
    if 0 <= row < rows and 0 <= col < cols:
        grid[row][col] = value


def count_neighbors(grid: Grid, row: int, col: int, wrap: bool = False) -> int:
    rows = len(grid)
    if rows == 0:
        return 0
    cols = len(grid[0])
    cnt = 0

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r = row + dr
            c = col + dc
            if wrap:
                r %= rows
                c %= cols
                cnt += grid[r][c]
            else:
                if 0 <= r < rows and 0 <= c < cols:
                    cnt += grid[r][c]
    return cnt


def next_generation(grid: Grid, wrap: bool = False) -> Grid:
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            neighbors = count_neighbors(grid, r, c, wrap=wrap)
            if grid[r][c] == 1:
                new_grid[r][c] = 1 if neighbors in (2, 3) else 0
            else:
                new_grid[r][c] = 1 if neighbors == 3 else 0
    return new_grid


def grid_to_string(grid: Grid) -> str:
    if not grid:
        return ""
    return "\n".join("".join("1" if cell else "0" for cell in row) for row in grid)


def string_to_grid(s: str) -> Grid:
    lines = [line.rstrip() for line in s.splitlines() if line.strip() != ""]
    if not lines:
        return []
    max_cols = max(len(line) for line in lines)
    grid: Grid = []
    for line in lines:
        row: List[int] = []
        for ch in line:
            row.append(1 if ch == "1" else 0)
        if len(row) < max_cols:
            row.extend([0] * (max_cols - len(row)))
        grid.append(row)
    return grid

if __name__ == "__main__":
    random.seed(0)  
    rows, cols = 5, 7
    g = create_grid(rows, cols, randomize=True, prob_alive=0.3)
    print("Initial:")
    print(grid_to_string(g))
    g2 = next_generation(g)
    print("\nNext:")
    print(grid_to_string(g2))
