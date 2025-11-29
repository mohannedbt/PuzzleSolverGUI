# PuzzleSolverGUI

**Author:** Mohanned Bentaleb (`mohannedbt`)

## Overview

This repository contains multiple projects for puzzle-solving and testing algorithms with both **graphical interfaces** and **console-based versions**. The code has been reorganized into separate folders for clarity and usability.

### Folder Structure

- `graphical_interfaces/`  
  Contains GUI versions of the projects:  
  - `sudoku.py` – Sudoku solver with a PySide6 interface  
  - `kpiece.py` – K-Pieces placement solver with a GUI  
  - `tetris.py` – Testing versions of Tetris logic  

- `non_interfaces/`  
  Console-based versions of the projects (incomplete or for testing purposes)  

- `unifiedinterface.py`  
  Combines multiple GUIs into a single interface for easy access  

## Features

- Fully **dark-mode GUIs** for Sudoku and K-Pieces solvers  
- **Subgrid visualization** for Sudoku  
- **Piece placement rules** for K-Pieces (Queens, Rooks, Bishops, Knights)  
- Modular and organized project structure  
- Uses **Gurobi** for solving optimization problems via **PLNE** (linear/integer programming)

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/mohannedbt/PuzzleSolverGUI.git
   cd PuzzleSolverGUI
   ```

2. Install dependencies:
   ```bash
   pip install PySide6 gurobipy
   ```

3. Run a GUI version:
   ```bash
   python graphical_interfaces/sudoku.py
   python graphical_interfaces/kpiece.py
   ```

4. Run the unified interface:
   ```bash
   python unifiedinterface.py
   ```

5. For console-based testing, check the `non_interfaces/` folder:
   ```bash
   python non_interfaces/tetris_test.py
   ```

## Notes

- Sudoku solver allows for custom grid size and block size  
- K-Pieces solver checks feasibility based on the number of pieces and board size  
- Ensure Gurobi is installed and licensed to use PLNE solvers  

## License

This project is open source. Feel free to explore and modify the code.

