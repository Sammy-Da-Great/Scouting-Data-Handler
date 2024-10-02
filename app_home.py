import sys
from config_maker import read_global_config as config
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QAction
import database

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

    def set_open_table(self, button, target_database):
        button.triggered.connect(lambda: self.open_table(button.text() + ".csv", target_database, button.text()))

    def open_table(self, file_name, database_name, table_name):
        database.get_csv_from_database(file_name, database_name, table_name)

    def create_toolbar_dropdown(self, name, parent):
        self.buffer = QMenu(name, self)
        parent.addMenu(self.buffer)
        return self.buffer

    def create_toolbar_button(self, name, parent, action = ""):
        self.buffer = QAction(name, self)
        parent.addAction(self.buffer)
        if not(action == ""):
            self.buffer.triggered.connect(action)
        return self.buffer
    
    def database_buttons(self, names, parent, action = ""):
        self.list_buffer = []
        for name in names:
            self.buffer = QAction(name, self)
            parent.addAction(self.buffer)
            if not(action == ""):
                self.buffer.triggered.connect(action)
            self.list_buffer.append(self.buffer)
        return self.list_buffer

    def table_buttons(self, target_database, parent, action = ""):
        self.list_buffer = []
        self.names = []
        
        self.names = database.get_all_tables(target_database)
        if not self.names:
            return(list())
    
        for name in self.names:
            self.buffer = self.create_toolbar_button(name, parent)
            self.list_buffer.append(self.buffer)

        self.list_buffer = list(map(lambda mylambda: self.set_open_table(mylambda, target_database), self.list_buffer))

        return self.list_buffer

    def database_dropdowns(self, names, parent, action = ""):
        self.list_buffer = []
        for name in names:
            self.buffer = QMenu(name, self)
            parent.addMenu(self.buffer)
            self.list_buffer.append(self.buffer)
            self.table_buttons(name, self.buffer, action)
        return self.list_buffer

    def _createMenuBar(self):
        menuBar = self.menuBar()

    #File
        file_dropdown = self.create_toolbar_dropdown("&File", menuBar)

        file_dropdown.addSeparator()
        self.exitAction = self.create_toolbar_button("&Exit", file_dropdown, self.close)
    #
        self.create_toolbar_button("&Home", menuBar)
    #Database
        database_names = database.get_all_databases()

        database_dropdown = self.create_toolbar_dropdown("&Database", menuBar)

        view_dropdown = self.create_toolbar_dropdown("&View", database_dropdown)
        self.database_dropdowns(database_names, view_dropdown)
    #
        export_dropdown = self.create_toolbar_dropdown("&Data Export", database_dropdown)
        self.database_dropdowns(database_names, export_dropdown)

        import_dropdown = self.create_toolbar_dropdown("&Data Import", database_dropdown)
        self.database_buttons(database_names, import_dropdown)
        
        self.create_toolbar_button("&Settings", database_dropdown)
    #

def start_app():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()
    #APP CLOSED
    import cleanup
    cleanup.remove_temp_dir()

    

if __name__ == "__main__":
    start_app()