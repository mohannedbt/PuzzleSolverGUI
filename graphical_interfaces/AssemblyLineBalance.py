from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from non_interfaces.AssemblyLineBalance import (
    balance_line, parse_task_input, display_solution
)

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

example_data = """task paint max 10 avg 7
task hammer max 30 avg 27
task assemble max 50 avg 40
task inspect max 15 avg 12

max_cycle 60"""

# Helper function for efficiency color
def get_efficiency_color(efficiency):
    """Return color based on efficiency percentage"""
    if efficiency >= 85:
        return "#2cb67d"  # Green
    elif efficiency >= 70:
        return "#ffc107"  # Yellow
    elif efficiency >= 50:
        return "#ff9800"  # Orange
    else:
        return "#ff6b6b"  # Red


# ----------------------------
# Main GUI
# ----------------------------
class AssemblyLineBalanceSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assembly Line Balancing - Solver")
        self.setGeometry(50, 50, 1200, 800)
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
        self.solution = None
        self.tasks = []
        self.t_max = []
        self.t_avg = []

    # ============== Menu Page ==============
    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        title = QLabel("ASSEMBLY LINE BALANCING")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:32px;font-weight:bold;color:#FFFFFF;")
        
        subtitle = QLabel("Minimize workstations while respecting cycle time constraints")
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
        
        title = QLabel("Assembly Line Configuration")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:28px;font-weight:bold;color:#FFFFFF;")
        layout.addWidget(title)
        
        subtitle = QLabel("Define tasks with durations and maximum cycle time")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size:14px;color:#CCCCCC;")
        layout.addWidget(subtitle)
        
        # Task input
        tasks_label = QLabel("Task Configuration (one per line: 'task <name> max <max_time> avg <avg_time>'):")
        tasks_label.setStyleSheet("font-size:16px;color:#FFFFFF;font-weight:bold;")
        layout.addWidget(tasks_label)
        
        self.tasks_input = QPlainTextEdit()
        self.tasks_input.setStyleSheet(INPUT_STYLE)
        self.tasks_input.setPlaceholderText("Example:\n" + example_data)
        self.tasks_input.setFixedHeight(150)
        layout.addWidget(self.tasks_input)
        
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
        
        title = QLabel("BALANCING SOLUTION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:28px;font-weight:bold;color:#FFFFFF;")
        layout.addWidget(title)
        
        # Metrics section
        metrics_layout = QHBoxLayout()
        
        self.stations_label = QLabel("Stations: -")
        self.stations_label.setStyleSheet("font-size:18px;color:#1E90FF;font-weight:bold;")
        metrics_layout.addWidget(self.stations_label)
        
        metrics_layout.addSpacing(30)
        
        self.cycle_max_label = QLabel("Max Cycle: -")
        self.cycle_max_label.setStyleSheet("font-size:18px;color:#FFD700;font-weight:bold;")
        metrics_layout.addWidget(self.cycle_max_label)
        
        metrics_layout.addSpacing(30)
        
        self.efficiency_label = QLabel("Efficiency: -")
        self.efficiency_label.setStyleSheet("font-size:18px;color:#2cb67d;font-weight:bold;")
        metrics_layout.addWidget(self.efficiency_label)
        
        metrics_layout.addStretch()
        layout.addLayout(metrics_layout)
        
        layout.addSpacing(10)
        
        # Stations scroll area (horizontal)
        scroll_label = QLabel("Workstations (scroll horizontally for more stations):")
        scroll_label.setStyleSheet("font-size:14px;color:#CCCCCC;")
        layout.addWidget(scroll_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #555555;
                background-color: #1E1E1E;
            }
            QScrollBar:horizontal {
                background-color: #2C2C2C;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #1E90FF;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #3AA0FF;
            }
        """)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.stations_container = QWidget()
        self.stations_layout = QHBoxLayout(self.stations_container)
        self.stations_layout.setContentsMargins(10, 10, 10, 10)
        self.stations_layout.setSpacing(20)
        self.stations_layout.addStretch()
        
        scroll.setWidget(self.stations_container)
        layout.addWidget(scroll)
        
        # Details text area
        details_label = QLabel("Detailed Analysis:")
        details_label.setStyleSheet("font-size:14px;color:#CCCCCC;")
        layout.addWidget(details_label)
        
        self.result_display = QPlainTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet(INPUT_STYLE)
        self.result_display.setFixedHeight(150)
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
        
        title = QLabel("📖 ASSEMBLY LINE BALANCING MANUAL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #FFFFFF;")
        scroll_layout.addWidget(title)
        
        instructions = QLabel("""
        Welcome to the Assembly Line Balancing Solver!

        🎯 PROBLEM OVERVIEW:
        Assign tasks to the minimum number of workstations such that:
        - Each task is assigned to exactly one station
        - Total time per station does NOT exceed the maximum cycle time
        - Precedence constraints are respected (if specified)

        📝 INPUT FORMAT:

        Each line defines a task:
            task <name> max <max_duration> avg <avg_duration>
        
        Example:
            task paint max 10 avg 7
            task hammer max 30 avg 27
            task assemble max 50 avg 40
            task inspect max 15 avg 12
            
            max_cycle 60

        📌 FIELDS:
        - name: Task identifier (e.g., paint, hammer)
        - max: Worst-case (maximum) duration
        - avg: Expected (average) duration
        - max_cycle: Maximum allowed time per workstation

        💡 DUAL TIME ANALYSIS:
        The solver optimizes using MAXIMUM durations (worst-case scenario).
        The same assignment is analyzed with AVERAGE durations to show:
        - Real-world efficiency expectations
        - Actual cycle time with expected performance
        - Comparison between pessimistic and optimistic views

        📊 OUTPUT METRICS:
        
        Stations Used: Number of workstations required
        Theoretical Minimum: Lower bound (cannot do better)
        Is Optimal: Whether we achieved the theoretical minimum
        
        Efficiency (max): Real-world efficiency using worst-case times
        Efficiency (avg): Efficiency using expected times
        Balance Delay: Percentage of idle time in the line
        Cycle Time: Maximum time on any single workstation
        
        Station Efficiencies: Load utilization per station
        - > 100%: NOT POSSIBLE (constraint violation)
        - 85-100%: Excellent
        - 70-85%: Good
        - 50-70%: Moderate
        - < 50%: Poor balance

        🔍 HOW IT WORKS:
        1. Parse task definitions and maximum cycle time
        2. Solve MIP (Mixed Integer Program) using Gurobi
        3. Minimize number of stations subject to capacity constraints
        4. Extract and analyze the optimal assignment
        5. Calculate metrics for both max and avg durations
        """)
        instructions.setStyleSheet("font-size: 16px; color: #FFFFFF;")
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
        self.tasks_input.setPlainText(example_data)

    def solve(self):
        input_text = self.tasks_input.toPlainText().strip()
        
        if not input_text:
            QMessageBox.warning(self, "Input Error", "Please enter task configuration.")
            return
        
        try:
            tasks, t_max, t_avg, C_max = parse_task_input(input_text)
        except ValueError as e:
            QMessageBox.warning(self, "Parse Error", str(e))
            return
        
        # Solve
        try:
            result = balance_line(t_max, precedence=None, C_max=C_max, t_avg=t_avg, tasks=tasks)
        except Exception as e:
            QMessageBox.critical(self, "Solver Error", f"Failed to solve: {str(e)}")
            return
        
        if result.get('error'):
            QMessageBox.critical(self, "Solver Error", result['error'])
            return
        
        self.solution = result
        self.tasks = tasks
        self.t_max = t_max
        self.t_avg = t_avg
        self.display_result()
        self.stacked.setCurrentWidget(self.result_page)

    def display_result(self):
        """Display solution with cards and metrics"""
        
        result = self.solution
        
        # Update metrics
        self.stations_label.setText(f"Stations: {result['stations_used']}")
        self.cycle_max_label.setText(f"Max Cycle: {result['actual_max_cycle']:.2f}")
        self.efficiency_label.setText(f"Efficiency (max): {result['efficiency_max']:.1f}%")
        
        # Clear previous cards
        while self.stations_layout.count() > 1:
            item = self.stations_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create station cards
        for station_idx, station_tasks in enumerate(result['assignment']):
            card = self.create_station_card(station_idx, station_tasks, result)
            self.stations_layout.insertWidget(self.stations_layout.count() - 1, card)
        
        # Display detailed analysis
        analysis_text = display_solution(result, self.t_max, self.t_avg)
        self.result_display.setPlainText(analysis_text)

    def create_station_card(self, station_idx, task_indices, result):
        """Create a card widget for a single station"""
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2C2C2C;
                border: 2px solid #1E90FF;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        card.setMinimumWidth(220)
        card.setMaximumWidth(220)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Station header
        header = QLabel(f"Station {station_idx + 1}")
        header.setStyleSheet("font-size:16px;font-weight:bold;color:#1E90FF;")
        layout.addWidget(header)
        
        # Tasks
        tasks_text = QLabel()
        task_names = [self.tasks[i] for i in task_indices]
        task_str = "\n".join(f"• {name}" for name in task_names)
        tasks_text.setText(task_str)
        tasks_text.setStyleSheet("font-size:12px;color:#FFFFFF;margin:5px 0px;")
        tasks_text.setWordWrap(True)
        layout.addWidget(tasks_text)
        
        layout.addSpacing(8)
        
        # Efficiencies
        eff_max = result['station_efficiencies_max'][station_idx]
        eff_avg = result['station_efficiencies_avg'][station_idx]
        
        color_max = get_efficiency_color(eff_max)
        color_avg = get_efficiency_color(eff_avg)
        
        eff_max_label = QLabel(f"Eff (max): {eff_max:.1f}%")
        eff_max_label.setStyleSheet(f"font-size:11px;color:{color_max};font-weight:bold;")
        layout.addWidget(eff_max_label)
        
        eff_avg_label = QLabel(f"Eff (avg): {eff_avg:.1f}%")
        eff_avg_label.setStyleSheet(f"font-size:11px;color:{color_avg};font-weight:bold;")
        layout.addWidget(eff_avg_label)
        
        layout.addStretch()
        
        return card


# ============== Main Entry Point ==============
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    solver = AssemblyLineBalanceSolverGUI()
    solver.show()
    sys.exit(app.exec())
