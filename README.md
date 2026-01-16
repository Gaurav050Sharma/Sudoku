---
title: Sudoku Solver
emoji: 🧩
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.1
app_file: app_gradio.py
pinned: false
license: mit
---

# Sudoku Solver


A complete, production-ready Sudoku application built with Python and Streamlit.

## Features

- **Custom Sudoku Mode**: Input your own puzzle and solve it.
- **Preset Puzzles**: Choose from sample puzzles.
- **Backtracking Solver**: Efficient algorithm to solve any valid Sudoku.
- **Validator**: Real-time validation of inputs (via solver logic).
- **Responsive Grid**: Custom CSS for a clean, square grid layout.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

Run the Gradio application:
```bash
python app_gradio.py
```

## Modes

1. **Custom Sudoku**: Enter numbers manually. Click "Solve" to auto-fill.
2. **Preset Puzzles**: Select a puzzle ID (1-5) to load a challenge.
3. **Image Upload**: (Coming Soon) Upload an image to extract the puzzle.

## Project Structure

- `app.py`: Main application code containing UI, Logic, and CSS.
- `requirements.txt`: Python dependencies.
