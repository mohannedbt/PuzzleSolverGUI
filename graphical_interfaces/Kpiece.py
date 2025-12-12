# full_kpieces_with_place_existing.py
from functools import partial
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
    font-family: 'Comic Sans MS'
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
    font-family: 'Comic Sans MS'
    
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
    font-family: 'Comic Sans MS'
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
font-family: 'Comic Sans MS'
"""

# ----------------------------
# Main GUI
# ----------------------------
class KPieceSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.custom_pieces = {}   # name → {'offsets':[(dr,dc)...], 'special':[...]}
        self.setWindowTitle("K-Pieces Solver")
        self.setGeometry(50, 50, 1000, 760)
        self.setStyleSheet("background-color: #121212;font-family: 'Comic Sans MS'")
        self.special_attacks = []
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        self.piece_map = {
    "King": "♔",
    "Queen": "♕",
    "Rook": "♖",
    "Bishop": "♗",
    "Knight": "♘",
    "Pawn": "♙"
}
        
        # Will hold existing manual placements: {(r,c): piece_name} using 1-based indices
        self.existing_placements = {}

        # default board size for creation pages
        self.board_size = 8

        # Pages
        self.menu_page = self.create_menu_page()
        self.input_page = self.create_input_page()
        self.board_page = self.create_board_page()
        self.manual_page = self.create_manual_page()
        self.create_piece_page = self.create_new_piece_page()
        self.place_existing_page = self.create_place_existing_page()

        self.stacked.addWidget(self.menu_page)
        self.stacked.addWidget(self.input_page)
        self.stacked.addWidget(self.board_page)
        self.stacked.addWidget(self.manual_page)
        self.stacked.addWidget(self.create_piece_page)
        self.stacked.addWidget(self.place_existing_page)

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

    # ---------------------------- Manual Page ----------------
    def create_manual_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #1E1E1E;")
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        scroll_layout.setContentsMargins(30,20,30,20)
        scroll_layout.setSpacing(25)
        title = QLabel("📖 K-PIECES SOLVER MANUAL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 40px; font-weight: bold; color: #FFFFFF;")
        scroll_layout.addWidget(title)
        instructions = QLabel("""
    Welcome to the K-Pieces Solver! Here's how to use it:

    1️⃣ Select the type of piece you want to place on the board:
    - Queen ♛
    - Rook ♜
    - Bishop ♝
    - Knight ♞
    - Custom pieces (create your own!)
    You can create custom pieces by defining their attack patterns.
                              

    2️⃣ Enter the board size N (e.g., 8 for an 8x8 board).

    3️⃣ Enter the number of pieces K to place on the board (for the single-type solver).

    4️⃣ Click 🚀 SOLVE to compute a valid placement — or use PLACE EXISTING PIECES
       to manually place existing pieces then maximize type X.

    5️⃣ If a solution exists, the board will display the pieces.
    """)
        instructions.setStyleSheet("font-size: 22px; color: #FFFFFF;")
        instructions.setWordWrap(True)
        scroll_layout.addWidget(instructions)
        scroll_layout.addStretch()
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
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        return page
    
    # -------------------Piece Page ----------------
    def create_new_piece_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        title = QLabel("➕ Create Custom Piece")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)
        instructions = QLabel("Click squares to mark attack moves.\nCenter square is the piece's position.\nOr tick standard directions:")
        instructions.setStyleSheet("font-size: 18px; color: #CCCCCC;")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        self.row_cb = QCheckBox("Row")
        self.col_cb = QCheckBox("Column")
        self.diag_cb = QCheckBox("Diagonals")
        for cb in [self.row_cb, self.col_cb, self.diag_cb]:
            cb.setStyleSheet("color:white; font-size:16px;")
            cb.stateChanged.connect(self.update_standard_highlights)
        cb_layout = QHBoxLayout()
        cb_layout.addWidget(self.row_cb)
        cb_layout.addWidget(self.col_cb)
        cb_layout.addWidget(self.diag_cb)
        layout.addLayout(cb_layout)
        # Chessboard grid (8x8)
        self.custom_board_size = 8
        size = self.custom_board_size
        self.custom_board_widget = QWidget()
        self.custom_board_layout = QGridLayout(self.custom_board_widget)
        self.custom_board_layout.setSpacing(0)
        self.custom_board_layout.setContentsMargins(0,0,0,0)
        self.custom_board_widget.setFixedSize(size*50, size*50)
        self.custom_board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.custom_cells = {}
        for r in range(size):
            for c in range(size):
                btn = QPushButton()
                btn.setFixedSize(50, 50)
                btn.setCheckable(True)
                base_color = "#EEEED2" if (r+c)%2==0 else "#769656"
                if r == size//2 and c == size//2:
                    btn.setText("★")
                    btn.setEnabled(False)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color:#1E90FF;
                            color:white;
                            font-size:28px;
                            margin:0; padding:0; border:0; border-radius:0;
                        }   """)
                else:
                    btn.setStyleSheet(f"QPushButton {{background-color:{base_color};margin:0;padding:0;border:0;border-radius:0;}}")
                    btn.clicked.connect(partial(self.toggle_attack_square, r, c))
                self.custom_cells[(r,c)] = {'btn': btn, 'base_color': base_color, 'manual': False, 'standard': False}
                self.custom_board_layout.addWidget(btn, r, c)
        layout.addWidget(self.custom_board_widget)
        name_label = QLabel("Piece Name:")
        name_label.setStyleSheet("color:white; font-size:20px; font-weight:bold;")
        layout.addWidget(name_label)
        self.new_piece_name = QLineEdit()
        self.new_piece_name.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.new_piece_name)
        save_btn = QPushButton("💾 SAVE PIECE")
        save_btn.setStyleSheet(BUTTON_STYLE)
        save_btn.clicked.connect(self.save_custom_piece)
        layout.addWidget(save_btn)
        back_btn = QPushButton("⬅ BACK")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        layout.addWidget(back_btn)
        return page

    # ---------------- Update Standard Highlights ----------------
    def update_standard_highlights(self):
        center = self.custom_board_size//2
        size = self.custom_board_size
        for (r, c), cell in self.custom_cells.items():
            if r == center and c == center:
                continue
            cell['standard'] = False
            if self.row_cb.isChecked() and r == center:
                cell['standard'] = True
            if self.col_cb.isChecked() and c == center:
                cell['standard'] = True
            if self.diag_cb.isChecked() and (r-center == c-center or r-center == center-c):
                cell['standard'] = True
            self.update_cell_color(r, c)

    # ---------------- Toggle Manual Attack ----------------
    def toggle_attack_square(self, r, c):
        cell = self.custom_cells[(r, c)]
        cell['manual'] = not cell['manual']
        self.update_cell_color(r, c)

    # ---------------- Update Cell Color ----------------
    def update_cell_color(self, r, c):
        cell = self.custom_cells[(r, c)]
        btn = cell['btn']
        base = cell['base_color']
        if cell['manual']:
            btn.setStyleSheet("background-color:#00AA00;margin:0;padding:0;border:0;border-radius:0")
        elif cell['standard']:
            btn.setStyleSheet("background-color:#88FF88;margin:0;padding:0;border:0;border-radius:0")
        else:
            btn.setStyleSheet(f"background-color:{base};margin:0;padding:0;border:0;border-radius:0")

    # ---------------- save custom piece ----------------
    def save_custom_piece(self):
        name = self.new_piece_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Enter a piece name.")
            return
        center = self.custom_board_size // 2
        attacks = []
        for (r, c), cell in self.custom_cells.items():
            if r == center and c == center:
                continue
            if cell['manual']:
                dr = r - center
                dc = c - center
                attacks.append((dr, dc))
        # Special directions
        special = []
        if self.row_cb.isChecked():
            special.append('row')
        if self.col_cb.isChecked():
            special.append('col')
        if self.diag_cb.isChecked():
            special.append('diag')
        if not attacks and not special:
            QMessageBox.warning(self, "Error", "Select at least one attack square or direction.")
            return
        # Save the custom piece (store both offsets and special flags)
        self.custom_pieces[name] = {'offsets': attacks, 'special': special}
        # add to combo on input page
        try:
            self.piece_combo.addItem(f"{name} ⭐")
        except Exception:
            pass
        # refresh placement page combos
        self.refresh_place_existing_page()
        QMessageBox.information(self, "Saved", f"Piece '{name}' added!")
        # Reset
        self.row_cb.setChecked(False)
        self.col_cb.setChecked(False)
        self.diag_cb.setChecked(False)
        for cell in self.custom_cells.values():
            cell['manual'] = False
            cell['standard'] = False
            btn = cell['btn']
            btn.setStyleSheet(f"background-color:{cell['base_color']};padding:0;border:0;border-radius:0")
        self.new_piece_name.clear()
        self.stacked.setCurrentWidget(self.input_page)

    # ---------------- Input Page ----------------
    def create_input_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        page.setStyleSheet("background-color: #1E1E1E;")
        LABEL_STYLE = """
            color: white;
            font-size: 20px;
            font-weight: bold;
        """
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
        label_n = QLabel("Board size N:")
        label_n.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label_n)
        self.n_input = QLineEdit()
        self.n_input.setPlaceholderText("Enter board size (e.g., 8)")
        self.n_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.n_input)
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
        new_piece_btn = QPushButton("➕ CREATE NEW PIECE")
        new_piece_btn.setMinimumHeight(50)
        new_piece_btn.setCursor(Qt.PointingHandCursor)
        new_piece_btn.setStyleSheet(BUTTON_STYLE)
        new_piece_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.create_piece_page))
        layout.addWidget(new_piece_btn)

        # NEW: Place Existing Pieces button (go to new page)
        place_existing_btn = QPushButton("🧩 PLACE EXISTING PIECES")
        place_existing_btn.setMinimumHeight(50)
        place_existing_btn.setCursor(Qt.PointingHandCursor)
        place_existing_btn.setStyleSheet(BUTTON_STYLE)
        place_existing_btn.clicked.connect(self.open_place_existing_page)
        layout.addWidget(place_existing_btn)

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
        self.board_widget = QWidget()
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(0)
        self.board_layout.setContentsMargins(0,0,0,0)
        self.board_widget.setLayout(self.board_layout)
        layout.addWidget(self.board_widget)
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

    # ---------------- Solve (original single-type exact-K solver) ----------------
    def solve(self):
        self.clear_board()
        try:
            piece_text = self.piece_combo.currentText()
            piece = piece_text.split()[0]     # name before symbol
            n = int(self.n_input.text())
            k = int(self.k_input.text())
        except:
            QMessageBox.warning(self, "Input Error", "Enter valid numbers.")
            return
        default_symbols = {"Queen":"♛","Rook":"♜","Bishop":"♝","Knight":"♞"}
        symbol = default_symbols.get(piece, "⭐")
        if piece == "Queen" and k > n:
            QMessageBox.warning(self, "Impossible", f"Max {n} Queens on {n}x{n} board!")
            return
        if piece == "Knight" and k > (n*n + 1)//2:
            QMessageBox.warning(self, "Impossible", f"Max {(n*n + 1)//2} Knights on {n}x{n} board!")
            return
        model = Model("K_Pieces")
        model.setParam("OutputFlag", 0)
        x = {}
        for r in range(1, n+1):
            for c in range(1, n+1):
                x[(r, c)] = model.addVar(vtype=GRB.BINARY)
        # Custom pieces
        if piece in self.custom_pieces:
            moves = self.custom_pieces[piece]['offsets']
            specials = self.custom_pieces[piece]['special']
            for r in range(1, n+1):
                for c in range(1, n+1):
                    # finite offsets
                    for dr, dc in moves:
                        rr = r + dr
                        cc = c + dc
                        if 1 <= rr <= n and 1 <= cc <= n:
                            model.addConstr(x[(r, c)] + x[(rr, cc)] <= 1)
                    # specials (row/col/diag) - treat like rook/bishop
                    if 'row' in specials:
                        model.addConstr(sum(x[(r, cc)] for cc in range(1, n+1)) <= 1)
                    if 'col' in specials:
                        model.addConstr(sum(x[(rr, c)] for rr in range(1, n+1)) <= 1)
                    if 'diag' in specials:
                        for b in range(-(n-1), n):
                            model.addConstr(sum(x[(rr, cc)] for rr in range(1, n+1)
                                                    for cc in range(1, n+1)
                                                    if rr-cc == b) <= 1)
                        for b in range(2, 2*n):
                            model.addConstr(sum(x[(rr, cc)] for rr in range(1, n+1)
                                                    for cc in range(1, n+1)
                                                    if rr+cc == b) <= 1)
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
        grid = [[0]*n for _ in range(n)]
        for (r, c), var in x.items():
            if var.X > 0.5:
                grid[r-1][c-1] = 1
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

    # ---------------- Helper: attack generation for a piece type ----------------
    def get_attack_cells_for_piece(self, piece_name, r, c, n):
        """
        Return set of cells (rr,cc) that a piece of type piece_name placed at (r,c) would attack.
        r,c are 1-based indices.
        """
        attacked = set()
        base_name = piece_name.replace(" ⭐", "")

        # Build a set of occupied cells to stop sliding
        occupied = set(self.existing_placements.keys())  # {(r,c)}

        # Knight jumps
        if base_name == "Knight" or base_name == "Knight ♞":
            moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
            for dr, dc in moves:
                rr, cc = r+dr, c+dc
                if 1 <= rr <= n and 1 <= cc <= n:
                    attacked.add((rr, cc))
            return attacked

        # Custom pieces or sliding pieces
        offsets = []
        specials = []
        if base_name in self.custom_pieces:
            info = self.custom_pieces[base_name]
            offsets = info.get('offsets', [])
            specials = info.get('special', [])

        # 1. finite offsets for custom pieces
        for dr, dc in offsets:
            rr, cc = r+dr, c+dc
            if 1 <= rr <= n and 1 <= cc <= n:
                attacked.add((rr, cc))

        # 2. sliding special directions for custom pieces
        directions = []
        if 'row' in specials:
            for rr in range(1, n+1):
                for cc in range(1, n+1):
                    if rr == r:
                        attacked.add((rr, cc))
        if 'col' in specials:
            for cc in range(1, n+1):
                for rr in range(1, n+1):
                    if cc == c:
                        attacked.add((rr, cc))
        if 'diag' in specials:
            directb=r-c
            for rr in range(1,n+1):
                cc = rr - directb
                if 1 <= cc <= n:
                    attacked.add((rr, cc))
            counterb=r+c
            for rr in range(1, n+1):
                cc = counterb - rr
                if 1 <= cc <= n:
                    attacked.add((rr, cc))

       

        # 3. standard chess pieces
        if base_name in ["Rook", "Queen","Queen ♛","Rook ♜"]:
            for rr in range(1, n+1):
                for cc in range(1, n+1):
                    if rr == r:
                        attacked.add((rr, cc))
            for cc in range(1, n+1):
                for rr in range(1, n+1):
                    if cc == c:
                        attacked.add((rr, cc))
        if base_name in ["Bishop", "Queen","Queen ♛","Bishop ♝"]:
            directb=r-c
            for rr in range(1,n+1):
                cc = rr - directb
                if 1 <= cc <= n:
                    attacked.add((rr, cc))
            counterb=r+c
            for rr in range(1, n+1):
                cc = counterb - rr
                if 1 <= cc <= n:
                    attacked.add((rr, cc))

        return attacked


    # ---------------- Helper: check if a cell attack another cell for their types ----------------
    def cell_attacks_cell(self, piece_name, r1, c1, r2, c2, n):
        """Return True if piece type piece_name at (r1,c1) would attack (r2,c2)."""
        return ((r2, c2) in self.get_attack_cells_for_piece(piece_name, r1, c1, n) and (r1,c1) in self.get_attack_cells_for_piece(piece_name, r2, c2, n))
    # ---------------- New Page: Place Existing Pieces ----------------
    def create_place_existing_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(12)
        page.setStyleSheet("background-color:#1E1E1E;")

        title = QLabel("🧩 Place Existing Pieces (manual)")
        title.setStyleSheet("font-size:28px;color:white;font-weight:bold;")
        layout.addWidget(title)

        # Controls row: choose board size, choose piece to place, clear, maximize
        controls = QHBoxLayout()
        size_label = QLabel("Board N:")
        size_label.setStyleSheet("color:white;font-weight:bold;")
        controls.addWidget(size_label)
        self.place_n_input = QLineEdit()
        self.place_n_input.setFixedWidth(70)
        self.place_n_input.setPlaceholderText(str(self.board_size))
        self.place_n_input.setStyleSheet(INPUT_STYLE)
        controls.addWidget(self.place_n_input)

        type_label = QLabel("Piece to place:")
        type_label.setStyleSheet("color:white;font-weight:bold;")
        controls.addWidget(type_label)
        self.place_piece_type_combo = QComboBox()
        self.place_piece_type_combo.setStyleSheet(COMBO_STYLE)
        # fill default pieces + custom (refresh function will keep it updated)
        self.refresh_place_existing_page()
        controls.addWidget(self.place_piece_type_combo)

        clear_btn = QPushButton("Clear All Placements")
        clear_btn.setStyleSheet(BUTTON_STYLE)
        clear_btn.clicked.connect(self.clear_existing_placements)
        controls.addWidget(clear_btn)
        layout.addLayout(controls)

        # board area (we create dynamically when user clicks "Create board")
        self.place_board_widget = QWidget()
        self.place_board_layout = QGridLayout(self.place_board_widget)
        self.place_board_layout.setSpacing(0)
        self.place_board_layout.setContentsMargins(0,0,0,0)
        self.place_board_cells = {}
        layout.addWidget(self.place_board_widget)

        # Buttons row
        buttons_row = QHBoxLayout()
        create_board_btn = QPushButton("Create Board")
        create_board_btn.setStyleSheet(BUTTON_STYLE)
        create_board_btn.clicked.connect(self.build_place_board)
        buttons_row.addWidget(create_board_btn)

        maximize_btn = QPushButton("🔍 Maximize X (add as many X as possible)")
        maximize_btn.setStyleSheet(BUTTON_STYLE)
        maximize_btn.clicked.connect(self.solve_maximize_X)
        buttons_row.addWidget(maximize_btn)

        back_btn = QPushButton("⬅ BACK")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        buttons_row.addWidget(back_btn)

        layout.addLayout(buttons_row)
        return page

    def refresh_place_existing_page(self):
        """Reload custom pieces inside the placement combo."""
        # ensure combo exists
        try:
            combo = self.place_piece_type_combo
        except AttributeError:
            return
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(["Queen ♛", "Rook ♜", "Bishop ♝", "Knight ♞"])
        for name in self.custom_pieces.keys():
            combo.addItem(f"{name} ⭐")
        combo.blockSignals(False)

    def open_place_existing_page(self):
        # prefill with n if the user already set it
        try:
            self.place_n_input.setText(self.n_input.text())
        except:
            pass
        # refresh pieces
        self.refresh_place_existing_page()
        # clear previous placements
        self.clear_existing_placements()
        self.stacked.setCurrentWidget(self.place_existing_page)

    def clear_existing_placements(self):
        # Reset the existing placements mapping and reset all board buttons
        self.existing_placements = {}
        for cell_dict in self.place_board_cells.values():
            btn = cell_dict.get("btn")
            if btn:
                btn.setText("")
                btn.setProperty("placed_piece", "")
                base_style = cell_dict.get("base_style", "")
                if base_style:
                    btn.setStyleSheet(base_style)
                else:
                    # fallback to base_color if base_style isn't set
                    base_color = cell_dict.get("base_color", "#EEEED2")
                    btn.setStyleSheet(f"background-color:{base_color};border:0;margin:0;padding:0;")

    #        ----------- Build Place Board ----------------
    def build_place_board(self):
        # Completely rebuild the board widget and layout
        if hasattr(self, "custom_board_widget"):
            self.custom_board_widget.deleteLater()

        self.custom_board_widget = QWidget()
        self.custom_board_layout = QGridLayout(self.custom_board_widget)

        self.custom_board_layout.setSpacing(0)
        self.custom_board_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_board_layout.setAlignment(Qt.AlignCenter)

        # Attach widget to the page
        self.place_board_layout.addWidget(self.custom_board_widget)
        
        self.place_board_cells = {}
        n = int(self.place_n_input.text()) if self.place_n_input.text().isdigit() else self.board_size

        # Resize widget to the exact board size
        self.custom_board_widget.setFixedSize(n * 50, n * 50)

        for r in range(n):
            for c in range(n):
                btn = QPushButton()
                btn.setFixedSize(30, 30)
                btn.setCheckable(True)

                base_color = "#EEEED2" if (r + c) % 2 == 0 else "#769656"
                btn.setStyleSheet(
                    f"background-color:{base_color};"
                    "border:0;margin:0;padding:0;"
                )

                btn.clicked.connect(partial(self.toggle_place_existing, r, c))

                self.place_board_cells[(r, c)] = {
                    "btn": btn,
                    "base_color": base_color,
                    "occupied": False
                }

                btn.setProperty("placed_piece", "")

                # IMPORTANT — add to the correct board layout
                self.custom_board_layout.addWidget(btn, r, c)

        self.last_place_n = n





    # ---------------- Toggle Place Existing ----------------
    def toggle_place_existing(self, r0, c0):

        """
        r0, c0 are 0-based UI coordinates. Clicking cycles: empty -> place current selected piece -> remove.
        We store placements with 1-based indices in self.existing_placements to match solver helpers.
        """
        # make sure board was created
        cell = self.place_board_cells.get((r0, c0))
        if cell is None:
            return

        btn = cell["btn"]

        # require a valid N
        try:
            n = int(self.place_n_input.text())
        except:
            QMessageBox.warning(self, "Input Error", "Create the board first with a valid N.")
            return

        current_type_label = self.place_piece_type_combo.currentText()
        if not current_type_label:
            return

        piece_name = current_type_label.split()[0]  # normalized name (e.g., "Queen" or custom)
        placed = btn.property("placed_piece") or ""

        # convert to 1-based for storage in existing_placements
        r = r0 + 1
        c = c0 + 1

        if placed == "":
            # place the selected piece here
            normalized = current_type_label.replace(self.piece_map[piece_name], "")
            symbol = self.get_piece_display_symbol(normalized)
            btn.setText(self.piece_map[piece_name] if piece_name in self.piece_map else symbol)
            btn.setProperty("placed_piece", normalized)
            btn.setStyleSheet("background-color:#1E90FF;color:white;font-size:20px;border:2px solid #FFD700;padding:0;margin:0;")
            # store as 1-based to be compatible with other helpers
            self.existing_placements[(r, c)] = normalized
        else:
            # remove placement
            btn.setText("")
            btn.setProperty("placed_piece", "")
            # restore style from stored base style in cell dict
            base_style = cell.get("base_style")
            if base_style:
                btn.setStyleSheet(base_style)
            else:
                base_color = cell.get("base_color", "#EEEED2")
                btn.setStyleSheet(f"background-color:{base_color};border:0;margin:0;padding:0;")
            # remove from existing_placements (remember stored 1-based keys)
            if (r, c) in self.existing_placements:
                del self.existing_placements[(r, c)]


    # ---------------- Helper: get display symbol ----------------
    def get_piece_display_symbol(self, piece_name):
        """Return display symbol for a piece name (supports custom)."""
        if piece_name == "Queen":
            return "♛"
        if piece_name == "Rook":
            return "♜"
        if piece_name == "Bishop":
            return "♝"
        if piece_name == "Knight":
            return "♞"
        # custom piece -> first letter (uppercase)
        if piece_name:
            return piece_name[0].upper()
        return "?"

    # ---------------- Solve maximize X (fixed with existing conflict check) ----------------
    def solve_maximize_X(self):
        # Get board size
        try:
            n = int(self.place_n_input.text())
            if n <= 0:
                raise ValueError()
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid board size N and create the board.")
            return
        if not hasattr(self, "place_board_cells") or not self.place_board_cells:
            QMessageBox.warning(self, "Board Error", "Create the board first.")
            return

        # Check for conflicts among already placed pieces
        conflicts = []
        items = list(self.existing_placements.items())
        for i in range(len(items)):
            (r1, c1), piece1 = items[i]
            for j in range(i+1, len(items)):
                (r2, c2), piece2 = items[j]
                print(f"Checking conflict between {piece1} at ({r1},{c1}) and {piece2} at ({r2},{c2})")
                print("piece1:", piece1)
                print("piece2:", piece2)
                print("Attack result:",
                self.cell_attacks_cell(piece1, r1, c1, r2, c2, n))
                print(self.cell_attacks_cell(piece2, r2, c2, r1, c1, n))
                if self.cell_attacks_cell(piece1, r1, c1, r2, c2, n) or \
                self.cell_attacks_cell(piece2, r2, c2, r1, c1, n):
                    conflicts.append(((r1,c1,piece1),(r2,c2,piece2)))

        if conflicts:
            msg = "⚠ The following existing pieces are attacking each other:\n"
            for (r1,c1,p1),(r2,c2,p2) in conflicts:
                msg += f" - {p1} at ({r1},{c1}) attacks {p2} at ({r2},{c2})\n"
            QMessageBox.warning(self, "Existing Piece Conflict", msg)
            return

        # Pick the piece type X
        type_label = self.place_piece_type_combo.currentText()
        piece_X = type_label.split()[0]
        default_symbols = {"Queen":"♛","Rook":"♜","Bishop":"♝","Knight":"♞"}
        X_symbol =self.piece_map[piece_X] if piece_X in self.piece_map else default_symbols.get(piece_X, piece_X[0].upper())

        # Initialize Gurobi model
        model = Model("Maximize_X")
        model.setParam("OutputFlag", 0)

        # Create binary variables only for empty cells
        y = {}
        for r in range(1, n+1):
            for c in range(1, n+1):
                if (r,c) in self.existing_placements:
                    continue
                y[(r,c)] = model.addVar(vtype=GRB.BINARY)

        # Step 1: forbid placement if new X attacks existing piece or is attacked
        for (r,c), var in y.items():
            for (re, ce), existing_piece in self.existing_placements.items():
                if self.cell_attacks_cell(piece_X, r, c, re, ce, n) or \
                self.cell_attacks_cell(existing_piece, re, ce, r, c, n):
                    model.addConstr(var == 0)

        # Step 2: forbid X pieces from attacking each other
        cells = list(y.keys())
        for i in range(len(cells)):
            r1, c1 = cells[i]
            attacked_by_r1 = self.get_attack_cells_for_piece(piece_X, r1, c1, n)
            for j in range(i+1, len(cells)):
                r2, c2 = cells[j]
                if (r2, c2) in attacked_by_r1:
                    model.addConstr(y[(r1, c1)] + y[(r2, c2)] <= 1)

        # Objective: maximize the number of X pieces added
        if y:
            model.setObjective(sum(y.values()), GRB.MAXIMIZE)
        else:
            model.setObjective(0, GRB.MAXIMIZE)

        model.optimize()

        if model.status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
            QMessageBox.warning(self, "No Solution", "Gurobi couldn't solve the maximization.")
            return

        # Extract solution
        added = []
        for (r,c), var in y.items():
            if var.X is not None and var.X > 0.5:
                added.append((r,c))

        # Display board with existing and new pieces
        self.clear_board()
        cell_size = min(500//n, 60)
        for r in range(1, n+1):
            for c in range(1, n+1):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(cell_size, cell_size)
                color = "#3A3A3A" if (r+c) % 2 == 0 else "#2C2C2C"
                if (r,c) in self.existing_placements:
                    p = self.existing_placements[(r,c)]
                    symbol = default_symbols.get(p, self.piece_map[p] if p in self.piece_map else p[0].upper())
                    cell.setText(symbol)
                    cell.setStyleSheet(
                        f"background-color:#1E90FF;color:white;"
                        f"font-size:{cell_size//2}px;font-weight:bold;"
                        f"border:2px solid #FFD700;"
                    )
                elif (r,c) in added:
                    cell.setText(X_symbol)
                    cell.setStyleSheet(
                        f"background-color:#00AA00;color:white;"
                        f"font-size:{cell_size//2}px;font-weight:bold;"
                        f"border:2px solid #222222;"
                    )
                else:
                    cell.setStyleSheet(f"background-color:{color};border:1px solid #555555;")
                self.board_layout.addWidget(cell, r-1, c-1)

        QMessageBox.information(self, "Result", f"Added {len(added)} {piece_X}(s) to the board.")
        self.stacked.setCurrentWidget(self.board_page)

