from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from gurobipy import Model, GRB
from random import randint as rand

# ---------------------------- Styles ----------------------------
BUTTON_STYLE = """
QPushButton {
    background-color: #1E90FF;
    color: white;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    padding: 10px;
}
QPushButton:hover { background-color: #3AA0FF; }
QPushButton:pressed { background-color: #105CB3; }
"""

INPUT_STYLE = """
QLineEdit {
    padding: 8px;
    border: 2px solid #555555;
    border-radius: 6px;
    font-size: 16px;
    background-color: #2C2C2C;
    color: #FFFFFF;
}
QLineEdit:focus {
    border: 2px solid #1E90FF;
    background-color: #3A3A3A;
}
"""

LABEL_STYLE = """
font-size: 24px;
font-weight: bold;
color: #FFFFFF;
"""

# ---------------------------- GUI ----------------------------
class SudokuSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku Solver")
        self.setGeometry(50, 50, 900, 700)
        self.setStyleSheet("background-color: #121212;")

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Pages
        self.menu_page = self.create_menu_page()
        self.input_page = self.create_input_page()
        self.board_page = self.create_board_page()
        self.manual_page = self.create_manual_page()

        self.stacked.addWidget(self.menu_page)
        self.stacked.addWidget(self.input_page)
        self.stacked.addWidget(self.board_page)
        self.stacked.addWidget(self.manual_page)

    # ---------------- Menu Page ----------------
    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("SUDOKU SOLVER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:36px;font-weight:bold;color:#FFFFFF;")

        start_btn = QPushButton("START SOLVER")
        start_btn.setStyleSheet(BUTTON_STYLE)
        start_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))

        manual_btn = QPushButton("MANUAL PAGE")
        manual_btn.setStyleSheet(BUTTON_STYLE)
        manual_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.manual_page))

        layout.addWidget(title)
        layout.addWidget(start_btn)
        layout.addWidget(manual_btn)
        return page

    # ---------------- Input Page ----------------
    def create_input_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        page.setStyleSheet("background-color: #1E1E1E;")

        # Sudoku size
        label_n = QLabel("Sudoku size (n):")
        label_n.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_n)

        self.n_input = QLineEdit()
        self.n_input.setPlaceholderText("e.g., 9 for 9x9 Sudoku")
        self.n_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.n_input)

        # Cells to remove
        label_remove = QLabel("Cells to remove:")
        label_remove.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_remove)

        self.remove_input = QLineEdit()
        self.remove_input.setPlaceholderText("e.g., 40")
        self.remove_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.remove_input)

        # Custom block size checkbox
        self.block_checkbox = QCheckBox("Use custom block size")
        self.block_checkbox.setStyleSheet("color:white; font-size:18px;")
        layout.addWidget(self.block_checkbox)

        # Block size input, hidden initially
        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("Block size (e.g., 3)")
        self.block_input.setStyleSheet(INPUT_STYLE)
        self.block_input.setVisible(False)
        layout.addWidget(self.block_input)

        # Connect checkbox to toggle function
        self.block_checkbox.stateChanged.connect(
            lambda state: self.block_input.setVisible(state != Qt.CheckState.Checked)
        )

        # Solve button
        self.solve_btn = QPushButton("🚀 SOLVE")
        self.solve_btn.setMinimumHeight(50)
        self.solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: #1E1E1E;
                font-weight: bold;
                font-size: 20px;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #00CED1; }
            QPushButton:pressed { background-color: #1ABC9C; }
        """)
        self.solve_btn.clicked.connect(self.solve)
        layout.addWidget(self.solve_btn)

        # Back button
        back_btn = QPushButton("⬅ BACK")
        back_btn.setMinimumHeight(50)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #FF5252; }
        """)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.menu_page))
        layout.addWidget(back_btn)

        return page


    # ---------------- Board Page ----------------
    def create_board_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.board_widget = QWidget()
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(1)
        self.board_widget.setLayout(self.board_layout)
        layout.addWidget(self.board_widget)

        self.back_btn_board = QPushButton("⬅ BACK")
        self.back_btn_board.setStyleSheet(BUTTON_STYLE)
        self.back_btn_board.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        layout.addWidget(self.back_btn_board)

        return page

    # ---------------- Manual Page ----------------
    def create_manual_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("MANUAL PAGE (empty for now)")
        label.setStyleSheet("color:white; font-size:24px; font-weight:bold;")
        layout.addWidget(label)

        back_btn = QPushButton("⬅ BACK")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.menu_page))
        layout.addWidget(back_btn)

        return page

    # ---------------- Clear Board ----------------
    def clear_board(self):
        for i in reversed(range(self.board_layout.count())):
            w = self.board_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

    # ---------------- Solve ----------------
    def solve(self):
        self.clear_board()
        try:
            n = int(self.n_input.text())
            eliminate = int(self.remove_input.text())
            block_size = int(self.block_input.text()) if self.block_checkbox.isChecked() else -1
        except:
            QMessageBox.warning(self, "Input Error", "Enter valid numbers.")
            return

        if n < 1 or (block_size < 1 and self.block_checkbox.isChecked()==True) or block_size > n:
            QMessageBox.warning(self, "Input Error", "Invalid sizes.")
            return
        if eliminate >= n*n:
            QMessageBox.warning(self, "Input Error", f"Cells to remove must be < {n*n}.")
            return

        # ---------------- Gurobi Model ----------------
        model = Model("Sudoku")
        model.setParam("OutputFlag",0)
        x = {}
        for r in range(1,n+1):
            for c in range(1,n+1):
                for d in range(1,n+1):
                    x[(r,c,d)] = model.addVar(vtype=GRB.BINARY)

        # Constraints
        for r in range(1,n+1):
            for c in range(1,n+1):
                model.addConstr(sum(x[(r,c,d)] for d in range(1,n+1))==1)
        for r in range(1,n+1):
            for d in range(1,n+1):
                model.addConstr(sum(x[(r,c,d)] for c in range(1,n+1))==1)
        for c in range(1,n+1):
            for d in range(1,n+1):
                model.addConstr(sum(x[(r,c,d)] for r in range(1,n+1))==1)
        if block_size!=-1:
            # subgrid constraints
            for r in range(1,n+1,block_size):
                for c in range(1,n+1,block_size):
                    for d in range(1,n+1):
                        model.addConstr(
                            sum(
                                x[rr,cc,d]
                                for rr in range(r,min(r+block_size,n+1))
                                for cc in range(c,min(c+block_size,n+1))
                            )==1
                        )

        model.setObjective(0, GRB.MINIMIZE)
        model.optimize()

        if model.status != GRB.OPTIMAL:
            QMessageBox.warning(self, "No Solution", "Sudoku could not be solved.")
            if block_size**2 != n:
                QMessageBox.warning(self, "Invalid Block Size", 
                    f"Block size {block_size} is invalid for grid {n}x{n}. Must satisfy block_size^2 = n.")
                

            return

        # Build grid
        grid = [[0]*n for _ in range(n)]
        for (r,c,d), var in x.items():
            if var.X > 0.5:
                grid[r-1][c-1] = d

        # Remove cells
        removed = 0
        while removed < eliminate:
            i,j = rand(0,n-1), rand(0,n-1)
            if grid[i][j] != 0:
                grid[i][j] = 0
                removed += 1

        # Display grid with subgrid borders
        cell_size = min(500//n,60)
        for r in range(n):
            for c in range(n):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(cell_size, cell_size)
                val = grid[r][c]

                if val != 0:
                    bg_color = "#3A3A3A"
                    cell.setText(str(val))
                    cell.setStyleSheet(f"background-color:{bg_color}; color:white; font-size:{cell_size//2}px; font-weight:bold;")
                else:
                    bg_color = "#1E1E1E"
                    cell.setText("")
                    cell.setStyleSheet(f"background-color:{bg_color};")

                # Borders for blocks
                top = 2 if r % block_size == 0 else 1
                left = 2 if c % block_size == 0 else 1
                bottom = 2 if (r+1) % block_size == 0 else 1
                right = 2 if (c+1) % block_size == 0 else 1

                cell.setStyleSheet(cell.styleSheet() + f"""
                    border-top:{top}px solid white;
                    border-left:{left}px solid white;
                    border-bottom:{bottom}px solid white;
                    border-right:{right}px solid white;
                """)

                self.board_layout.addWidget(cell, r, c)

        self.stacked.setCurrentWidget(self.board_page)


if __name__=="__main__":
    app = QApplication([])
    win = SudokuSolverGUI()
    win.show()
    app.exec()
