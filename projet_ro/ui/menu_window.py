from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from ui.main_window import MainWindow

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Choisissez le mode")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("<h2>Sélection du Mode de Grille</h2>")
        layout.addWidget(title)

        # Bouton sans diagonales
        btn_no_diag = QPushButton("Grille : mouvements sans diagonales")
        btn_no_diag.clicked.connect(lambda: self.start_main(diagonal_flag=False))
        layout.addWidget(btn_no_diag)

        # Bouton avec diagonales
        btn_diag = QPushButton("Grille : mouvements avec diagonales")
        btn_diag.clicked.connect(lambda: self.start_main(diagonal_flag=True))
        layout.addWidget(btn_diag)

        #Graph stuff
        btn_graph = QPushButton("Graphe : édition libre (noeuds + arcs)")
        btn_graph.clicked.connect(self.start_graph_mode)
        layout.addWidget(btn_graph)


    def start_main(self, diagonal_flag):
        self.main = MainWindow(diagonal=diagonal_flag)
        self.main.show()
        self.close()

    def start_graph_mode(self):
        from ui.graph_window import GraphWindow
        self.graph_ui = GraphWindow()
        self.graph_ui.show()
        self.close()

