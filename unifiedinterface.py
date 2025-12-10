import sys
from subprocess import Popen
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QColor, QAction

# -------------------------------------------------------------------------
# IMPORTS (Replace these with your actual file paths)
# -------------------------------------------------------------------------
try:
    from graphical_interfaces.sudoku import SudokuSolverGUI
    from graphical_interfaces.Kpiece import KPieceSolverGUI
    from graphical_interfaces.Scheduling import SchedulingSolverGUI
    from graphical_interfaces.AssemblyLineBalance import AssemblyLineBalanceSolverGUI
    # from graphical_interfaces.friend_project import FriendSolverGUI 
except ImportError:
    # Fallbacks for testing if files aren't found
    print("Warning: Solver modules not found. Using placeholders.")
    class Placeholder(QMainWindow):
        def __init__(self, name): super().__init__(); self.setCentralWidget(QLabel(f"{name} Placeholder"))
    SudokuSolverGUI = lambda: Placeholder("Sudoku")
    KPieceSolverGUI = lambda: Placeholder("K-Pieces")
    SchedulingSolverGUI = lambda: Placeholder("Scheduling")
    AssemblyLineBalanceSolverGUI = lambda: Placeholder("Assembly Line Balance")


# -------------------------------------------------------------------------
# STYLING & THEME CONFIGURATION
# -------------------------------------------------------------------------
THEME = {
    "bg_dark": "#1e1e2e",       # Main Window BG
    "bg_lighter": "#2a2a3c",    # Card/Sidebar BG
    "accent": "#7f5af0",        # Main Purple Accent
    "secondary": "#2cb67d",     # Green Accent
    "text_main": "#fffffe",
    "text_dim": "#94a1b2",
    "button_hover": "#36364f"
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {THEME['bg_dark']};
}}

/* Sidebar Styling */
QFrame#Sidebar {{
    background-color: {THEME['bg_lighter']};
    border-right: 1px solid #3f3f55;
}}
QLabel#AppLogo {{
    color: {THEME['accent']};
    font-weight: bold;
    font-size: 24px;
    padding: 20px;
}}
QPushButton.NavButton {{
    background-color: transparent;
    color: {THEME['text_dim']};
    text-align: left;
    padding: 15px 20px;
    border: none;
    font-size: 16px;
    border-left: 4px solid transparent;
}}
QPushButton.NavButton:hover {{
    background-color: {THEME['button_hover']};
    color: {THEME['text_main']};
}}
QPushButton.NavButton:checked {{
    color: {THEME['text_main']};
    border-left: 4px solid {THEME['accent']};
    background-color: {THEME['button_hover']};
}}

