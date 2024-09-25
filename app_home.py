import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Python Menus & Toolbars")
        self.resize(1000, 500)
        self._createMenuBar()

        self.centralWidget = QLabel("Hello, World")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)

    def create_toolbar_button(self, name, menu, action = ""):
        self.buffer = QAction(name, self)
        menu.addAction(self.buffer)
        if not(action == ""):
            self.buffer.triggered.connect(action)
        return self.buffer

    def create_toolbar_dropdown(self, name, bar):
        self.buffer = QMenu(name, self)
        bar.addMenu(self.buffer)
        return self.buffer

    def _createMenuBar(self):
        menuBar = self.menuBar()

    #Navigation
        nav_dropdown = self.create_toolbar_dropdown("&Menu", menuBar)

        self.homeAction = self.create_toolbar_button("&Home", nav_dropdown)
        self.exitAction = self.create_toolbar_button("&Exit", nav_dropdown, self.close)
    #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())