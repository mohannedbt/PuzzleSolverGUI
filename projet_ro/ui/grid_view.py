from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QRectF, Qt

CELL_SIZE = 40

class GridView(QGraphicsView):

    MODE_NORMAL = 0
    MODE_START = 1
    MODE_END = 2
    MODE_FORBIDDEN = 3
    MODE_DANGEROUS = 4

    def __init__(self, n=10,diagonal=False):
        super().__init__()
        self.n = n
        self.diagonal=diagonal
        self.mode = GridView.MODE_NORMAL

        self.start = None
        self.end = None
        self.forbidden = set()
        self.dangerous = set()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.cells = {}
        self.draw_grid()

    def draw_grid(self):
        self.scene.clear()
        self.cells = {}

        for i in range(self.n):
            for j in range(self.n):
                rect = QGraphicsRectItem(
                    QRectF(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
                rect.setPen(Qt.black)
                rect.setBrush(QBrush(Qt.white))

                rect.setData(0, (i, j))  # store coordinates
                self.scene.addItem(rect)
                self.cells[(i, j)] = rect

    def set_mode(self, mode):
        self.mode = mode

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())
        x = int(pos.y() // CELL_SIZE)
        y = int(pos.x() // CELL_SIZE)

        if not (0 <= x < self.n and 0 <= y < self.n):
            return

        cell = (x, y)

        if self.mode == GridView.MODE_START:
            if self.start:
                self.cells[self.start].setBrush(QBrush(Qt.white))
            self.start = cell
            self.cells[cell].setBrush(QBrush(QColor("green")))

        elif self.mode == GridView.MODE_END:
            if self.end:
                self.cells[self.end].setBrush(QBrush(Qt.white))
            self.end = cell
            self.cells[cell].setBrush(QBrush(QColor("blue")))

        elif self.mode == GridView.MODE_FORBIDDEN:
            self.forbidden.add(cell)
            self.cells[cell].setBrush(QBrush(Qt.black))

        elif self.mode == GridView.MODE_DANGEROUS:
            self.dangerous.add(cell)
            self.cells[cell].setBrush(QBrush(QColor("orange")))

        super().mousePressEvent(event)

    def color_path(self, path_arcs):
        """Colorie les arcs du chemin optimal"""
        for ((i,j),(ni,nj)) in path_arcs:
            self.cells[(i,j)].setBrush(QBrush(QColor(150,255,150)))
            self.cells[(ni,nj)].setBrush(QBrush(QColor(150,255,150)))
