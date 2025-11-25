from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from gurobipy import Model, GRB

# ----------------------------
# Global Styles (reusable)
# ----------------------------
BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FF6B6B, stop:1 #4ECDC4);
    color: white;
    border: 4px solid white;
    border-radius: 15px;
    font-size: 24px;
    font-weight: bold;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4ECDC4, stop:1 #FF6B6B);
    border: 4px solid yellow;
}
QPushButton:pressed {
    background: #00FF00;
}
"""

LABEL_TITLE_STYLE = """
font-size: 40px;
font-weight: bold;
color: white;
background: rgba(0,0,0,0.4);
padding: 20px;
border: 4px solid white;
border-radius: 20px;
"""

INPUT_STYLE = """
QLineEdit {
    padding: 12px;
    border: 3px solid #4ECDC4;
    border-radius: 12px;
    font-size: 18px;
    background: #E6F9FF;
}
QLineEdit:focus {
    border: 3px solid #00CED1;
    background: white;
}
"""

COMBO_STYLE = """
QComboBox {
    padding: 12px;
    border: 3px solid #FF6B6B;
    border-radius: 12px;
    font-size: 18px;
    background: #FFF9E6;
}
QComboBox:hover {
    border: 3px solid #FF0080;
    background: #FFFFE0;
}
"""

# ----------------------------
# Main Application
# ----------------------------
class KPieceSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K-Pieces Solver")
        self.setGeometry(50,50,900,700)
        self.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #FF6B6B, stop:0.5 #FFE66D, stop:1 #4ECDC4);")
        
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        
        # Pages
        self.menu_page = self.create_menu_page()
        self.input_page = self.create_input_page()
        self.board_page = self.create_board_page()
        
        self.stacked.addWidget(self.menu_page)
        self.stacked.addWidget(self.input_page)
        self.stacked.addWidget(self.board_page)
    
    # ---------------- Menu Page ----------------
    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        title = QLabel("🤯 K-PIECES SOLVER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(LABEL_TITLE_STYLE)
        
        start_btn = QPushButton("🎮 START")
        start_btn.setMinimumHeight(60)
        start_btn.setStyleSheet(BUTTON_STYLE)
        start_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        
        layout.addWidget(title)
        layout.addWidget(start_btn)
        return page
    
    # ---------------- Input Page ----------------
    def create_input_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Piece selection
        self.piece_combo = QComboBox()
        self.piece_combo.addItems(["Queen ♛", "Rook ♜", "Bishop ♝"])
        self.piece_combo.setStyleSheet(COMBO_STYLE)
        
        # Board size
        self.n_input = QLineEdit()
        self.n_input.setPlaceholderText("Board size N")
        self.n_input.setStyleSheet(INPUT_STYLE)
        
        # Number of pieces
        self.k_input = QLineEdit()
        self.k_input.setPlaceholderText("Number of pieces K")
        self.k_input.setStyleSheet(INPUT_STYLE)
        
        # Solve button
        self.solve_btn = QPushButton("🚀 SOLVE")
        self.solve_btn.setStyleSheet(BUTTON_STYLE)
        self.solve_btn.clicked.connect(self.solve)
        
        # Back button
        back_btn = QPushButton("⬅ BACK")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.menu_page))
        
        layout.addWidget(QLabel("Select Piece:"))
        layout.addWidget(self.piece_combo)
        layout.addWidget(QLabel("Board size N:"))
        layout.addWidget(self.n_input)
        layout.addWidget(QLabel("Number of pieces K:"))
        layout.addWidget(self.k_input)
        layout.addWidget(self.solve_btn)
        layout.addWidget(back_btn)
        
        return page
    
    # ---------------- Board Page ----------------
    def create_board_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.board_widget = QWidget()
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(2)
        self.board_widget.setLayout(self.board_layout)
        layout.addWidget(self.board_widget)
        
        self.back_btn_board = QPushButton("🔄 TRY AGAIN")
        self.back_btn_board.setStyleSheet(BUTTON_STYLE)
        self.back_btn_board.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        layout.addWidget(self.back_btn_board)
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
            piece = self.piece_combo.currentText().split()[0]
            n = int(self.n_input.text())
            k = int(self.k_input.text())
        except:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers.")
            return
        
        if piece=="Queen" and k>n:
            QMessageBox.warning(self, "Impossible", f"Max {n} Queens on {n}x{n} board!")
            return
        
        # ---------------- Gurobi Model ----------------
        model = Model("K_Pieces")
        model.setParam("OutputFlag",0)
        x = {}
        for r in range(1,n+1):
            for c in range(1,n+1):
                x[(r,c)] = model.addVar(vtype=GRB.BINARY)
        
        # Row/Column constraints
        if piece in ["Queen","Rook"]:
            for r in range(1,n+1):
                model.addConstr(sum(x[(r,c)] for c in range(1,n+1)) <= 1)
            for c in range(1,n+1):
                model.addConstr(sum(x[(r,c)] for r in range(1,n+1)) <= 1)
        if piece in ["Queen","Bishop"]:
            for d in range(-(n-1), n):
                model.addConstr(sum(x[(r,c)] for r in range(1,n+1) for c in range(1,n+1) if r-c==d)<=1)
            for d in range(2,2*n):
                model.addConstr(sum(x[(r,c)] for r in range(1,n+1) for c in range(1,n+1) if r+c==d)<=1)
        
        model.addConstr(sum(x[(r,c)] for r in range(1,n+1) for c in range(1,n+1))==k)
        model.setObjective(0,GRB.MINIMIZE)
        model.optimize()
        
        if model.status!=GRB.OPTIMAL:
            QMessageBox.warning(self,"No Solution", f"Cannot place {k} {piece}s on {n}x{n} board!")
            return
        
        grid = [[0]*n for _ in range(n)]
        for (r,c), var in x.items():
            if var.X>0.5:
                grid[r-1][c-1]=1
        
        # Display board
        cell_size = min(500//n,60)
        symbol={"Queen":"♛","Rook":"♜","Bishop":"♝"}[piece]
        
        for r in range(n):
            for c in range(n):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(cell_size,cell_size)
                color = "#F0D9B5" if (r+c)%2==0 else "#B58863"
                if grid[r][c]==1:
                    cell.setText(symbol)
                    cell.setStyleSheet(f"background:#FF6B6B;color:white;font-size:{cell_size//2}px;")
                else:
                    cell.setStyleSheet(f"background:{color};")
                self.board_layout.addWidget(cell,r,c)
        
        self.stacked.setCurrentWidget(self.board_page)

if __name__=="__main__":
    app=QApplication([])
    win=KPieceSolverGUI()
    win.show()
    app.exec()
