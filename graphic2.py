from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from gurobipy import Model, GRB

class ChessSolverGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K-Pieces Solver")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Inputs
        input_layout = QHBoxLayout()
        self.piece_combo = QComboBox()
        self.piece_combo.addItems(["Queen","Rook","Bishop"])
        self.n_input = QLineEdit(); self.n_input.setPlaceholderText("Board size N")
        self.k_input = QLineEdit(); self.k_input.setPlaceholderText("Number of Pieces K")
        self.solve_btn = QPushButton("Solve")
        self.solve_btn.clicked.connect(self.solve)
        input_layout.addWidget(QLabel("Piece:")); input_layout.addWidget(self.piece_combo)
        input_layout.addWidget(QLabel("N:")); input_layout.addWidget(self.n_input)
        input_layout.addWidget(QLabel("K:")); input_layout.addWidget(self.k_input)
        input_layout.addWidget(self.solve_btn)
        self.layout.addLayout(input_layout)

        # Board
        self.board_widget = QWidget()
        self.board_layout = QGridLayout()
        self.board_widget.setLayout(self.board_layout)
        self.layout.addWidget(self.board_widget)

    def clear_board(self):
        for i in reversed(range(self.board_layout.count())):
            self.board_layout.itemAt(i).widget().deleteLater()

    def solve(self):
        self.clear_board()
        try:
            piece = self.piece_combo.currentText()
            n = int(self.n_input.text())
            k = int(self.k_input.text())
            if k > n and piece=="Queen":
                QMessageBox.warning(self,"Error","K must be <= N for Queen")
                return
        except:
            QMessageBox.warning(self,"Error","Invalid input")
            return

        # --- Create Gurobi model ---
        model = Model("K_Pieces")
        x = {}
        for r in range(1,n+1):
            for c in range(1,n+1):
                x[(r,c)] = model.addVar(vtype=GRB.BINARY,name=f"x_{r}_{c}")
        # Row/Column constraints
        if piece in ["Rook","Queen"]:
            for r in range(1,n+1):
                model.addConstr(sum(x[(r,c)] for c in range(1,n+1)) <= 1)
            for c in range(1,n+1):
                model.addConstr(sum(x[(r,c)] for r in range(1,n+1)) <= 1)
        if piece in ["Bishop","Queen"]:
            for d in range(-(n-1), n):
                model.addConstr(sum(x[(r,c)] for r in range(1,n+1) for c in range(1,n+1) if r-c==d) <=1)
            for d in range(2,2*n):
                model.addConstr(sum(x[(r,c)] for r in range(1,n+1) for c in range(1,n+1) if r+c==d) <=1)
        model.addConstr(sum(x[(r,c)] for r in range(1,n+1) for c in range(1,n+1))==k)
        model.setObjective(0, GRB.MINIMIZE)
        model.optimize()

        if model.status != GRB.OPTIMAL:
            QMessageBox.information(self,"Result","No solution found")
            return

        # Build board
        grid = [[0]*n for _ in range(n)]
        for (r,c), var in x.items():
            if var.X>0.5:
                grid[r-1][c-1]=1

        # Show board with highlights
        for r in range(n):
            for c in range(n):
                cell = QLabel()
                cell.setAlignment(Qt.AlignCenter)
                cell.setFixedSize(40,40)
                # Chess colors
                if (r+c)%2==0:
                    cell.setStyleSheet("background-color: #eee; border: 1px solid black;")
                else:
                    cell.setStyleSheet("background-color: #aaa; border: 1px solid black;")
                if grid[r][c]==1:
                    cell.setText(piece[0])
                    cell.setStyleSheet("background-color: #ff6666; border:1px solid black; font-weight:bold; font-size:16px;")
                    # Highlight dominated squares
                    attacked = self.get_attacks(piece, r, c, n)
                    for ar,ac in attacked:
                        # We'll update later after all cells created
                        pass
                self.board_layout.addWidget(cell,r,c)

        # Highlight dominated squares (separate pass)
        for r in range(n):
            for c in range(n):
                if grid[r][c]==1:
                    attacked = self.get_attacks(piece, r, c, n)
                    for ar, ac in attacked:
                        cell = self.board_layout.itemAtPosition(ar,ac).widget()
                        # Only color if empty
                        if grid[ar][ac]==0:
                            cell.setStyleSheet("background-color: #ffff99; border:1px solid black;")

    def get_attacks(self, piece, r, c, n):
        attacked = set()
        if piece in ["Rook","Queen"]:
            for i in range(n):
                if i!=c: attacked.add((r,i))
                if i!=r: attacked.add((i,c))
        if piece in ["Bishop","Queen"]:
            for i in range(n):
                for j in range(n):
                    if abs(r-i)==abs(c-j) and (i,j)!=(r,c):
                        attacked.add((i,j))
        return attacked

if __name__=="__main__":
    app = QApplication([])
    window = ChessSolverGUI()
    window.show()
    app.exec()
