import streamlit as st
import time
import numpy as np
import pandas as pd # Import pandas for CSV handling

# -----------------------------------------------------------------------------
# 1. CORE LOGIC: Solver & Validator
# -----------------------------------------------------------------------------

def is_valid(board, row, col, num):
    """
    Check if placing 'num' at board[row][col] is valid according to Sudoku rules.
    """
    # Check row
    for c in range(9):
        if board[row][c] == num:
            return False
            
    # Check column
    for r in range(9):
        if board[r][col] == num:
            return False
            
    # Check 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if board[r][c] == num:
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
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku_backtracking(board):
                            return True
                        board[row][col] = 0
                return False
    return True

@st.cache_data
def load_puzzles():
    """
    Loads puzzles from a CSV file.
    Expected format: id, difficulty, puzzle (string of 81 chars)
    """
    try:
        df = pd.read_csv('puzzles.csv')
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading puzzles: {e}")
        return []

def parse_puzzle_string(puzzle_str):
    """
    Parses a string of 81 characters into a 9x9 board.
    '.' or '0' are treated as empty cells.
    """
    board = []
    if len(puzzle_str) != 81:
         return [[0]*9 for _ in range(9)] # Return empty board on error
         
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
# 2. STATE MANAGEMENT
# -----------------------------------------------------------------------------

if 'board' not in st.session_state:
    st.session_state.board = [[0]*9 for _ in range(9)]

if 'solved_board' not in st.session_state:
    st.session_state.solved_board = None

if 'mode' not in st.session_state:
    st.session_state.mode = "Custom Sudoku"

# -----------------------------------------------------------------------------
# 3. CSS STYLING
# -----------------------------------------------------------------------------

def apply_sudoku_style():
    st.markdown("""
        <style>
        /* Make every input box a perfect square and center the text */
        input {
            width: 40px !important;
            height: 40px !important;
            text-align: center !important;
            font-size: 20px !important;
            font-weight: bold !important;
            border: 1px solid #999 !important;
            padding: 0px !important;
        }

        /* Remove the red/blue focus border from Streamlit */
        input:focus {
            border: 2px solid #4CAF50 !important;
            outline: none !important;
        }

        /* Create the thick borders for the 3x3 grids */
        [data-testid="column"]:nth-of-type(3n) {
            border-right: 3px solid black !important;
            padding-right: 5px;
        }
        
        /* This selector is tricky in Streamlit, so we usually 
           wrap the rows in containers to get the horizontal thick line */
        .stVerticalBlock > div > div:nth-of-type(3n) {
            border-bottom: 3px solid black !important;
        }
        
        /* ADJUSTMENT: Target stColumn for recent Streamlit versions if "column" fails */
        [data-testid="stColumn"]:nth-of-type(3n) {
             border-right: 3px solid black !important;
             padding-right: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_sudoku_style()


# -----------------------------------------------------------------------------
# 4. APP INTERFACE
# -----------------------------------------------------------------------------

st.title("🧩 Sudoku Solver")

# Sidebar
st.sidebar.header("Navigation")
mode = st.sidebar.radio("Select Mode", ["Custom Sudoku", "Preset Puzzles", "Image Upload (Future)"])

# Handle Mode Changes
if mode != st.session_state.mode:
    st.session_state.mode = mode
    # Reset board when switching modes (optional, but good UX to clear state)
    if mode == "Custom Sudoku":
        st.session_state.board = [[0]*9 for _ in range(9)]
        st.session_state.solved_board = None
    elif mode == "Preset Puzzles":
        # Load default puzzle 1
        puzzles = load_puzzles()
        if puzzles:
             first_puzzle = puzzles[0]
             st.session_state.board = parse_puzzle_string(first_puzzle['puzzle'])
             st.session_state.solved_board = None
             st.session_state.current_puzzle_id = first_puzzle['id']
        else:
            st.session_state.board = [[0]*9 for _ in range(9)]
            
# --- MODE 1: CUSTOM SUDOKU ---
if mode == "Custom Sudoku":
    st.sidebar.subheader("Controls")
    if st.sidebar.button("Clear Grid"):
        st.session_state.board = [[0]*9 for _ in range(9)]
        st.session_state.solved_board = None
        st.rerun()

    if st.sidebar.button("Solve Puzzle"):
        # Copy current board to avoid mutating UI state if we want to show animation or diff
        # Here we just solve in place
        board_copy = [row[:] for row in st.session_state.board]
        if solve_sudoku_backtracking(board_copy):
            st.session_state.board = board_copy
            st.success("Solved!")
            st.rerun()
        else:
            st.error("No solution found for this configuration.")

# --- MODE 2: PRESET PUZZLES ---
elif mode == "Preset Puzzles":
    st.sidebar.subheader("Select Puzzle")
    
    puzzles = load_puzzles()
    if not puzzles:
        st.error("No puzzles found in puzzles.csv")
    else:
        # Create a mapping of ID to puzzle data
        puzzle_map = {p['id']: p for p in puzzles}
        
        # Slider to select puzzle ID
        max_id = len(puzzles)
        puzzle_index = st.sidebar.slider("Puzzle ID", 1, max_id, 1) - 1 # 0-based index
        
        selected_puzzle = puzzles[puzzle_index]
        puzzle_id = selected_puzzle['id']
        
        # Display Difficulty
        st.sidebar.info(f"Difficulty: {selected_puzzle['difficulty']}")
    
        # Check if we need to load a new puzzle
        if 'current_puzzle_id' not in st.session_state or st.session_state.current_puzzle_id != puzzle_id:
            st.session_state.board = parse_puzzle_string(selected_puzzle['puzzle'])
            st.session_state.solved_board = None
            st.session_state.current_puzzle_id = puzzle_id
            st.rerun()
            
    if st.sidebar.button("Solve Preset"):
         board_copy = [row[:] for row in st.session_state.board]
         if solve_sudoku_backtracking(board_copy):
            st.session_state.board = board_copy
            st.success("Solved!")
            st.rerun()
         else:
            st.error("No solution found.")

# --- MODE 3: IMAGE UPLOAD ---
elif mode == "Image Upload (Future)":
    st.subheader("Image Upload")
    st.info("Coming Soon: OCR API Integration")
    uploaded_file = st.file_uploader("Upload an image of a Sudoku puzzle", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Puzzle", use_column_width=True)


# -----------------------------------------------------------------------------
# 5. GRID DISPLAY & INPUT HANDLING
# -----------------------------------------------------------------------------

def render_styled_grid(board):
    # Use a container to hold the entire grid
    with st.container():
        for i in range(9):
            # Add a divider line every 3 rows
            if i % 3 == 0 and i != 0:
                st.markdown("---") 
            
            cols = st.columns(9)
            for j in range(9):
                val = board[i][j]
                key = f"cell_{i}_{j}"
                
                # Use text_input but style it to look like a cell
                user_val = cols[j].text_input(
                    label="Values", # Hidden by CSS
                    value=str(val) if val != 0 else "",
                    key=key,
                    label_visibility="collapsed"
                )
                
                # Update the board state
                if user_val.isdigit() and 1 <= int(user_val) <= 9:
                    board[i][j] = int(user_val)
                else:
                    board[i][j] = 0
    return board

# Display the Grid
if mode in ["Custom Sudoku", "Preset Puzzles"]:
    st.write("### Grid")
    render_styled_grid(st.session_state.board)

