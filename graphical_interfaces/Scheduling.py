from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from gurobipy import Model, GRB
import csv
from io import StringIO

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

TEXT_EDIT_STYLE = """
QPlainTextEdit {
    padding: 8px;
    border: 2px solid #555555;
    border-radius: 6px;
    font-size: 14px;
    background-color: #2C2C2C;
    color: #FFFFFF;
    font-family: 'Courier New';
}
QPlainTextEdit:focus {
    border: 2px solid #1E90FF;
    background-color: #3A3A3A;
}
"""

LABEL_STYLE = """
font-size: 24px;
font-weight: bold;
color: #FFFFFF;
"""

example_data = """UNIX,GL2,Mr. Jemai
WEB,GL2,Mr. Aymen
WEB(advanced),GL3,Mr. Aymen
Recherche Op,GL3,Mrs. Imen
SE,GL2,Mrs. Imen"""

# ----------------------------
# Main GUI
# ----------------------------
class SchedulingSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Coloring - Scheduling Solver")
        self.setGeometry(50, 50, 1000, 700)
        self.setStyleSheet("background-color: #121212;")
        
        # Create a container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Create stacked widget for pages
        self.stacked = QStackedWidget()
        container_layout.addWidget(self.stacked)
        
        self.setCentralWidget(container)
        
        # Pages
        self.menu_page = self.create_menu_page()
        self.input_page = self.create_input_page()
        self.result_page = self.create_result_page()
        self.manual_page = self.create_manual_page()
        
        self.stacked.addWidget(self.menu_page)
        self.stacked.addWidget(self.input_page)
        self.stacked.addWidget(self.result_page)
        self.stacked.addWidget(self.manual_page)
        
        # State
        self.graph = {}  # vertex -> set of adjacent vertices
        self.coloring = {}  # vertex -> color
        self.num_colors = 0

    # ============== Menu Page ==============
    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        title = QLabel("GRAPH COLORING - SCHEDULING SOLVER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:32px;font-weight:bold;color:#FFFFFF;")
        
        subtitle = QLabel("Assign exams to time slots without conflicts")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size:18px;color:#CCCCCC;")
        
        start_btn = QPushButton("START SOLVER")
        start_btn.setStyleSheet(BUTTON_STYLE)
        start_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        
        manual_btn = QPushButton("📘 MANUAL")
        manual_btn.setStyleSheet(BUTTON_STYLE)
        manual_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.manual_page))
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(start_btn)
        layout.addWidget(manual_btn)
        return page

    # ============== Input Page ==============
    def create_input_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Exam Scheduling Configuration")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:28px;font-weight:bold;color:#FFFFFF;")
        layout.addWidget(title)
        
        subtitle = QLabel("Enter exam data (name, filière, teacher) to auto-generate conflicts")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size:14px;color:#CCCCCC;")
        layout.addWidget(subtitle)
        
        # Exam data
        exams_label = QLabel("Exam Data (one per line: 'ExamName,Filière,Teacher'):")
        exams_label.setStyleSheet("font-size:16px;color:#FFFFFF;font-weight:bold;")
        layout.addWidget(exams_label)
        
        self.exams_input = QPlainTextEdit()
        self.exams_input.setStyleSheet(TEXT_EDIT_STYLE)
        self.exams_input.setPlaceholderText("Example:\n" + example_data)
        self.exams_input.setFixedHeight(120)
        layout.addWidget(self.exams_input)
        
        # Example button
        example_btn = QPushButton("📋 Load Example")
        example_btn.setStyleSheet(BUTTON_STYLE)
        example_btn.clicked.connect(self.load_example)
        layout.addWidget(example_btn)
        
        # Solve button
        solve_btn = QPushButton("🚀 SOLVE")
        solve_btn.setStyleSheet(BUTTON_STYLE)
        solve_btn.setFixedHeight(50)
        solve_btn.clicked.connect(self.solve)
        layout.addWidget(solve_btn)
        
        # Back button
        back_btn = QPushButton("⬅ BACK TO MENU")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.menu_page))
        layout.addWidget(back_btn)
        
        layout.addStretch()
        return page

    # ============== Result Page ==============
    def create_result_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        title = QLabel("SCHEDULING SOLUTION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:28px;font-weight:bold;color:#FFFFFF;")
        layout.addWidget(title)
        
        # Stats
        stats_layout = QHBoxLayout()
        
        self.num_colors_label = QLabel("Colors Used: -")
        self.num_colors_label.setStyleSheet("font-size:20px;color:#1E90FF;font-weight:bold;")
        stats_layout.addWidget(self.num_colors_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Result display
        self.result_display = QPlainTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet(TEXT_EDIT_STYLE)
        layout.addWidget(self.result_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        try_again_btn = QPushButton("🔄 TRY AGAIN")
        try_again_btn.setStyleSheet(BUTTON_STYLE)
        try_again_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.input_page))
        button_layout.addWidget(try_again_btn)
        
        back_btn = QPushButton("⬅ BACK TO MENU")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.menu_page))
        button_layout.addWidget(back_btn)
        
        layout.addLayout(button_layout)
        return page

    # ============== Manual Page ==============
    def create_manual_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #1E1E1E;")
        
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        scroll_layout.setContentsMargins(30, 20, 30, 20)
        scroll_layout.setSpacing(25)
        
        title = QLabel("📖 GRAPH COLORING - SCHEDULING MANUAL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #FFFFFF;")
        scroll_layout.addWidget(title)
        
        instructions = QLabel("""
        Welcome to the Exam Scheduling Solver!

        🎯 PROBLEM OVERVIEW:
        Automatically assign exams to the minimum number of time slots so that:
        - No two exams from the same filière (class) are at the same time
        - No two exams taught by the same teacher are at the same time

        📝 HOW TO USE:

        1️⃣ Enter EXAM DATA (one exam per line)
        Format: ExamName,Filière,Teacher
        
        Examples:
            Math101,CS1,Prof. Smith
            Physics101,CS1,Prof. Jones
            Chemistry101,CS2,Prof. Smith
            Biology101,CS2,Prof. Brown
            Economics101,CS1,Prof. Adams

        2️⃣ Click 📋 LOAD EXAMPLE to see a sample schedule

        3️⃣ Click 🚀 SOLVE to find the optimal schedule
        
        4️⃣ View the SOLUTION:
        - Minimum number of TIME SLOTS needed
        - Which exams are in each time slot
        - Details: Exam name, assigned slot, filière, and teacher

        🔄 AUTOMATIC CONFLICT GENERATION:
        The solver automatically detects conflicts:
        - Same filière → exams conflict (same students might take both)
        - Same teacher → exams conflict (teacher can't teach two at once)
        
        Example: Math101 (CS1, Prof. Smith) conflicts with:
            - Physics101 (CS1, Prof. Jones) - same filière
            - Chemistry101 (CS2, Prof. Smith) - same teacher

        💡 TECHNICAL DETAILS:
        This solver uses Mixed Integer Programming (MIP) with Gurobi to:
        - Minimize the number of time slots
        - Respect all conflict constraints
        - Guarantee an optimal solution
        """)
        instructions.setStyleSheet("font-size: 18px; color: #FFFFFF;")
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
    font-size: 18px;
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

    # ============== Helper Methods ==============
    def load_example(self):
        self.exams_input.setPlainText(example_data)

    def parse_exams_data(self):
        """Parse exam data and auto-generate conflicts"""
        data_text = self.exams_input.toPlainText().strip()
        
        if not data_text:
            QMessageBox.warning(self, "Input Error", "Please enter exam data.")
            return None, None, None
        
        exams = []
        lines = data_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 3:
                QMessageBox.warning(self, "Input Error", 
                    f"Invalid format: '{line}'\nUse: ExamName,Filière,Teacher")
                return None, None, None
            exam_name, filiere, teacher = parts
            exams.append({
                'name': exam_name,
                'filiere': filiere,
                'teacher': teacher
            })
        
        if not exams:
            QMessageBox.warning(self, "Input Error", "No exams found.")
            return None, None, None
        
        # Auto-generate conflicts
        edges = []
        for i in range(len(exams)):
            for j in range(i+1, len(exams)):
                # Conflict if same filière OR same teacher
                if exams[i]['filiere'] == exams[j]['filiere'] or \
                   exams[i]['teacher'] == exams[j]['teacher']:
                    edges.append((i, j))
        
        return exams, edges, len(exams)

    def solve(self):
        exams, edges, num_vertices = self.parse_exams_data()
        if exams is None:
            return
        
        # Store for later display
        self.exams = exams
        
        # Build adjacency
        self.graph = {i: set() for i in range(num_vertices)}
        for u, v in edges:
            self.graph[u].add(v)
            self.graph[v].add(u)
        
        # Solve MIP
        solution = self.solve_graph_coloring(num_vertices)
        
        if solution is None:
            QMessageBox.warning(self, "Error", "Failed to solve the problem.")
            return
        
        self.coloring, self.num_colors = solution
        self.display_result()
        self.stacked.setCurrentWidget(self.result_page)

    def solve_graph_coloring(self, num_vertices):
        """Solve graph coloring using Gurobi MIP"""
        
        # Upper bound on colors (greedy approximation)
        max_colors = max([len(self.graph[v]) for v in self.graph]) + 1
        max_colors = max(max_colors, 2)
        
        model = Model("GraphColoring")
        model.setParam("OutputFlag", 0)
        
        # Variables:
        # x[v][c] = 1 if vertex v gets color c
        x = {}
        for v in range(num_vertices):
            for c in range(max_colors):
                x[(v, c)] = model.addVar(vtype=GRB.BINARY, name=f"x_{v}_{c}")
        
        # y[c] = 1 if color c is used
        y = {}
        for c in range(max_colors):
            y[c] = model.addVar(vtype=GRB.BINARY, name=f"y_{c}")
        
        # Constraints:
        # 1. Each vertex gets exactly one color
        for v in range(num_vertices):
            model.addConstr(
                sum(x[(v, c)] for c in range(max_colors)) == 1,
                name=f"vertex_color_{v}"
            )
        
        # 2. Adjacent vertices must have different colors
        for u in self.graph:
            for v in self.graph[u]:
                if u < v:  # Avoid duplicate constraints
                    for c in range(max_colors):
                        model.addConstr(
                            x[(u, c)] + x[(v, c)] <= 1,
                            name=f"adjacent_{u}_{v}_{c}"
                        )
        
        # 3. y[c] = 1 if any vertex uses color c
        for c in range(max_colors):
            for v in range(num_vertices):
                model.addConstr(
                    y[c] >= x[(v, c)],
                    name=f"use_color_{c}_{v}"
                )
        
        # Objective: minimize number of colors
        model.setObjective(sum(y[c] for c in range(max_colors)), GRB.MINIMIZE)
        model.optimize()
        
        if model.status != GRB.OPTIMAL:
            return None
        
        # Extract solution
        coloring = {}
        for v in range(num_vertices):
            for c in range(max_colors):
                if x[(v, c)].X > 0.5:
                    coloring[v] = c
                    break
        
        num_colors_used = int(sum(y[c].X for c in range(max_colors)))
        
        # Renumber colors to be consecutive (0, 1, 2, ..., num_colors_used-1)
        # This ensures no gaps in slot numbering
        used_colors = sorted(set(coloring.values()))
        color_mapping = {old_color: new_color for new_color, old_color in enumerate(used_colors)}
        coloring = {v: color_mapping[c] for v, c in coloring.items()}
        
        return coloring, num_colors_used

    def display_result(self):
        """Display coloring solution with exam details"""
        
        self.num_colors_label.setText(f"Time Slots Required: {self.num_colors}")
        
        # Group exams by time slot
        slot_groups = {}
        for exam_idx, slot in sorted(self.coloring.items()):
            if slot not in slot_groups:
                slot_groups[slot] = []
            slot_groups[slot].append(exam_idx)
        
        # Build result text
        result_text = "OPTIMAL EXAM SCHEDULING SOLUTION\n"
        result_text += "=" * 60 + "\n\n"
        
        for slot in sorted(slot_groups.keys()):
            exam_indices = slot_groups[slot]
            exam_names = [self.exams[idx]['name'] for idx in exam_indices]
            result_text += f"Time Slot {slot + 1}:\n"
            for name in exam_names:
                result_text += f"  • {name}\n"
            result_text += "\n"
        
        result_text += "=" * 60 + "\n"
        result_text += f"Minimum Time Slots Required: {self.num_colors}\n"
        result_text += f"Total Exams: {len(self.exams)}\n"
        
        # Add exam details
        result_text += "\nEXAM DETAILS:\n"
        result_text += "-" * 60 + "\n"
        for idx, exam in enumerate(self.exams):
            slot = self.coloring[idx]
            result_text += f"{exam['name']:20} | Slot: {slot + 1} | {exam['filiere']:10} | {exam['teacher']}\n"
        
        self.result_display.setPlainText(result_text)


# ============== Main Entry Point ==============
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    solver = SchedulingSolverGUI()
    solver.show()
    sys.exit(app.exec())
