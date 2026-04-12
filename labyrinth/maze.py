import random

def buat_maze(rows, cols):
    maze = []

    for i in range(rows):
        row = []
        for j in range(cols):
            if random.random() < 0.3:
                row.append("*")  # dinding
            else:
                row.append(".")  # jalan
        maze.append(row)

    # set start dan exit
    maze[0][0] = "S"
    maze[rows-1][cols-1] = "E"

    return maze