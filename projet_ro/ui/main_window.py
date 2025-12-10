from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

from ui.grid_view import GridView
from core.grid_builder import build_grid_graph
from core.solver import solve_shortest_path_with_risk


class MainWindow(QWidget):
    def __init__(self, diagonal=False):
        super().__init__()
        self.diagonal = diagonal

        if self.diagonal:
            self.setWindowTitle("Minimisation de distance dans une grille (avec diagonales)")
        else:
            self.setWindowTitle("Minimisation de distance dans une grille (sans diagonales)")

        self.setFixedSize(1100, 700)

        self.grid = None  # sera rempli après création de la grille

        # --- Layout principal ---
        layout = QHBoxLayout()
        self.setLayout(layout)

        # ---------------------------------------------------------
        # 1) PANNEAU GAUCHE : GRILLE
        # ---------------------------------------------------------
        self.grid = GridView(n=10)
        layout.addWidget(self.grid, stretch=3)

        # ---------------------------------------------------------
        # 2) PANNEAU DROIT : CONTROLS
        # ---------------------------------------------------------
        control_panel = QVBoxLayout()
        layout.addLayout(control_panel, stretch=1)

        # Titre
        if self.diagonal:
            title = QLabel("<h2>Contrôle (avec diagonales)</h2>")
        else:
            title = QLabel("<h2>Contrôle (sans diagonales)</h2>")

        control_panel.addWidget(title)

        # --- Taille de la grille ---
        grid_label = QLabel("Taille de grille (n x n) :")
        control_panel.addWidget(grid_label)

        self.n_box = QSpinBox()
        self.n_box.setRange(3, 40)
        self.n_box.setValue(10)
        control_panel.addWidget(self.n_box)

        btn_rebuild = QPushButton("Reconstruire Grille")
        btn_rebuild.clicked.connect(self.rebuild_grid)
        control_panel.addWidget(btn_rebuild)

        control_panel.addSpacing(20)

        # --- R_max ---
        risk_label = QLabel("Risque maximum (R_max) :")
        control_panel.addWidget(risk_label)

        self.rmax_box = QDoubleSpinBox()
        self.rmax_box.setRange(0, 1000)
        self.rmax_box.setSingleStep(0.5)
        self.rmax_box.setValue(4.0)
        control_panel.addWidget(self.rmax_box)

        control_panel.addSpacing(20)

        # --- Boutons de mode ---
        control_panel.addWidget(QLabel("<b>Mode d'annotation :</b>"))

        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(lambda: self.grid.set_mode(GridView.MODE_START))
        control_panel.addWidget(self.btn_start)

        self.btn_end = QPushButton("End")
        self.btn_end.clicked.connect(lambda: self.grid.set_mode(GridView.MODE_END))
        control_panel.addWidget(self.btn_end)

        self.btn_forbidden = QPushButton("Forbidden")
        self.btn_forbidden.clicked.connect(lambda: self.grid.set_mode(GridView.MODE_FORBIDDEN))
        control_panel.addWidget(self.btn_forbidden)

        self.btn_dangerous = QPushButton("Dangerous")
        self.btn_dangerous.clicked.connect(lambda: self.grid.set_mode(GridView.MODE_DANGEROUS))
        control_panel.addWidget(self.btn_dangerous)

        control_panel.addSpacing(30)

        # --- Solve button ---
        solve_btn = QPushButton("Résoudre")
        solve_btn.clicked.connect(self.solve)
        control_panel.addWidget(solve_btn)

        # --- Résultats ---
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignTop)
        control_panel.addWidget(self.result_label)

        btn_return = QPushButton("Retour au Menu")
        btn_return.clicked.connect(self.return_to_menu)
        control_panel.addWidget(btn_return)


        control_panel.addStretch()

    # ===============================================================
    # 1) Reconstruire la grille selon la nouvelle taille n
    # ===============================================================
    def rebuild_grid(self):
        n = self.n_box.value()
        self.grid.setParent(None)
        self.grid = GridView(n=n, diagonal=self.diagonal)
        self.layout().insertWidget(0, self.grid, stretch=3)
        self.result_label.setText("")

    # ===============================================================
    # 2) Bouton "Solve"
    # ===============================================================
    def solve(self):
        # Vérification start/end
        if self.grid.start is None or self.grid.end is None:
            self.result_label.setText("<font color='red'>Start ou End non défini.</font>")
            return

        n = self.n_box.value()
        R_max = self.rmax_box.value()

        # Construire le graphe (dist et risk sont générés ici)
        nodes, arcs, dist, risk = build_grid_graph(
            n,
            dangerous_cells=self.grid.dangerous,
            forbidden_cells=self.grid.forbidden,
            diagonal=self.diagonal
        )


        # Résoudre
        status, total_dist, total_risk, path_arcs = solve_shortest_path_with_risk(
            nodes, arcs, dist, risk,
            start=self.grid.start,
            end=self.grid.end,
            R_max=R_max
        )

        print("Status =", status)
        print("Path arcs:", path_arcs)
        print("Forbidden =", self.grid.forbidden)
        print("Dangerous =", self.grid.dangerous)
        print("Start =", self.grid.start)
        print("End =", self.grid.end)


        # Afficher résultats
        if status.upper() == "OPTIMAL":
            self.result_label.setText(
                f"<b>Solution optimale trouvée :</b><br>"
                f"Distance = {total_dist:.2f}<br>"
                f"Risque = {total_risk:.2f}"
            )
            self.grid.color_path(path_arcs)
        else:
            self.result_label.setText(
                "<font color='red'>Aucune solution trouvée (Infeasible).</font>"
            )
    def return_to_menu(self):
        from ui.menu_window import MenuWindow
        self.menu = MenuWindow()
        self.menu.show()
        self.close()