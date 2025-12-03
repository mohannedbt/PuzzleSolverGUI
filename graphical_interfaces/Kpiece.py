from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from gurobipy import Model, GRB

# ----------------------------
# Dark Mode Styles
# ----------------------------
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

COMBO_STYLE = """
QComboBox {
    padding: 8px;
    border: 2px solid #555555;
    border-radius: 6px;
    font-size: 16px;
    background-color: #2C2C2C;
    color: #FFFFFF;
}
QComboBox:hover {
    border: 2px solid #1E90FF;
    background-color: #3A3A3A;
}
"""

LABEL_STYLE = """
font-size: 24px;
font-weight: bold;
color: #FFFFFF;
"""

# ----------------------------
# Main GUI
# ----------------------------
class KPieceSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.custom_pieces = {}   # name → list of attack offsets
        self.setWindowTitle("K-Pieces Solver")
        self.setGeometry(50, 50, 900, 700)
        self.setStyleSheet("background-color: #121212;")
        
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        
        # Pages
        self.menu_page = self.create_menu_page()
        self.input_page = self.create_input_page()
        self.board_page = self.create_board_page()
        self.manual_page = self.create_manual_page()
        self.create_piece_page = self.create_new_piece_page()




        
        self.stacked.addWidget(self.menu_page)
        self.stacked.addWidget(self.input_page)
        self.stacked.addWidget(self.board_page)
        self.stacked.addWidget(self.manual_page)
        self.stacked.addWidget(self.create_piece_page)

    # ---------------- Menu Page ----------------
    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        title = QLabel("K-PIECES SOLVER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:36px;font-weight:bold;color:#FFFFFF;")
        
        start_btn = QPushButton("START")
        start_btn.setStyleSheet(BUTTON_STYLE)
        start_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        manual_btn = QPushButton("📘 MANUAL")
        manual_btn.setStyleSheet(BUTTON_STYLE)
        manual_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.manual_page))
        layout.addWidget(title)
        layout.addWidget(start_btn)
        layout.addWidget(manual_btn)
        return page
    # ----------------------------
    # Manual Page(Scrollable)
    #----------------------------
    def create_manual_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #1E1E1E;")  # dark gray

        # Main layout for the page
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")  # remove borders

        # Container widget inside scroll area
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        scroll_layout.setContentsMargins(30, 20, 30, 20)
        scroll_layout.setSpacing(25)

        # Title
        title = QLabel("📖 K-PIECES SOLVER MANUAL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 40px; font-weight: bold; color: #FFFFFF;")
        scroll_layout.addWidget(title)

        # Instructions
        instructions = QLabel("""
    Welcome to the K-Pieces Solver! Here's how to use it:

    1️⃣ Select the type of piece you want to place on the board:
    - Queen ♛
    - Rook ♜
    - Bishop ♝
    - Knight ♞

    2️⃣ Enter the board size N (e.g., 8 for an 8x8 board).

    3️⃣ Enter the number of pieces K to place on the board.

    4️⃣ Click 🚀 SOLVE to compute a valid placement.

    5️⃣ If a solution exists, the board will display the pieces:
    - Blue background cells with golden border indicate placed pieces.
    - Dark gray cells are empty.

    ⚠️ Notes:
    - Max Queens on N x N board = N
    - Max Knights on N x N board = (N*N + 1) // 2
    - If no solution exists, a warning will appear.

    6️⃣ Click TRY AGAIN to go back and try different parameters.
    7️⃣ Use ⬅ BACK to return to the main menu.
    """)
        instructions.setStyleSheet("font-size: 22px; color: #FFFFFF;")
        instructions.setWordWrap(True)
        scroll_layout.addWidget(instructions)

        # Spacer to push content to top
        scroll_layout.addStretch()

        # Back to Menu button
        back_btn = QPushButton("⬅ BACK TO MENU")
        back_btn.setMinimumHeight(50)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                font-size: 22px;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.menu_page))
        scroll_layout.addWidget(back_btn)

        # Set container as scroll widget
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        return page
    #--------------- toggle --------------------
    def toggle_attack_square(self, r, c):
        btn, base_color = self.custom_cells[(r, c)]

        if btn.isChecked():
            # Highlight green
            btn.setStyleSheet("background-color: #00AA00;")
        else:
            # Return to normal board color
            btn.setStyleSheet(f"background-color: {base_color};")

    #-------------------Piece Page ----------------
    def create_new_piece_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        title = QLabel("➕ Create Custom Piece")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)

        instructions = QLabel(
            "Click squares to mark attack moves.\n"
            "Center square is the piece's position."
        )
        instructions.setStyleSheet("font-size: 18px; color: #CCCCCC;")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # ====== Chessboard grid (8x8) ======
        self.custom_board_size = 8
        size = self.custom_board_size
        self.custom_board_widget = QWidget()
        self.custom_board_widget.setContentsMargins(0, 0, 0, 0)
        self.custom_board_widget.setStyleSheet("margin:0; padding:0; border:0;")

        self.custom_board_layout = QGridLayout(self.custom_board_widget)
        self.custom_board_layout.setSpacing(0)
        self.custom_board_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_board_layout.setSizeConstraint(QLayout.SetFixedSize)
        self.custom_board_widget.setFixedSize(size * 50, size * 50)

        self.custom_cells = {}

        for r in range(size):
            for c in range(size):
                btn = QPushButton()
                btn.setFixedSize(50, 50)
                btn.setCheckable(True)

                base_color = "#EEEED2" if (r + c) % 2 == 0 else "#769656"

                if r == size // 2 and c == size // 2:
                    btn.setText("★")
                    btn.setEnabled(False)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1E90FF;
                            color:white;
                            font-size:28px;
                            margin:0; padding:0; border:0;
                        }
                    """)
                else:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color:{base_color};
                            margin:0; padding:0; border:0;
                        }}
                    """)
                    btn.clicked.connect(lambda _, rr=r, cc=c: self.toggle_attack_square(rr, cc))

                self.custom_cells[(r, c)] = (btn, base_color)
                self.custom_board_layout.addWidget(btn, r, c)


        layout.addWidget(self.custom_board_widget)

        # ====== Piece name ======
        name_label = QLabel("Piece Name:")
        name_label.setStyleSheet("color:white; font-size:20px; font-weight:bold;")
        layout.addWidget(name_label)

        self.new_piece_name = QLineEdit()
        self.new_piece_name.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.new_piece_name)

        # ====== Save button ======
        save_btn = QPushButton("💾 SAVE PIECE")
        save_btn.setStyleSheet(BUTTON_STYLE)
        save_btn.clicked.connect(self.save_custom_piece)
        layout.addWidget(save_btn)

        # ====== Back button ======
        back_btn = QPushButton("⬅ BACK")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        layout.addWidget(back_btn)

        return page


    


    # ---------------- Input Page ----------------
    def create_input_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)

        # Page background color
        page.setStyleSheet("background-color: #1E1E1E;")  # dark gray

        # ---------------- Labels style ----------------
        LABEL_STYLE = """
            color: white;
            font-size: 20px;
            font-weight: bold;
        """

        # ---------------- Piece selection ----------------
        label_piece = QLabel("Select Piece:")
        label_piece.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_piece)

        self.piece_combo = QComboBox()
        self.piece_combo.addItems(["Queen ♛", "Rook ♜", "Bishop ♝","Knight ♞"])
        self.piece_combo.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 2px solid #4ECDC4;
                border-radius: 10px;
                font-size: 18px;
                color: white;
                background-color: #2E2E2E;
            }
            QComboBox:hover {
                border: 2px solid #00CED1;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        layout.addWidget(self.piece_combo)

        # ---------------- Board size ----------------
        label_n = QLabel("Board size N:")
        label_n.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_n)

        self.n_input = QLineEdit()
        self.n_input.setPlaceholderText("Enter board size (e.g., 8)")
        self.n_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #4ECDC4;
                border-radius: 10px;
                font-size: 18px;
                color: white;
                background-color: #2E2E2E;
            }
            QLineEdit:focus {
                border: 2px solid #00CED1;
                background-color: #3E3E3E;
            }
        """)
        layout.addWidget(self.n_input)

        # ---------------- Number of pieces ----------------
        label_k = QLabel("Number of pieces K:")
        label_k.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_k)

        self.k_input = QLineEdit()
        self.k_input.setPlaceholderText("Enter number of pieces (e.g., 8)")
        self.k_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #FFE66D;
                border-radius: 10px;
                font-size: 18px;
                color: white;
                background-color: #2E2E2E;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
                background-color: #3E3E3E;
            }
        """)
        layout.addWidget(self.k_input)

        # ---------------- Solve button ----------------
        self.solve_btn = QPushButton("🚀 SOLVE")
        self.solve_btn.setMinimumHeight(50)
        self.solve_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: #1E1E1E;
                font-weight: bold;
                font-size: 20px;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00CED1;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
            }
        """)
        self.solve_btn.clicked.connect(self.solve)
        layout.addWidget(self.solve_btn)
        # --------------- New Piece ----------------------

        new_piece_btn = QPushButton("➕ CREATE NEW PIECE")
        new_piece_btn.setMinimumHeight(50)
        new_piece_btn.setCursor(Qt.PointingHandCursor)
        new_piece_btn.setStyleSheet(BUTTON_STYLE)
        new_piece_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.create_piece_page))
        layout.addWidget(new_piece_btn)

        # ---------------- Back button ----------------
        back_btn = QPushButton("⬅ BACK")
        back_btn.setMinimumHeight(50)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.menu_page))
        layout.addWidget(back_btn)

        return page


    # ---------------- Board Page ----------------
    def create_board_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Board container
        self.board_widget = QWidget()
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(1)
        self.board_widget.setLayout(self.board_layout)
        layout.addWidget(self.board_widget)
        
        # Try again button
        self.back_btn_board = QPushButton("TRY AGAIN")
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
    # ---------------- save Custom piece ------------
    def save_custom_piece(self):
        name = self.new_piece_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Enter a piece name.")
            return

        center = self.custom_board_size // 2
        attacks = []

        # Iterate on real dictionary
        for (r, c), (btn, base_color) in self.custom_cells.items():
            if r == center and c == center:
                continue  # skip center

            if btn.isChecked():  # green square
                dr = r - center
                dc = c - center
                attacks.append((dr, dc))

        if not attacks:
            QMessageBox.warning(self, "Error", "Select at least one attack square.")
            return

        # Save the custom piece
        self.custom_pieces[name] = attacks

        # Add into combo
        self.piece_combo.addItem(f"{name} ⭐")

        QMessageBox.information(self, "Saved", f"Piece '{name}' added!")

        self.stacked.setCurrentWidget(self.input_page)



    # ---------------- Solve ----------------
    def solve(self):
        self.clear_board()

        # ---------------- Parse Inputs ----------------
        try:
            piece_text = self.piece_combo.currentText()
            piece = piece_text.split()[0]     # name before symbol
            n = int(self.n_input.text())
            k = int(self.k_input.text())
        except:
            QMessageBox.warning(self, "Input Error", "Enter valid numbers.")
            return

        # ---------------- Select Display Symbol ----------------
        default_symbols = {
            "Queen":  "♛",
            "Rook":   "♜",
            "Bishop": "♝",
            "Knight": "♞",
        }

        if piece in default_symbols:
            symbol = default_symbols[piece]
        else:
            # Custom pieces get a ⭐ symbol
            symbol = "⭐"

        # ---------------- Quick Impossible Checks ----------------
        if piece == "Queen" and k > n:
            QMessageBox.warning(self, "Impossible", f"Max {n} Queens on {n}x{n} board!")
            return

        if piece == "Knight" and k > (n*n + 1)//2:
            QMessageBox.warning(self, "Impossible", f"Max {(n*n + 1)//2} Knights on {n}x{n} board!")
            return

        # ---------------- Gurobi Model ----------------
        model = Model("K_Pieces")
        model.setParam("OutputFlag", 0)

        x = {}
        for r in range(1, n+1):
            for c in range(1, n+1):
                x[(r, c)] = model.addVar(vtype=GRB.BINARY)

        # ---------------- Constraints ----------------
        # Custom pieces
        if piece in self.custom_pieces:
            moves = self.custom_pieces[piece]
            for r in range(1, n+1):
                for c in range(1, n+1):
                    for dr, dc in moves:
                        rr = r + dr
                        cc = c + dc
                        if 1 <= rr <= n and 1 <= cc <= n:
                            model.addConstr(x[(r, c)] + x[(rr, cc)] <= 1)

        # Rook/Queen – rows & columns
        if piece in ["Queen", "Rook"]:
            for r in range(1, n+1):
                model.addConstr(sum(x[(r, c)] for c in range(1, n+1)) <= 1)
            for c in range(1, n+1):
                model.addConstr(sum(x[(r, c)] for r in range(1, n+1)) <= 1)

        # Bishop/Queen – diagonals
        if piece in ["Queen", "Bishop"]:
            for b in range(-(n-1), n):
                model.addConstr(sum(x[(r, c)] for r in range(1, n+1)
                                                for c in range(1, n+1)
                                                if r-c == b) <= 1)

            for b in range(2, 2*n):
                model.addConstr(sum(x[(r, c)] for r in range(1, n+1)
                                                for c in range(1, n+1)
                                                if r+c == b) <= 1)

        # Knight
        if piece == "Knight":
            moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
            for r in range(1, n+1):
                for c in range(1, n+1):
                    for dr, dc in moves:
                        rr, cc = r+dr, c+dc
                        if 1 <= rr <= n and 1 <= cc <= n:
                            model.addConstr(x[(r, c)] + x[(rr, cc)] <= 1)

        # exactly K pieces
        model.addConstr(sum(x[(r, c)] for r in range(1, n+1)
                                    for c in range(1, n+1)) == k)

        model.setObjective(0, GRB.MINIMIZE)
        model.optimize()

        if model.status != GRB.OPTIMAL:
            QMessageBox.warning(self, "No Solution",
                                f"Cannot place {k} {piece}s on {n}x{n} board!")
            return

        # ---------------- Build Output Grid ----------------
        grid = [[0]*n for _ in range(n)]
        for (r, c), var in x.items():
            if var.X > 0.5:
                grid[r-1][c-1] = 1

        # ---------------- Draw Board ----------------
        cell_size = min(500//n, 60)

        for r in range(n):
            for c in range(n):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(cell_size, cell_size)

                color = "#3A3A3A" if (r+c) % 2 == 0 else "#2C2C2C"

                if grid[r][c] == 1:
                    cell.setText(symbol)
                    cell.setStyleSheet(
                        f"background-color:#1E90FF;color:white;"
                        f"font-size:{cell_size//2}px;font-weight:bold;"
                        f"border:2px solid #FFD700;"
                    )
                else:
                    cell.setStyleSheet(
                        f"background-color:{color};border:1px solid #555555;"
                    )

                self.board_layout.addWidget(cell, r, c)

        self.stacked.setCurrentWidget(self.board_page)
