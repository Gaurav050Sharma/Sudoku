import gradio as gr
import pandas as pd
from validate import is_valid
from backtracking import solve_sudoku_backtracking
from others import normalize_digit, format_grid, parse_grid, get_random_puzzle

# -----------------------------------------------------------------------------
# GRADIO
# -----------------------------------------------------------------------------

def validate_current_board(grid_df):
    if isinstance(grid_df, pd.DataFrame):
        data = grid_df.fillna("").values.tolist()
    else:
        data = grid_df if grid_df is not None else []

    for r, row in enumerate(data):
        for c, val in enumerate(row):
            s = str(val).strip()
            if s == "": continue
            
            norm = normalize_digit(s)
            
            if not norm.isdigit():
                 return f"⚠️ Input Error: '{s}' at Row {r+1}, Col {c+1} is not a number."
            
            num = int(norm)
            if not (1 <= num <= 9) and num != 0:
                 return f"⚠️ Range Error: '{num}' at Row {r+1}, Col {c+1}. Use 1-9."

    clean_grid = parse_grid(grid_df)
    
    for r in range(9):
        for c in range(9):
            val = clean_grid[r][c]
            if val != 0:
                if not is_valid(clean_grid, r, c, val):
                    return f"❌ Violation: Number {val} at Row {r+1}, Col {c+1} is invalid!"
    return "✅ Valid State"

def solve_custom_grid(grid_df):
    clean_grid = parse_grid(grid_df)
    
    original_grid = [row[:] for row in clean_grid]

    validation_msg = validate_current_board(grid_df)
    if "❌" in validation_msg:
        return format_grid(clean_grid), "Cannot Solve: " + validation_msg

    if solve_sudoku_backtracking(clean_grid):
        return format_grid(clean_grid, original_grid), "✅ Solved!"
    else:
        return format_grid(clean_grid), "❌ No solution found."

def clear_grid():
    return [[""]*9 for _ in range(9)], "Grid Cleared."

theme = gr.themes.Soft()
sudoku_css = """
footer {visibility: hidden}

.sudoku-grid {
    display: flex;
    justify-content: center;
}

.sudoku-grid table {
    border-collapse: collapse !important;
    border: 3px solid var(--body-text-color) !important;
    width: 100% !important;
    max-width: 600px !important; 
    margin: 0 auto !important;
    table-layout: fixed !important;
}

.sudoku-grid td, .sudoku-grid th {
    width: auto !important; 
    height: auto !important;
    aspect-ratio: 1 / 1 !important;
    padding: 0 !important;
    border: 1px solid var(--border-color-primary);
    text-align: center !important;
    vertical-align: middle !important;
    overflow: hidden !important;
    position: relative;
}

.sudoku-grid td > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

.sudoku-grid input {
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

.sudoku-grid td:nth-child(3),
.sudoku-grid th:nth-child(3) {
    border-right: 3px solid var(--body-text-color) !important;
}

.sudoku-grid td:nth-child(6),
.sudoku-grid th:nth-child(6) {
    border-right: 3px solid var(--body-text-color) !important;
}

.sudoku-grid tbody tr:nth-child(3) td {
    border-bottom: 3px solid var(--body-text-color) !important;
}

.sudoku-grid tbody tr:nth-child(6) td {
    border-bottom: 3px solid var(--body-text-color) !important;
}

.sudoku-grid table thead {
    display: none !important;
}

.sudoku-grid .sort-button,
.sudoku-grid svg { display: none !important; }
"""

with gr.Blocks(title="Sudoku Solver", theme=theme, css=sudoku_css) as demo:
    gr.Markdown("# 🧩 Sudoku Solver")
    
    with gr.Tabs():
        
        with gr.TabItem("Custom Sudoku"):
            gr.Markdown("Enter numbers manually into the grid. 0 represents an empty cell.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    custom_grid = gr.Dataframe(
                        headers=[str(i+1) for i in range(9)],
                        row_count=(9, "fixed"),
                        col_count=(9, "fixed"),
                        label="Sudoku Grid",
                        type="pandas",
                        interactive=True,
                        value=[[""]*9 for _ in range(9)],
                        elem_classes=["sudoku-grid"]
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
            
            custom_grid.change(
                fn=validate_current_board,
                inputs=custom_grid,
                outputs=custom_status
            )

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
                        interactive=True, 
                        elem_classes=["sudoku-grid"]
                    )
            
            demo.load(fn=get_random_puzzle, inputs=None, outputs=[preset_grid, preset_status])
            
            preset_new_btn.click(
                fn=get_random_puzzle,
                inputs=None,
                outputs=[preset_grid, preset_status]
            )
            
            preset_solve_btn.click(
                fn=solve_custom_grid,
                inputs=preset_grid,
                outputs=[preset_grid, preset_status]
            )
            
            preset_grid.change(
                fn=validate_current_board,
                inputs=preset_grid,
                outputs=preset_status
            )


if __name__ == "__main__":
    demo.launch()
