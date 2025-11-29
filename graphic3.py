from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from gurobipy import Model, GRB

# ---------------- Styles ----------------
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
QPushButton:hover {
    background-color: #3AA0FF;
}
QPushButton:pressed {
    background-color: #105CB3;
}
"""

LABEL_STYLE = """
font-size: 20px;
font-weight: bold;
color: #FFFFFF;
"""

# ---------------- Tetris pieces ----------------
PIECES = {
    "I": [[(0,0),(1,0),(2,0),(3,0)], [(0,0),(0,1),(0,2),(0,3)]],
    "O": [[(0,0),(0,1),(1,0),(1,1)]],
    "T": [[(0,0),(0,1),(0,2),(1,1)], [(0,1),(1,0),(1,1),(2,1)],
          [(1,0),(1,1),(1,2),(0,1)], [(0,0),(1,0),(1,1),(2,0)]],
    "S": [[(0,1),(0,2),(1,0),(1,1)], [(0,0),(1,0),(1,1),(2,1)]],
    "Z": [[(0,0),(0,1),(1,1),(1,2)], [(0,1),(1,0),(1,1),(2,0)]],
    "J": [[(0,0),(1,0),(2,0),(2,1)], [(0,0),(0,1),(0,2),(1,0)],
          [(0,0),(0,1),(1,1),(2,1)], [(0,2),(1,0),(1,1),(1,2)]],
    "L": [[(0,1),(1,1),(2,1),(2,0)], [(0,0),(1,0),(1,1),(1,2)],
          [(0,0),(0,1),(1,0),(2,0)], [(0,0),(0,1),(0,2),(1,2)]]
}

# Distinct border colors for each piece
BORDERS = {
    "I": "#FF4136", "O": "#FFDC00", "T": "#B10DC9",
    "S": "#2ECC40", "Z": "#FF851B", "J": "#0074D9", "L": "#FF69B4"
}

# ---------------- Helper functions ----------------
def piece_fits(shape, r, c, rows, cols):
    for dr,dc in shape:
        rr,cc = r+dr, c+dc
        if rr<0 or rr>=rows or cc<0 or cc>=cols:
            return False
    return True

def cells_covered_by(shape, r, c):
    return [(r+dr, c+dc) for dr,dc in shape]

# ---------------- GUI ----------------
class TetrisKPiecesGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tetris K-Pieces Solver")
        self.setGeometry(50,50,900,700)
        self.setStyleSheet("background-color: #121212;")
        
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        
        self.menu_page = self.create_menu_page()
        self.input_page = self.create_input_page()
        self.board_page = self.create_board_page()
        
        self.stacked.addWidget(self.menu_page)
        self.stacked.addWidget(self.input_page)
        self.stacked.addWidget(self.board_page)
    
    # ---------------- Menu ----------------
    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        title = QLabel("TETRIS K-PIECES SOLVER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:32px;font-weight:bold;color:white;")
        
        start_btn = QPushButton("START")
        start_btn.setStyleSheet(BUTTON_STYLE)
        start_btn.clicked.connect(lambda:self.stacked.setCurrentWidget(self.input_page))
        
        layout.addWidget(title)
        layout.addWidget(start_btn)
        return page
    
    # ---------------- Input ----------------
    def create_input_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50,30,50,30)
        page.setStyleSheet("background-color: #1E1E1E;")
        
        # Board size N
        label_rows = QLabel("Rows (N):")
        label_rows.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_rows)
        self.rows_input = QLineEdit()
        self.rows_input.setPlaceholderText("e.g., 6")
        layout.addWidget(self.rows_input)
        
        label_cols = QLabel("Columns (N):")
        label_cols.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_cols)
        self.cols_input = QLineEdit()
        self.cols_input.setPlaceholderText("e.g., 6")
        layout.addWidget(self.cols_input)
        
        # Number of pieces K
        label_k = QLabel("Number of pieces (K):")
        label_k.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_k)
        self.k_input = QLineEdit()
        self.k_input.setPlaceholderText("e.g., 4")
        layout.addWidget(self.k_input)
        
        # Piece selection (ComboBox)
        label_piece = QLabel("Select Piece:")
        label_piece.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_piece)
        
        self.piece_combo = QComboBox()
        self.piece_combo.addItems(list(PIECES.keys()))
        self.piece_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #4ECDC4;
                border-radius: 8px;
                font-size: 18px;
                color: white;
                background-color: #2E2E2E;
            }
            QComboBox:hover { border:2px solid #00CED1; }
        """)
        layout.addWidget(self.piece_combo)
        
        # Solve button
        solve_btn = QPushButton("🚀 SOLVE")
        solve_btn.setStyleSheet(BUTTON_STYLE)
        solve_btn.clicked.connect(self.solve)
        layout.addWidget(solve_btn)
        
        # Back button
        back_btn = QPushButton("⬅ BACK")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda:self.stacked.setCurrentWidget(self.menu_page))
        layout.addWidget(back_btn)
        
        return page
    
    # ---------------- Board ----------------
    def create_board_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.board_widget = QWidget()
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(0)
        self.board_widget.setLayout(self.board_layout)
        layout.addWidget(self.board_widget)
        
        # Try again
        back_btn = QPushButton("TRY AGAIN")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda:self.stacked.setCurrentWidget(self.input_page))
        layout.addWidget(back_btn)
        return page
    
    def clear_board(self):
        for i in reversed(range(self.board_layout.count())):
            w = self.board_layout.itemAt(i).widget()
            if w: w.deleteLater()
    
    # ---------------- Solve ----------------
    def solve(self):
        self.clear_board()
        try:
            rows = int(self.rows_input.text())
            cols = int(self.cols_input.text())
            K = int(self.k_input.text())
        except:
            QMessageBox.warning(self,"Input Error","Enter valid integers")
            return
        
        piece_name = self.piece_combo.currentText()
        rotations = PIECES[piece_name]
        border_color = BORDERS[piece_name]
        
        # ---------------- Gurobi Model ----------------
        model = Model("Tetris_KPieces")
        model.setParam("OutputFlag",0)
        x = {}
        for shape in rotations:
            for r in range(rows):
                for c in range(cols):
                    if piece_fits(shape,r,c,rows,cols):
                        x[(r,c,str(shape))] = model.addVar(vtype=GRB.BINARY)
        
        # Non-overlapping constraints
        for i in range(rows):
            for j in range(cols):
                model.addConstr(
                    sum(var for (r,c,sh),var in x.items() if (i,j) in cells_covered_by(eval(sh),r,c)) <= 1
                )
        
        # Total pieces K
        model.addConstr(sum(x.values()) == K)
        model.setObjective(0,GRB.MINIMIZE)
        model.optimize()
        
        if model.status != GRB.OPTIMAL:
            QMessageBox.warning(self,"No Solution","Cannot place pieces without overlaps")
            return
        
        # ---------------- Build grid ----------------
        grid = [["" for _ in range(cols)] for _ in range(rows)]
        for (r,c,sh),var in x.items():
            if var.X > 0.5:
                for rr,cc in cells_covered_by(eval(sh),r,c):
                    grid[rr][cc] = piece_name
        
        cell_size = min(500//cols,60)
        
        for r in range(rows):
            for c in range(cols):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(cell_size,cell_size)
                piece = grid[r][c]
                if piece:
                    cell.setText(piece)
                    cell.setStyleSheet(f"background-color:#1E90FF;color:white;font-weight:bold;font-size:{cell_size//2}px;border:2px solid {border_color};")
                else:
                    cell.setStyleSheet("background-color:#1E1E1E;border:1px solid #333;")
                self.board_layout.addWidget(cell,r,c)
        
        self.stacked.setCurrentWidget(self.board_page)


if __name__=="__main__":
    app = QApplication([])
    win = TetrisKPiecesGUI()
    win.show()
    app.exec()
