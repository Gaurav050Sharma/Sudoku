def is_valid(board, row, col, num):
    for c in range(9):
        if c != col and board[row][c] == num:
            return False
            
    for r in range(9):
        if r != row and board[r][col] == num:
            return False
            
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if (r != row or c != col) and board[r][c] == num:
                return False
                
    return True
