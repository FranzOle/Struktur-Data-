def solve_nqueens(n):
    board = [[0] * n for _ in range(n)]
    solutions = []

    def is_safe(board, row, col):
        for i in range(col):
            if board[row][i] == 1:
                return False
        i, j = row, col
        while i >= 0 and j >= 0:
            if board[i][j] == 1:
                return False
            i -= 1
            j -= 1
        i, j = row, col
        while i < n and j >= 0:
            if board[i][j] == 1:
                return False
            i += 1
            j -= 1
        return True

    def solve(board, col):
        if col >= n:
            sol = []
            for r in range(n):
                for c in range(n):
                    if board[r][c] == 1:
                        sol.append((r, c))
            solutions.append(sol)
            return True
        res = False
        for i in range(n):
            if is_safe(board, i, col):
                board[i][col] = 1
                res = solve(board, col + 1) or res
                board[i][col] = 0
        return res

    solve(board, 0)
    return solutions


def solve_knights_tour(n, start_row, start_col):
    board = [[-1] * n for _ in range(n)]
    moves_x = [2, 1, -1, -2, -2, -1, 1, 2]
    moves_y = [1, 2, 2, 1, -1, -2, -2, -1]

    def is_valid(x, y):
        return 0 <= x < n and 0 <= y < n and board[x][y] == -1

    def warnsdorff_count(x, y):
        count = 0
        for i in range(8):
            nx, ny = x + moves_x[i], y + moves_y[i]
            if is_valid(nx, ny):
                count += 1
        return count

    def solve(x, y, step):
        if step == n * n:
            return True
        neighbors = []
        for i in range(8):
            nx, ny = x + moves_x[i], y + moves_y[i]
            if is_valid(nx, ny):
                neighbors.append((warnsdorff_count(nx, ny), nx, ny))
        neighbors.sort()
        for _, nx, ny in neighbors:
            board[nx][ny] = step
            if solve(nx, ny, step + 1):
                return True
            board[nx][ny] = -1
        return False

    board[start_row][start_col] = 0
    if solve(start_row, start_col, 1):
        return board
    return None


def solve_knapsack(weights, target):
    solutions = []
    current = []

    def backtrack(index, remaining):
        if remaining == 0:
            solutions.append(list(current))
            return
        if index >= len(weights) or remaining < 0:
            return
        current.append(weights[index])
        backtrack(index + 1, remaining - weights[index])
        current.pop()
        backtrack(index + 1, remaining)

    backtrack(0, target)
    return solutions