import sys
from PyQt5.QtWidgets import QApplication
from ui.menu_window import MenuWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MenuWindow()
    window.show()

    sys.exit(app.exec_())
