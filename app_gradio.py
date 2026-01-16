import gradio as gr
import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# 1. CORE LOGIC: Solver & Validator (Reused from Streamlit app)
# -----------------------------------------------------------------------------

# Helper for unicode bold digits
def to_bold_digit(n):
    # Mathematical Sans-Serif Bold Digits 1-9
    # 1 is U+1D7EC (Wait, 1D7EC is bold 0. 1D7ED is 1)
    # Actually, let's use a safe map.
    map_bold = {
        1: "𝟏", 2: "𝟐", 3: "𝟑", 4: "𝟒", 5: "𝟓",
        6: "𝟔", 7: "𝟕", 8: "𝟖", 9: "𝟗", 0: ""
    }
    return map_bold.get(n, str(n))

def normalize_digit(s):
    """ Converts unicode bold digits back to standard string digits 1-9 """
    s = str(s).strip()
    # Map bold to normal
    map_normal = {
        "𝟏": "1", "𝟐": "2", "𝟑": "3", "𝟒": "4", "𝟓": "5",
        "𝟔": "6", "𝟕": "7", "𝟖": "8", "𝟗": "9"
    }
    return map_normal.get(s, s)

def is_valid(board, row, col, num):
    """
    Check if placing 'num' at board[row][col] is valid according to Sudoku rules.
    This checks if 'num' exists in the row, column, or 3x3 box, SKIPPING the cell (row, col) itself
    if we are validating a board that already has the number placed.
    """
    # Check row
    for c in range(9):
        # validation logic: if we are checking a placement, we want to know if OTHER cells have this num
        if c != col and board[row][c] == num:
            return False
            
    # Check column
    for r in range(9):
        if r != row and board[r][col] == num:
            return False
            
    # Check 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if (r != row or c != col) and board[r][c] == num:
                return False
                
    return True