/* Dashboard Card Styling */
QFrame.SolverCard {{
    background-color: {THEME['bg_lighter']};
    border-radius: 15px;
    border: 1px solid #3f3f55;
}}
QFrame.SolverCard:hover {{
    border: 1px solid {THEME['accent']};
    background-color: {THEME['button_hover']};
}}
QLabel.CardTitle {{
    color: {THEME['text_main']};
    font-size: 20px;
    font-weight: bold;
}}
QLabel.CardDesc {{
    color: {THEME['text_dim']};
    font-size: 14px;
}}
QPushButton.CardButton {{
    background-color: {THEME['accent']};
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}}
QPushButton.CardButton:hover {{
    background-color: #6a48c9;
}}
"""

# -------------------------------------------------------------------------
# CUSTOM WIDGET: DASHBOARD CARD
# -------------------------------------------------------------------------
class SolverCard(QFrame):
    """A graphical card representing a specific solver on the dashboard."""
    def __init__(self, title, description, icon_text, launch_callback):
        super().__init__()
        self.setProperty("class", "SolverCard")
        self.setFixedSize(280, 200)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Icon / Header
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Title
        title_lbl = QLabel(title)
        title_lbl.setProperty("class", "CardTitle")
        layout.addWidget(title_lbl)
        
        # Description
        desc_lbl = QLabel(description)
        desc_lbl.setProperty("class", "CardDesc")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
        
        layout.addStretch()
        
        # Launch Button
        self.btn = QPushButton("Launch Tool")
        self.btn.setProperty("class", "CardButton")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(launch_callback)
        layout.addWidget(self.btn)

# -------------------------------------------------------------------------
# MAIN APPLICATION
# -------------------------------------------------------------------------
class OptiSuiteHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiSuite | Integrated PL Solver Hub")
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)

        # Data structure to hold registered solvers
        # Format: { id: { 'title': str, 'widget': QWidget, 'btn': QPushButton } }
        self.solvers = {} 

        self._setup_ui()
        self._load_solvers()
        
        # Select Dashboard by default
        self.nav_btns_group.buttons()[0].setChecked(True)

    def _setup_ui(self):
        """Builds the 2-column layout (Sidebar + Main Content)"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- LEFT SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 20)
        
        # Logo
        logo = QLabel("⚡ OptiSuite")
        logo.setObjectName("AppLogo")
        sidebar_layout.addWidget(logo)
        
        # Navigation Buttons Container
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setSpacing(5)
        self.nav_btns_group = QButtonGroup(self)
        self.nav_btns_group.setExclusive(True)
        
        # Dashboard Button (Always first)
        self.dashboard_btn = self._create_nav_button("Dashboard", "🏠", 0)
        self.nav_layout.addWidget(self.dashboard_btn)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3f3f55; margin: 10px 20px;")
        self.nav_layout.addWidget(line)

        sidebar_layout.addLayout(self.nav_layout)
        sidebar_layout.addStretch()
        
        # Footer
        version = QLabel("v2.0.1 Stable")
        version.setStyleSheet(f"color: {THEME['text_dim']}; padding-left: 20px;")
        sidebar_layout.addWidget(version)

        # --- RIGHT CONTENT AREA ---
        self.stack = QStackedWidget()
        
        # Page 0: Dashboard (Grid of Cards)
        self.dashboard_page = QWidget()
        self.dashboard_grid = QGridLayout(self.dashboard_page)
        self.dashboard_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.dashboard_grid.setSpacing(20)
        self.dashboard_grid.setContentsMargins(40, 40, 40, 40)
        
        # Header for dashboard
        dash_header = QLabel("Available Solvers")
        dash_header.setStyleSheet(f"color: white; font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        self.dashboard_grid.addWidget(dash_header, 0, 0, 1, 3)

        self.stack.addWidget(self.dashboard_page)

        # Add Layouts to Main
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

    def _create_nav_button(self, text, icon, index):
        """Helper to create consistent sidebar buttons"""
        btn = QPushButton(f"  {icon}   {text}")
        btn.setProperty("class", "NavButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # We use a lambda to force the index capture
        btn.clicked.connect(lambda: self.switch_view(index))
        self.nav_btns_group.addButton(btn)
        return btn

    def register_solver(self, name, description, icon, widget_instance):
        """
        DYNAMICALY ADDS A SOLVER TO THE INTERFACE.
        1. Adds a page to the Stack.
        2. Adds a button to the Sidebar.
        3. Adds a Card to the Dashboard.
        """
        # Get the central widget if it's a QMainWindow, otherwise use as is
        if isinstance(widget_instance, QMainWindow):
            content_widget = widget_instance.centralWidget()
            # If the QMainWindow didn't have a central widget set properly, create a wrapper
            if content_widget is None:
                content_widget = widget_instance
        else:
            content_widget = widget_instance

        # Add to Stack
        index = self.stack.addWidget(content_widget)
        
        # Add to Sidebar
        nav_btn = self._create_nav_button(name, icon, index)
        self.nav_layout.addWidget(nav_btn)
        
        # Add Card to Dashboard
        row = (index + 1) // 3 + 1 # Simple grid logic
        col = (index + 1) % 3
        
        card = SolverCard(
            title=name,
            description=description,
            icon_text=icon,
            launch_callback=lambda: self.switch_view(index)
        )
        self.dashboard_grid.addWidget(card, row, col)
    def add_external_app(self, name, description, icon, script_path):
        """Ajoute une carte + bouton qui lance une app externe PyQt6/Python."""
        
        # --- Bouton dans la Sidebar ---
        btn = self._create_nav_button(name, icon, -1)
        btn.clicked.connect(lambda: Popen([sys.executable, script_path]))
        self.nav_layout.addWidget(btn)

        # --- Carte Dashboard ---
        row = (self.stack.count()) // 3 + 1
        col = (self.stack.count() + 1) % 3

        card = SolverCard(
            title=name,
            description=description,
            icon_text=icon,
            launch_callback=lambda: Popen([sys.executable, script_path])
        )

        self.dashboard_grid.addWidget(card, row, col)

    def add_external_app1(self, name, description, icon, script_path):
        """Ajoute une carte + bouton qui lance une app externe PyQt6/Python."""
        
        # --- Bouton dans la Sidebar ---
        btn = self._create_nav_button(name, icon, -1)
        btn.clicked.connect(lambda: Popen([sys.executable, script_path]))
        self.nav_layout.addWidget(btn)

        # --- Carte Dashboard ---
        row = (self.stack.count() + 1) // 3 + 1
        col = (self.stack.count() + 1) % 3+2

        card = SolverCard(
            title=name,
            description=description,
            icon_text=icon,
            launch_callback=lambda: Popen([sys.executable, script_path])
        )

        self.dashboard_grid.addWidget(card, row, col)

    def switch_view(self, index):
        """Switches the right-hand view and updates sidebar state"""
        self.stack.setCurrentIndex(index)
        
        # Sync sidebar button state manually if triggered from Dashboard Card
        # (Because QButtonGroup handles it if clicked directly, but not if done via code)
        for btn in self.nav_btns_group.buttons():
            # Logic depends on how you store button indices, simplest is finding the one connected to this index
            pass 
            
        # Optional: Add animation here if desired

    def _load_solvers(self):
        """
        HERE IS WHERE YOU INTEGRATE NEW INTERFACES
        """
        
        # 1. Sudoku
        # self.register_solver(
        #     name="Sudoku Master",
        #     description="Constraint Satisfaction Problem solver optimized for 9x9 grids.",
        #     icon="🧩",
        #     widget_instance=SudokuSolverGUI()
        # )

        # 2. K-Pieces
        self.register_solver(
            name="K-Pieces Solver",
            description="Linear optimization for placing K chess pieces without attacks.",
            icon="♟️",
            widget_instance=KPieceSolverGUI()
        )
        self.add_external_app(
            name="Capital Budgeting",
            description="Optimisation & sélection des projets d'investissement",
            icon="💼",
            script_path="project_capital_budgeting/main.py"  
        )
        self.add_external_app1(
            name="Path Plannig",
            description="Planification d'une trajectoire minimisant la distance et le risque (évitant certaines zones).",
            icon="🤖",
            script_path="projet_ro/main.py" 
        )
        self.register_solver(
            name="Scheduling Solver",
            description="Graph coloring MIP for exam scheduling without conflicts.",
            icon="📅",
            widget_instance=SchedulingSolverGUI()
        )

        # 3. Assembly Line Balancing
        self.register_solver(
            name="Assembly Line Balancing",
            description="Minimize workstations while respecting cycle time with dual time analysis.",
            icon="⚙️",
            widget_instance=AssemblyLineBalanceSolverGUI()
        )
        # ---------------------------------------------------------
        # HOW TO ADD YOUR FRIEND'S INTERFACE:
        # ---------------------------------------------------------
        # 3. Friend's Solver
        # self.register_solver(
        #     name="Graph Coloring", 
        #     description="Heuristic approach to the N-coloring map problem.",
        #     icon="🎨",
        #     widget_instance=FriendSolverGUI()
        # )
        
        # 4. Another Solver
        # self.register_solver(
        #     name="Knapsack Optimizer", 
        #     description="Dynamic programming solution for resource allocation.",
        #     icon="🎒",
        #     widget_instance=KnapsackGUI()
        # )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Optional: Set global app font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = OptiSuiteHub()
    window.show()
    sys.exit(app.exec())