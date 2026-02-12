from validate import is_valid

def solve_sudoku_backtracking(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku_backtracking(board):
                            return True
                        board[row][col] = 0
                return False
    return True
