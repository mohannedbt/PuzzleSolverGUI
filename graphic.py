from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from gurobipy import Model, GRB
from random import randint as rand
import sys

class SudokuGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Sudoku Generator")
        self.setGeometry(100, 100, 700, 750)
        
        # Set modern color palette
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #ffffff;
                background: white;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f093fb, stop:1 #f5576c);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffecd2, stop:1 #fcb69f);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff9a9e, stop:1 #fecfef);
            }
            QTableWidget {
                background: white;
                border: none;
                border-radius: 15px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
            QHeaderView::section {
                background: transparent;
                border: none;
            }
        """)
        
        # Create central widget with layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QtWidgets.QLabel("🎯 Sudoku Puzzle Generator")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        """)
        main_layout.addWidget(title)
        
        # Control panel
        control_panel = QtWidgets.QWidget()
        control_panel.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        control_layout = QtWidgets.QHBoxLayout(control_panel)
        control_layout.setSpacing(20)
        
        # Size input group
        size_group = QtWidgets.QVBoxLayout()
        self.size_label = QtWidgets.QLabel("Grid Size (n × n)")
        self.size_input = QtWidgets.QLineEdit()
        self.size_input.setPlaceholderText("e.g., 9")
        self.size_input.setMaximumWidth(100)
        size_group.addWidget(self.size_label)
        size_group.addWidget(self.size_input)
        control_layout.addLayout(size_group)
        
        # Remove cells input group
        remove_group = QtWidgets.QVBoxLayout()
        self.remove_label = QtWidgets.QLabel("Cells to Remove")
        self.remove_input = QtWidgets.QLineEdit()
        self.remove_input.setPlaceholderText("e.g., 40")
        self.remove_input.setMaximumWidth(100)
        remove_group.addWidget(self.remove_label)
        remove_group.addWidget(self.remove_input)
        control_layout.addLayout(remove_group)
        
        control_layout.addStretch()
        
        # Generate button
        self.generate_btn = QtWidgets.QPushButton("🎲 Generate Puzzle")
        self.generate_btn.setMinimumWidth(180)
        self.generate_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.generate_btn.clicked.connect(self.generate_sudoku)
        control_layout.addWidget(self.generate_btn)
        
        main_layout.addWidget(control_panel)
        
        # Table container
        table_container = QtWidgets.QWidget()
        table_container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        table_layout = QtWidgets.QVBoxLayout(table_container)
        table_layout.setContentsMargins(10, 10, 10, 10)
        
        # Table for displaying Sudoku
        self.table = QtWidgets.QTableWidget()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        table_layout.addWidget(self.table)
        
        main_layout.addWidget(table_container)
        
    def generate_sudoku(self):
        try:
            n = int(self.size_input.text())
        except ValueError:
            self.show_message("⚠️ Invalid Input", "Please enter a valid number for grid size")
            return
        
        if n < 1:
            self.show_message("⚠️ Invalid Size", "Grid size must be at least 1")
            return
        
        try:
            eliminate = int(self.remove_input.text())
        except ValueError:
            eliminate = 0
        
        if eliminate >= n*n:
            self.show_message("⚠️ Too Many Cells", f"Cells to remove must be less than {n*n}")
            return
        
        # Show loading state
        self.generate_btn.setText("⏳ Generating...")
        self.generate_btn.setEnabled(False)
        QApplication.processEvents()
        
        # --- Build Gurobi model ---
        model = Model("Sudoku")
        model.setParam('OutputFlag', 0)
        
        x = {}
        for r in range(1, n+1):
            for c in range(1, n+1):
                for d in range(1, n+1):
                    x[(r,c,d)] = model.addVar(vtype=GRB.BINARY, name=f"x_{r}_{c}_{d}")
        
        for r in range(1,n+1):
            for c in range(1,n+1):
                model.addConstr(sum(x[(r,c,d)] for d in range(1,n+1)) == 1)
        
        for r in range(1,n+1):
            for d in range(1,n+1):
                model.addConstr(sum(x[(r,c,d)] for c in range(1,n+1)) == 1)
        
        for c in range(1,n+1):
            for d in range(1,n+1):
                model.addConstr(sum(x[(r,c,d)] for r in range(1,n+1)) == 1)
        
        model.setObjective(0, GRB.MINIMIZE)
        model.optimize()
        
        if model.status != GRB.OPTIMAL:
            self.show_message("❌ Error", "No solution found for this configuration")
            self.generate_btn.setText("🎲 Generate Puzzle")
            self.generate_btn.setEnabled(True)
            return
        
        # --- Extract solution ---
        grid = [[0]*n for _ in range(n)]
        for (r,c,d), var in x.items():
            if var.X > 0.5:
                grid[r-1][c-1] = d
        
        # --- Eliminate cells ---
        list_eliminate = []
        while len(list_eliminate) < eliminate:
            i, j = rand(0, n-1), rand(0, n-1)
            if (i, j) not in list_eliminate:
                list_eliminate.append((i, j))
                grid[i][j] = ""
        
        # --- Display in table ---
        self.table.setRowCount(n)
        self.table.setColumnCount(n)
        
        # Calculate cell size
        cell_size = min(500 // n, 60)
        
        for i in range(n):
            self.table.setRowHeight(i, cell_size)
            self.table.setColumnWidth(i, cell_size)
            for j in range(n):
                item = QTableWidgetItem(str(grid[i][j]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                
                # Color filled cells differently
                if grid[i][j] != "":
                    item.setBackground(QtGui.QColor("#667eea"))
                    item.setForeground(QtGui.QColor("white"))
                    font = item.font()
                    font.setBold(True)
                    font.setPointSize(max(10, 24 - n))
                    item.setFont(font)
                else:
                    item.setBackground(QtGui.QColor("#f8f9fa"))
                    item.setForeground(QtGui.QColor("#adb5bd"))
                
                self.table.setItem(i, j, item)
        
        # Reset button
        self.generate_btn.setText("🎲 Generate Puzzle")
        self.generate_btn.setEnabled(True)
    
    def show_message(self, title, message):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QPushButton {
                min-width: 80px;
            }
        """)
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SudokuGUI()
    window.show()
    sys.exit(app.exec())