def solve_sudoku_backtracking(board):
    """
    Solves the sudoku board in-place using backtracking.
    Returns True if solved, False otherwise.
    """
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    # For solving, we are placing 'num' into an empty cell (0). 
                    # Our modified is_valid handles the check correctly because the current cell is 0,
                    # so it won't trigger equality with 'num' at (row, col).
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku_backtracking(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def load_puzzles():
    """
    Loads puzzles from a CSV file.
    Expected format: id, difficulty, puzzle (string of 81 chars)
    """
    try:
        df = pd.read_csv('puzzles.csv')
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading puzzles: {e}")
        return []

def parse_puzzle_string(puzzle_str):
    """
    Parses a string of 81 characters into a 9x9 board.
    '.' or '0' are treated as empty cells.
    """
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

# -----------------------------------------------------------------------------
# 2. GRADIO INTERFACE HELPERS
# -----------------------------------------------------------------------------

def format_grid(grid, original_grid=None):
    """
    Converts a 9x9 integer grid to a list of lists of strings.
    0 becomes "" (empty string) for better display.
    If original_grid is provided, filled numbers (where original was 0) are bolded.
    """
    new_grid = []
    for r in range(9):
        new_row = []
        for c in range(9):
            val = grid[r][c]
            if val == 0:
                new_row.append("")
            else:
                # Check if it was pre-filled
                if original_grid and original_grid[r][c] == 0:
                     # It's a new number -> Bold
                     new_row.append(to_bold_digit(val))
                else:
                     # It's original -> Normal
                     new_row.append(str(val))
        new_grid.append(new_row)
    return new_grid

def parse_grid(grid_data):
    """
    Parses Gradio Dataframe (or list) into a 9x9 integer grid.
    Empty strings "", NaNs, or invalid chars become 0.
    """
    # Handles dataframe or list of lists
    if isinstance(grid_data, pd.DataFrame):
        # Fill NaNs with "" and convert to list
        grid_data = grid_data.fillna("").values.tolist()
        
    cleaned = []
    if grid_data is None:
         return [[0]*9 for _ in range(9)]
         
    for row in grid_data:
        clean_row = []
        for val in row:
            try:
                s = normalize_digit(val) # Handle unicode bold inputs
                if s.isdigit() and 1 <= int(s) <= 9:
                    clean_row.append(int(s))
                else:
                    clean_row.append(0)
            except:
                clean_row.append(0)
        cleaned.append(clean_row)
    return cleaned

def validate_current_board(grid_df):
    """
    Real-time validation function.
    Checks:
    1. Input Validity (0-9 only).
    2. Sudoku Rules (Row, Col, Box).
    """
    # 1. Check Input Format (Digits 1-9 only)
    if isinstance(grid_df, pd.DataFrame):
        data = grid_df.fillna("").values.tolist()
    else:
        data = grid_df if grid_df is not None else []

    for r, row in enumerate(data):
        for c, val in enumerate(row):
            s = str(val).strip()
            if s == "": continue
            
            # Handle bold digits
            norm = normalize_digit(s)
            
            # Check if digit
            if not norm.isdigit():
                 return f"⚠️ Input Error: '{s}' at Row {r+1}, Col {c+1} is not a number."
            
            # Check range
            num = int(norm)
            if not (1 <= num <= 9) and num != 0:
                 return f"⚠️ Range Error: '{num}' at Row {r+1}, Col {c+1}. Use 1-9."

    # 2. Check Sudoku Rules
    clean_grid = parse_grid(grid_df)
    
    # Iterate over all cells
    for r in range(9):
        for c in range(9):
            val = clean_grid[r][c]
            if val != 0:
                # Check if this value is valid in its position
                # is_valid now correctly skips the current cell (r,c) when checking
                if not is_valid(clean_grid, r, c, val):
                    return f"❌ Violation: Number {val} at Row {r+1}, Col {c+1} is invalid!"
    return "✅ Valid State"

def solve_custom_grid(grid_df):
    """
    Takes the Gradio DataFrame, solves it, and returns the solved grid + status.
    """
    # 1. Parse input to standard integer grid
    clean_grid = parse_grid(grid_df)
    
    # Store original state (use deepcopy to be safe, though list comp creates new list structure)
    original_grid = [row[:] for row in clean_grid]

    # 1.5. Validate Initial State
    validation_msg = validate_current_board(grid_df)
    if "❌" in validation_msg:
        # Pass None as original_grid effectively keeps current formatting (all normal)
        return format_grid(clean_grid), "Cannot Solve: " + validation_msg

    # 2. Solve (in-place)
    if solve_sudoku_backtracking(clean_grid):
        # 3. Format back to strings for display, using original_grid to bold new numbers
        return format_grid(clean_grid, original_grid), "✅ Solved!"
    else:
        return format_grid(clean_grid), "❌ No solution found."

def clear_grid():
    return [[""]*9 for _ in range(9)], "Grid Cleared."

# Load puzzles once
ALL_PUZZLES = load_puzzles()
MAX_PUZZLE_ID = len(ALL_PUZZLES)

def get_random_puzzle():
    """
    Returns a random puzzle from the loaded list.
    """
    import random
    if MAX_PUZZLE_ID == 0:
        return [[""]*9 for _ in range(9)], "No puzzles loaded"

    idx = random.randint(0, MAX_PUZZLE_ID - 1)
    p = ALL_PUZZLES[idx]
    
    # Handle both old format (dictionary) and potential simple list if structure changed
    puzzle_str = str(p.get('puzzle', ''))
    
    # Safety check for scientific notation corruption (e.g. 5.3007E+80)
    if "E+" in puzzle_str and "." in puzzle_str:
         return [[""]*9 for _ in range(9)], f"Error: CSV Data Corrupted (Scientific Notation detected: {puzzle_str[:15]}...)"

    grid = parse_puzzle_string(puzzle_str)
    return format_grid(grid), f"Loaded Random Puzzle (ID: {p.get('id', idx+1)})"

def solve_preset_grid(grid_df):
    return solve_custom_grid(grid_df)

# -----------------------------------------------------------------------------
# 3. BUILD UI
# -----------------------------------------------------------------------------

# Theme settings
theme = gr.themes.Soft()

# Custom CSS for Sudoku Grid
sudoku_css = """
footer {visibility: hidden}

/* Center the container */
.sudoku-grid {
    display: flex;
    justify-content: center;
}

/* Table Styling - Responsive */
.sudoku-grid table {
    border-collapse: collapse !important;
    border: 3px solid var(--body-text-color) !important;
    /* Use max-width with viewport units for responsiveness */
    width: 100% !important;
    max-width: 600px !important; 
    margin: 0 auto !important; /* Center horizontally */
    table-layout: fixed !important;
}

/* Cell Styling - Responsive */
.sudoku-grid td, .sudoku-grid th {
    /* Auto width allows table-layout: fixed to distribute evenly */
    width: auto !important; 
    height: auto !important;
    aspect-ratio: 1 / 1 !important;
    padding: 0 !important;
    border: 1px solid var(--border-color-primary);
    text-align: center !important;
    vertical-align: middle !important;
    overflow: hidden !important;
    position: relative; /* For absolute pos input */
}

/* Inner contents */
.sudoku-grid td > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Input Styling (Numbers) - Responsive Text */
.sudoku-grid input {
    /* Use container query units or viewport units for font size if supported, 
       but standard calc/clamp is safer here. */
    font-size: clamp(12px, 4vw, 24px) !important; 
    text-align: center !important;
    font-family: monospace;
    color: var(--body-text-color) !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
}

/* -----------------------------------------------------------
   THICK BORDERS FOR 3x3 SUBGRIDS 
   -----------------------------------------------------------
   NOTE: Because we hide the first-child (index), we DO NOT change the nth-child count.
   The hidden element is still in the DOM tree index.
   
   Structure: [Index, Col1, Col2, Col3, Col4, Col5, Col6, Col7, Col8, Col9]
                  1     2     3     4     5     6     7     8     9     10
*/

/* Right border of Col 3 */
.sudoku-grid td:nth-child(3),
.sudoku-grid th:nth-child(3) {
    border-right: 3px solid var(--body-text-color) !important;
}

/* Right border of Col 6 */
.sudoku-grid td:nth-child(6),
.sudoku-grid th:nth-child(6) {
    border-right: 3px solid var(--body-text-color) !important;
}

/* Bottom border of Row 3 */
.sudoku-grid tbody tr:nth-child(3) td {
    border-bottom: 3px solid var(--body-text-color) !important;
}

/* Bottom border of Row 6 */
.sudoku-grid tbody tr:nth-child(6) td {
    border-bottom: 3px solid var(--body-text-color) !important;
}

/* Hide Header completely */
.sudoku-grid table thead {
    display: none !important;
}

/* Hide extra Gradio elements (sort icons, etc) */
.sudoku-grid .sort-button { display: none !important; }
.sudoku-grid svg { display: none !important; }
"""

with gr.Blocks(title="Sudoku Solver", theme=theme, css=sudoku_css) as demo:
    gr.Markdown("# 🧩 Sudoku Solver")
    
    with gr.Tabs():
        
        # --- TAB 1: CUSTOM SUDOKU ---
        with gr.TabItem("Custom Sudoku"):
            gr.Markdown("Enter numbers manually into the grid. 0 represents an empty cell.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # headers=None hides the header row in some versions, or we can use 1-9
                    custom_grid = gr.Dataframe(
                        headers=[str(i+1) for i in range(9)],
                        row_count=(9, "fixed"),
                        col_count=(9, "fixed"),
                        label="Sudoku Grid",
                        type="pandas",
                        interactive=True,
                        value=[[""]*9 for _ in range(9)],
                        elem_classes=["sudoku-grid"] # Apply custom CSS class
                    )
                with gr.Column(scale=1):
                    custom_solve_btn = gr.Button("Solve Puzzle", variant="primary")
                    custom_clear_btn = gr.Button("Clear Grid", variant="secondary")
                    custom_status = gr.Textbox(label="Status", value="Ready", interactive=False)
            
            custom_solve_btn.click(
                fn=solve_custom_grid,
                inputs=custom_grid,
                outputs=[custom_grid, custom_status]
            )
            
            custom_clear_btn.click(
                fn=clear_grid,
                inputs=None,
                outputs=[custom_grid, custom_status]
            )
            
            # Real-time validation
            custom_grid.change(
                fn=validate_current_board,
                inputs=custom_grid,
                outputs=custom_status
            )

        # --- TAB 2: PRESET PUZZLES ---
        with gr.TabItem("Preset Puzzles"):
            gr.Markdown("Get a random puzzle from the library.")
            
            with gr.Row():
                with gr.Column():
                    preset_new_btn = gr.Button("Get Random Puzzle", variant="secondary")
                    preset_solve_btn = gr.Button("Solve", variant="primary")
                    preset_status = gr.Textbox(label="Status", value="", interactive=False)

                with gr.Column(scale=2):
                    preset_grid = gr.Dataframe(
                        headers=[str(i+1) for i in range(9)],
                        row_count=(9, "fixed"),
                        col_count=(9, "fixed"),
                        label="Puzzle Board",
                        interactive=True, # Allow users to try solving manually too
                        elem_classes=["sudoku-grid"] # Apply custom CSS class
                    )
            
            # Init first puzzle
            demo.load(fn=get_random_puzzle, inputs=None, outputs=[preset_grid, preset_status])
            
            # Events
            preset_new_btn.click(
                fn=get_random_puzzle,
                inputs=None,
                outputs=[preset_grid, preset_status]
            )
            
            preset_solve_btn.click(
                fn=solve_preset_grid,
                inputs=preset_grid,
                outputs=[preset_grid, preset_status]
            )
            
            # Real-time validation
            preset_grid.change(
                fn=validate_current_board,
                inputs=preset_grid,
                outputs=preset_status
            )

        # --- TAB 3: IMAGE UPLOAD ---
        with gr.TabItem("Image Upload"):
             gr.Markdown("# Coming Soon")

if __name__ == "__main__":
    demo.launch()
