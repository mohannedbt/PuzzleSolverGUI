from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from graphic1 import SudokuSolverGUI
from graphic2 import KPieceSolverGUI

# ---------------------------- Styles ----------------------------
WINDOW_BG = "#121212"
HERO_BG = "#1E1E1E"
BUTTON_PRIMARY = "#4ECDC4"
BUTTON_SECONDARY = "#FF6B6B"
BUTTON_HOVER_PRIMARY = "#00CED1"
BUTTON_HOVER_SECONDARY = "#FF5252"
TEXT_COLOR = "#FFFFFF"
TITLE_COLOR = "#FFD700"

BUTTON_STYLE = f"""
QPushButton {{
    background-color: {BUTTON_PRIMARY};
    color: {WINDOW_BG};
    font-size: 20px;
    font-weight: bold;
    border-radius: 12px;
    padding: 15px 30px;
}}
QPushButton:hover {{
    background-color: {BUTTON_HOVER_PRIMARY};
}}
"""

BUTTON_STYLE_SECONDARY = f"""
QPushButton {{
    background-color: {BUTTON_SECONDARY};
    color: {TEXT_COLOR};
    font-size: 20px;
    font-weight: bold;
    border-radius: 12px;
    padding: 15px 30px;
}}
QPushButton:hover {{
    background-color: {BUTTON_HOVER_SECONDARY};
}}
"""

TITLE_STYLE = f"font-size:48px;font-weight:bold;color:{TITLE_COLOR};"
SUBTITLE_STYLE = f"font-size:24px;color:{TEXT_COLOR};"

# ---------------------------- Main GUI ----------------------------
class MainLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark Mode Launcher")
        self.setGeometry(50, 50, 1000, 700)
        self.setStyleSheet(f"background-color: {WINDOW_BG};")

        # Main stacked widget
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Pages
        self.hero_page = self.create_hero_page()
        self.stacked.addWidget(self.hero_page)

        # Here you can import your other GUI classes

        self.sudoku_page = SudokuSolverGUI().centralWidget()
        self.kpieces_page = KPieceSolverGUI().centralWidget()
        self.stacked.addWidget(self.sudoku_page)
        self.stacked.addWidget(self.kpieces_page)

    # ---------------- Hero Page ----------------
    def create_hero_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(50)

        # Hero Title
        title = QLabel("🧩 Welcome to the Puzzle Hub")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(TITLE_STYLE)
        layout.addWidget(title)

        subtitle = QLabel("Solve Sudoku & K-Pieces puzzles in one place!")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(subtitle)

        # Buttons container
        btn_container = QHBoxLayout()
        btn_container.setSpacing(40)

        # Sudoku Button
        sudoku_btn = QPushButton("Sudoku Solver")
        sudoku_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sudoku_btn.setStyleSheet(BUTTON_STYLE)
        sudoku_btn.clicked.connect(self.open_sudoku)
        btn_container.addWidget(sudoku_btn)

        # K-Pieces Button
        kpieces_btn = QPushButton("K-Pieces Solver")
        kpieces_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        kpieces_btn.setStyleSheet(BUTTON_STYLE_SECONDARY)
        kpieces_btn.clicked.connect(self.open_kpieces)
        btn_container.addWidget(kpieces_btn)

        layout.addLayout(btn_container)
        return page

    # ---------------- Button Actions ----------------
    def open_sudoku(self):
        self.sudoku_win = SudokuSolverGUI()
        self.sudoku_win.show() 
    def open_kpieces(self):
        self.kpiece_win = KPieceSolverGUI()
        self.kpiece_win.show() 


if __name__ == "__main__":
    app = QApplication([])
    win = MainLauncher()
    win.show()
    app.exec()
