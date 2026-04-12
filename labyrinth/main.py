import time
from maze import buat_maze

def print_maze(maze):
    for row in maze:
        print(" ".join(row))
    print()

def valid_move(maze, r, c):
    rows = len(maze)
    cols = len(maze[0])

    return (0 <= r < rows and
            0 <= c < cols and
            maze[r][c] in [".", "E"])

def solve_maze(maze):
    stack = []
    stack.append((0, 0))  # start

    while stack:
        r, c = stack[-1]  # peek

        # animasi
        print("\033[H\033[J")  # clear layar
        print_maze(maze)
        time.sleep(0.2)

        if maze[r][c] == "E":
            print("🎉 Ketemu jalan keluar!")
            return True

        moved = False

        # arah: atas, bawah, kiri, kanan
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc

            if valid_move(maze, nr, nc):
                if maze[nr][nc] != "E":
                    maze[nr][nc] = "x"  # jalan benar
                stack.append((nr, nc))  # push
                moved = True
                break

        if not moved:
            maze[r][c] = "o"  # jalan buntu
            stack.pop()       # pop (mundur)

    print("❌ Tidak ada jalan")
    return False


# RUN
maze = buat_maze(10, 10)
solve_maze(maze)