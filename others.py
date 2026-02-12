import pandas as pd

def to_bold_digit(n):
    map_bold = {
        1: "𝟏", 2: "𝟐", 3: "𝟑", 4: "𝟒", 5: "𝟓",
        6: "𝟔", 7: "𝟕", 8: "𝟖", 9: "𝟗", 0: ""
    }
    return map_bold.get(n, str(n))

def normalize_digit(s):
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
    except (ValueError, TypeError):
        pass

    s = str(s).strip()
    map_normal = {
        "𝟏": "1", "𝟐": "2", "𝟑": "3", "𝟒": "4", "𝟓": "5",
        "𝟔": "6", "𝟕": "7", "𝟖": "8", "𝟗": "9"
    }
    return map_normal.get(s, s)

def load_puzzles():
    try:
        df = pd.read_csv('puzzles.csv')
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading puzzles: {e}")
        return []

def parse_puzzle_string(puzzle_str):
    board = []
    if len(puzzle_str) != 81:
         return [[0]*9 for _ in range(9)]
         
    for i in range(9):
        row = []
        for j in range(9):
            char = puzzle_str[i*9 + j]
            if char in '123456789':
                row.append(int(char))
            else:
                row.append(0)
        board.append(row)
    return board

def format_grid(grid, original_grid=None):
    new_grid = []
    for r in range(9):
        new_row = []
        for c in range(9):
            val = grid[r][c]
            if val == 0:
                new_row.append("")
            else:
                if original_grid and original_grid[r][c] == 0:
                     new_row.append(to_bold_digit(val))
                else:
                     new_row.append(str(val))
        new_grid.append(new_row)
    return new_grid

def parse_grid(grid_data):
    if isinstance(grid_data, pd.DataFrame):
        grid_data = grid_data.fillna("").values.tolist()
        
    cleaned = []
    if grid_data is None:
         return [[0]*9 for _ in range(9)]
         
    for row in grid_data:
        clean_row = []
        for val in row:
            try:
                s = normalize_digit(val)
                if s.isdigit() and 1 <= int(s) <= 9:
                    clean_row.append(int(s))
                else:
                    clean_row.append(0)
            except:
                clean_row.append(0)
        cleaned.append(clean_row)
    return cleaned

ALL_PUZZLES = load_puzzles()
MAX_PUZZLE_ID = len(ALL_PUZZLES)

def get_random_puzzle():
    import random
    if MAX_PUZZLE_ID == 0:
        return [[""]*9 for _ in range(9)], "No puzzles loaded"

    idx = random.randint(0, MAX_PUZZLE_ID - 1)
    p = ALL_PUZZLES[idx]
    
    puzzle_str = str(p.get('puzzle', ''))
    
    grid = parse_puzzle_string(puzzle_str)
    return format_grid(grid), f"Loaded Random Puzzle (ID: {p.get('id', idx+1)})"
